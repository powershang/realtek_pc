#!/usr/bin/env python3
"""
Register Address Value Comparer
比較兩個 register dump 檔案的差異

特殊處理: c2100~c2140 區間
- 當 c2100[31]=1 時記錄 snapshot
- 比較每次 trigger 時的值

支援從 regif.v 讀取 register name mapping

Contact: shane_wu #25696
Version: 1.0.0
"""

__author__ = "shane_wu #25696"
__version__ = "1.0.0"

import re
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field


def safe_hex_to_int(value: str, default: int = 0) -> Optional[int]:
    """
    安全地將 hex 字串轉換為整數
    處理 "N/A"、None 和無效值的情況
    """
    if not value or value.upper() == "N/A":
        return None
    try:
        return int(value, 16)
    except ValueError:
        return None


# =============================================================================
# USER CONFIGURATION - 使用者可修改此區域
# =============================================================================

# 比較檔案設定
FILE1 = "SW_SDP.tbl"          # 第一個比較檔案
FILE2 = "SW_DDP.tbl"          # 第二個比較檔案

# Register 定義檔 (用於顯示 field name)
REGFILE = "dc_mc1_regfile.v"    # Verilog register file

# =============================================================================
# END OF USER CONFIGURATION
# =============================================================================


# 需要特殊處理的 register 範圍 (每個 channel)
# 支援兩種地址格式: 0xb80cXXXX 和 0x180cXXXX
SPECIAL_RANGES = [
    (0xb80c2100, 0xb80c2140),  # Channel 0 (full address)
    (0xb80c3100, 0xb80c3140),  # Channel 1
    (0xb80c4100, 0xb80c4140),  # Channel 2
    (0xb80c5100, 0xb80c5140),  # Channel 3
    (0x180c2100, 0x180c2140),  # Channel 0 (short address)
    (0x180c3100, 0x180c3140),  # Channel 1
    (0x180c4100, 0x180c4140),  # Channel 2
    (0x180c5100, 0x180c5140),  # Channel 3
]

# Channel base addresses (用於 mapping)
# 支援兩種地址格式: 0xb80cXXXX 和 0x180cXXXX
CHANNEL_BASES = {
    0xb80c2000: 0,  # Channel 0 (full address)
    0xb80c3000: 1,  # Channel 1
    0xb80c4000: 2,  # Channel 2
    0xb80c5000: 3,  # Channel 3
    0x180c2000: 0,  # Channel 0 (short address)
    0x180c3000: 1,  # Channel 1
    0x180c4000: 2,  # Channel 2
    0x180c5000: 3,  # Channel 3
}

# LPDDR4 CMD TRUTH TABLE (BIT31:BIT28)
# 用於解析 0x2110~0x2120 區間的 CMD
LPDDR4_CMD_TABLE = {
    0xF: "MPC / CAS-2",
    0x0: "SRE",
    0x1: "SRX",
    0x2: "Precharge (per bank)",
    0x3: "Precharge (all)",
    0x6: "MRW-1 / MRW-2",
    0x7: "MRR-1 / CAS-2",
    0xA: "PDE / CKE low",
    0xB: "PDX / CKE high",
    0xE: "RFU",
}

# CMD 解析的地址範圍 (相對於 channel base 的 offset)
CMD_ADDR_OFFSETS = [0x110, 0x114, 0x118, 0x11c, 0x120]


def normalize_address(addr: str) -> str:
    """
    將 0x180... 開頭的地址正規化為 0xb80... 格式
    例如: 0x180c52ac -> 0xb80c52ac
    """
    addr_lower = addr.lower()
    # 檢查是否為 0x180 開頭
    if addr_lower.startswith('0x180'):
        # 將 0x180 替換為 0xb80
        return '0xb80' + addr_lower[5:]
    return addr_lower


def decode_lpddr4_cmd(value: int) -> str:
    """
    從 register value 的 BIT31:BIT28 解析 LPDDR4 CMD

    Args:
        value: register 的完整 32-bit 值

    Returns:
        CMD 名稱字串，如果無法識別則回傳 "Unknown"
    """
    cmd_bits = (value >> 28) & 0xF
    return LPDDR4_CMD_TABLE.get(cmd_bits, f"Unknown (0x{cmd_bits:X})")


def is_mrw_cmd(value: int) -> bool:
    """檢查是否為 MRW (Mode Register Write) 命令"""
    cmd_bits = (value >> 28) & 0xF
    return cmd_bits == 0x6  # MRW-1 / MRW-2


def decode_mrw(value: int) -> Tuple[int, int]:
    """
    解析 MRW 命令，取得 Mode Register 編號和值

    Args:
        value: register 的完整 32-bit 值

    Returns:
        (mr_number, mr_value): MR 編號 (BIT13:8) 和值 (BIT7:0)
    """
    mr_number = (value >> 8) & 0x3F  # BIT13:BIT8 (6 bits)
    mr_value = value & 0xFF          # BIT7:BIT0 (8 bits)
    return mr_number, mr_value


def decode_mrw_rank(value: int) -> Tuple[bool, bool]:
    """
    解析 MRW 命令的 rank 目標

    bit27 = 1: 對 rank1 下 MR
    bit26 = 1: 對 rank0 下 MR
    bit27 = 1 且 bit26 = 1: 同時更新 rank0 和 rank1

    Args:
        value: register 的完整 32-bit 值

    Returns:
        (rank0_enable, rank1_enable): 是否對 rank0/rank1 有效
    """
    rank1_enable = bool((value >> 27) & 0x1)  # bit27
    rank0_enable = bool((value >> 26) & 0x1)  # bit26
    return rank0_enable, rank1_enable


def _format_rank_target(rank0_enable: bool, rank1_enable: bool) -> str:
    """
    格式化 rank 目標字串

    Args:
        rank0_enable: 是否對 rank0 有效
        rank1_enable: 是否對 rank1 有效

    Returns:
        格式化的字串，例如 "[R0]", "[R1]", "[R0,R1]", 或 ""
    """
    if rank0_enable and rank1_enable:
        return "[R0,R1]"
    elif rank0_enable:
        return "[R0]"
    elif rank1_enable:
        return "[R1]"
    else:
        return ""


def extract_mr_values(registers: Dict[str, str], ddr_type: str = "LPDDR4") -> Dict[str, Dict[int, int]]:
    """
    從 snapshot registers 中提取所有 MR 值，按 rank 分類

    Args:
        registers: snapshot 中的 register 資料 {addr: value}
        ddr_type: DDR 類型

    Returns:
        {
            'rank0': {mr_number: mr_value},
            'rank1': {mr_number: mr_value}
        }
        按 rank 分類的最後一次寫入 MR 值
    """
    if ddr_type != "LPDDR4":
        return {'rank0': {}, 'rank1': {}}

    mr_values = {'rank0': {}, 'rank1': {}}
    for addr, value_str in registers.items():
        addr_int = int(addr, 16)
        if is_cmd_addr(addr_int):
            value_int = int(value_str, 16)
            if is_mrw_cmd(value_int):
                mr_num, mr_val = decode_mrw(value_int)
                rank0_en, rank1_en = decode_mrw_rank(value_int)
                # 根據 rank enable 位元決定寫入哪個 rank
                if rank0_en:
                    mr_values['rank0'][mr_num] = mr_val
                if rank1_en:
                    mr_values['rank1'][mr_num] = mr_val

    return mr_values


def extract_all_mr_values(snapshots: Dict[int, List], ddr_type: str = "LPDDR4") -> Dict[str, Dict[int, int]]:
    """
    從所有 channel 的所有 snapshots 中提取最終的 MR 值，按 rank 分類

    Args:
        snapshots: {range_start: [TriggerSnapshot, ...]}
        ddr_type: DDR 類型

    Returns:
        {
            'rank0': {mr_number: mr_value},
            'rank1': {mr_number: mr_value}
        }
        按 rank 分類，所有 snapshot 中最後一次寫入的 MR 值
    """
    if ddr_type != "LPDDR4":
        return {'rank0': {}, 'rank1': {}}

    mr_values = {'rank0': {}, 'rank1': {}}
    # 遍歷所有 channel 的所有 snapshot
    for range_start, snap_list in snapshots.items():
        for snap in snap_list:
            for addr, value_str in snap.registers.items():
                addr_int = int(addr, 16)
                if is_cmd_addr(addr_int):
                    value_int = int(value_str, 16)
                    if is_mrw_cmd(value_int):
                        mr_num, mr_val = decode_mrw(value_int)
                        rank0_en, rank1_en = decode_mrw_rank(value_int)
                        if rank0_en:
                            mr_values['rank0'][mr_num] = mr_val
                        if rank1_en:
                            mr_values['rank1'][mr_num] = mr_val

    return mr_values


def _compare_single_rank_mr(mr1: Dict[int, int], mr2: Dict[int, int]) -> dict:
    """
    比較單一 rank 的 MR 值

    Args:
        mr1: 檔案1 的 {mr_number: mr_value}
        mr2: 檔案2 的 {mr_number: mr_value}

    Returns:
        {
            'only_in_file1': [(mr_num, value), ...],
            'only_in_file2': [(mr_num, value), ...],
            'value_diff': [(mr_num, val1, val2), ...],
            'same': [(mr_num, value), ...]
        }
    """
    all_mr_nums = sorted(set(mr1.keys()) | set(mr2.keys()))

    result = {
        'only_in_file1': [],
        'only_in_file2': [],
        'value_diff': [],
        'same': []
    }

    for mr_num in all_mr_nums:
        in_file1 = mr_num in mr1
        in_file2 = mr_num in mr2

        if in_file1 and not in_file2:
            result['only_in_file1'].append((mr_num, mr1[mr_num]))
        elif in_file2 and not in_file1:
            result['only_in_file2'].append((mr_num, mr2[mr_num]))
        else:
            if mr1[mr_num] != mr2[mr_num]:
                result['value_diff'].append((mr_num, mr1[mr_num], mr2[mr_num]))
            else:
                result['same'].append((mr_num, mr1[mr_num]))

    return result


def compare_mr_values(mr1: Dict[str, Dict[int, int]], mr2: Dict[str, Dict[int, int]]) -> dict:
    """
    比較兩個檔案的 MR 值，按 rank 獨立比較

    Args:
        mr1: 檔案1 的 {'rank0': {...}, 'rank1': {...}}
        mr2: 檔案2 的 {'rank0': {...}, 'rank1': {...}}

    Returns:
        {
            'rank0': {
                'only_in_file1': [(mr_num, value), ...],
                'only_in_file2': [(mr_num, value), ...],
                'value_diff': [(mr_num, val1, val2), ...],
                'same': [(mr_num, value), ...]
            },
            'rank1': { ... }
        }
    """
    return {
        'rank0': _compare_single_rank_mr(mr1.get('rank0', {}), mr2.get('rank0', {})),
        'rank1': _compare_single_rank_mr(mr1.get('rank1', {}), mr2.get('rank1', {}))
    }


def _format_single_rank_mr_report(rank_diff: dict, rank_name: str,
                                   mr1_values: Dict[int, int],
                                   mr2_values: Dict[int, int]) -> List[str]:
    """
    格式化單一 rank 的 MR 比較報告

    Args:
        rank_diff: 差異資料
        rank_name: Rank 名稱 (顯示用)
        mr1_values: File1 該 rank 的所有 MR 值 {mr_num: value}
        mr2_values: File2 該 rank 的所有 MR 值 {mr_num: value}
    """
    lines = []
    lines.append(f"\n[{rank_name}]")
    lines.append("-" * 60)

    if rank_diff['value_diff']:
        lines.append(f"  VALUE DIFFERENCES ({len(rank_diff['value_diff'])} registers):")
        for mr_num, val1, val2 in rank_diff['value_diff']:
            lines.append(f"    MR{mr_num:<3}: File1=0x{val1:02X}  File2=0x{val2:02X}  <-- DIFF")
    else:
        lines.append("  VALUE DIFFERENCES: None")

    if rank_diff['only_in_file1']:
        lines.append(f"  ONLY IN FILE1 ({len(rank_diff['only_in_file1'])} registers):")
        for mr_num, val in rank_diff['only_in_file1']:
            lines.append(f"    MR{mr_num:<3}: 0x{val:02X}")

    if rank_diff['only_in_file2']:
        lines.append(f"  ONLY IN FILE2 ({len(rank_diff['only_in_file2'])} registers):")
        for mr_num, val in rank_diff['only_in_file2']:
            lines.append(f"    MR{mr_num:<3}: 0x{val:02X}")

    # Summary for this rank
    lines.append(f"  Summary: Diff={len(rank_diff['value_diff'])}, "
                f"OnlyFile1={len(rank_diff['only_in_file1'])}, "
                f"OnlyFile2={len(rank_diff['only_in_file2'])}, "
                f"Same={len(rank_diff['same'])}")

    # ALL MR VALUES (Info)
    lines.append("")
    lines.append(f"  ALL MR VALUES (Info):")

    # 合併所有 MR 編號並排序
    all_mr_nums = sorted(set(mr1_values.keys()) | set(mr2_values.keys()))

    if all_mr_nums:
        lines.append(f"    {'MR#':<6} {'File1':<12} {'File2':<12}")
        lines.append(f"    {'-'*6} {'-'*12} {'-'*12}")
        for mr_num in all_mr_nums:
            val1_str = f"0x{mr1_values[mr_num]:02X}" if mr_num in mr1_values else "-"
            val2_str = f"0x{mr2_values[mr_num]:02X}" if mr_num in mr2_values else "-"
            # 標記差異
            diff_mark = ""
            if mr_num in mr1_values and mr_num in mr2_values:
                if mr1_values[mr_num] != mr2_values[mr_num]:
                    diff_mark = " *"
            elif mr_num in mr1_values or mr_num in mr2_values:
                diff_mark = " *"
            lines.append(f"    MR{mr_num:<3}  {val1_str:<12} {val2_str:<12}{diff_mark}")
    else:
        lines.append("    (No MR values found)")

    return lines


def format_mr_report(mr_diff: dict, file1_name: str, file2_name: str,
                     mr1: Dict[str, Dict[int, int]] = None,
                     mr2: Dict[str, Dict[int, int]] = None) -> str:
    """
    格式化 MR 比較報告，按 rank 獨立顯示

    Args:
        mr_diff: {
            'rank0': {'value_diff': [...], 'only_in_file1': [...], ...},
            'rank1': {'value_diff': [...], 'only_in_file1': [...], ...}
        }
        mr1: File1 的 MR 值 {'rank0': {...}, 'rank1': {...}}
        mr2: File2 的 MR 值 {'rank0': {...}, 'rank1': {...}}
    """
    # 預設空值
    if mr1 is None:
        mr1 = {'rank0': {}, 'rank1': {}}
    if mr2 is None:
        mr2 = {'rank0': {}, 'rank1': {}}

    lines = []
    lines.append("\n" + "=" * 80)
    lines.append("MODE REGISTER (MR) COMPARISON (Per Rank)")
    lines.append("=" * 80)
    lines.append(f"File 1: {file1_name}")
    lines.append(f"File 2: {file2_name}")
    lines.append("-" * 80)
    lines.append("Note: bit27=1 -> Rank1, bit26=1 -> Rank0")
    lines.append("      bit27=1 & bit26=1 -> Both Rank0 and Rank1")
    lines.append("      * = value differs between files")

    # Rank0 報告
    rank0_diff = mr_diff.get('rank0', {'value_diff': [], 'only_in_file1': [], 'only_in_file2': [], 'same': []})
    lines.extend(_format_single_rank_mr_report(
        rank0_diff, "RANK0 (bit26=1)",
        mr1.get('rank0', {}), mr2.get('rank0', {})
    ))

    # Rank1 報告
    rank1_diff = mr_diff.get('rank1', {'value_diff': [], 'only_in_file1': [], 'only_in_file2': [], 'same': []})
    lines.extend(_format_single_rank_mr_report(
        rank1_diff, "RANK1 (bit27=1)",
        mr1.get('rank1', {}), mr2.get('rank1', {})
    ))

    # Overall Summary
    lines.append("\n" + "-" * 40)
    lines.append("OVERALL MR SUMMARY:")
    total_diff = len(rank0_diff['value_diff']) + len(rank1_diff['value_diff'])
    total_only1 = len(rank0_diff['only_in_file1']) + len(rank1_diff['only_in_file1'])
    total_only2 = len(rank0_diff['only_in_file2']) + len(rank1_diff['only_in_file2'])
    total_same = len(rank0_diff['same']) + len(rank1_diff['same'])
    lines.append(f"  Rank0 - Different: {len(rank0_diff['value_diff'])}, Same: {len(rank0_diff['same'])}")
    lines.append(f"  Rank1 - Different: {len(rank1_diff['value_diff'])}, Same: {len(rank1_diff['same'])}")
    lines.append(f"  Total - Different: {total_diff}, Only in File1: {total_only1}, "
                f"Only in File2: {total_only2}, Same: {total_same}")
    lines.append("=" * 80)

    return "\n".join(lines)


def is_cmd_addr(addr_int: int) -> bool:
    """檢查地址是否在 CMD 解析範圍 (0x2110~0x2120)"""
    for base in CHANNEL_BASES.keys():
        if base <= addr_int < base + 0x1000:
            offset = addr_int - base
            if offset in CMD_ADDR_OFFSETS:
                return True
    return False


def get_addr_offset(addr_int: int) -> Optional[int]:
    """取得地址相對於 channel base 的 offset"""
    for base in CHANNEL_BASES.keys():
        if base <= addr_int < base + 0x1000:
            return addr_int - base
    return None


@dataclass
class BitField:
    """Register bit field 定義"""
    name: str
    high_bit: int
    low_bit: int

    def __str__(self):
        if self.high_bit == self.low_bit:
            return f"{self.name}[{self.high_bit}]"
        else:
            return f"{self.name}[{self.high_bit}:{self.low_bit}]"


@dataclass
class RegisterInfo:
    """Register 資訊"""
    offset: int  # 相對於 channel base 的 offset (e.g., 0x100)
    fields: List[BitField] = field(default_factory=list)

    def get_field_value(self, value: int, field_name: str) -> Optional[int]:
        """取得特定 field 的值"""
        for f in self.fields:
            if f.name == field_name:
                mask = (1 << (f.high_bit - f.low_bit + 1)) - 1
                return (value >> f.low_bit) & mask
        return None


@dataclass
class RegisterOp:
    """單一 register 操作"""
    line_num: int
    op_type: str  # 'outl' or 'inl'
    address: str
    value: str


@dataclass
class TriggerSnapshot:
    """當 trigger 發生時的 snapshot"""
    trigger_line: int
    trigger_value: str
    registers: Dict[str, str] = field(default_factory=dict)


def parse_regfile_v(filepath: str) -> Dict[int, RegisterInfo]:
    """
    解析 regif.v 檔案，提取 register 定義

    返回: {offset: RegisterInfo}
    offset 是相對於 channel base 的偏移 (e.g., 0x2100 -> 0x100)
    """
    registers = {}

    # 匹配 assign signal = reg180cXXXX[high:low] 或 reg180cXXXX[bit]
    pattern = re.compile(
        r'assign\s+(\w+)\s*=\s*reg180c([0-9a-fA-F]{4})\[(\d+)(?::(\d+))?\]'
    )

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            match = pattern.search(line)
            if match:
                signal_name = match.group(1)
                reg_offset = int(match.group(2), 16)
                high_bit = int(match.group(3))
                low_bit = int(match.group(4)) if match.group(4) else high_bit

                if reg_offset not in registers:
                    registers[reg_offset] = RegisterInfo(offset=reg_offset)

                registers[reg_offset].fields.append(
                    BitField(name=signal_name, high_bit=high_bit, low_bit=low_bit)
                )

    # 對每個 register 的 fields 按 bit 位置排序 (高位在前)
    for reg in registers.values():
        reg.fields.sort(key=lambda f: f.high_bit, reverse=True)

    return registers


def get_register_offset(addr_int: int) -> Optional[int]:
    """從完整地址取得 register offset (用於查詢 reg_map)"""
    # reg_map 的 key 格式是 0x2XXX (從 reg180c2XXX 解析出來的)
    # 所以 0xb80c2100 對應到 0x2100, 0xb80c3100 對應到 0x2100 (channel 通用)
    for base in CHANNEL_BASES.keys():
        if base <= addr_int < base + 0x1000:
            # 將 channel 地址轉換為 channel 0 的 offset
            # 例如: 0xb80c3100 -> 0x2100
            relative_offset = addr_int - base  # 得到 0x100
            return 0x2000 + relative_offset    # 轉成 0x2100
    return None


def format_register_info(addr: str, value: str, reg_map: Dict[int, RegisterInfo]) -> List[str]:
    """
    格式化 register 資訊，包含 field 名稱和值

    返回格式化的字串列表
    """
    addr_int = int(addr, 16)
    value_int = safe_hex_to_int(value)
    if value_int is None:
        return []  # 無法解析值時返回空列表
    offset = get_register_offset(addr_int)

    lines = []

    if offset is not None and offset in reg_map:
        reg_info = reg_map[offset]
        for field in reg_info.fields:
            mask = (1 << (field.high_bit - field.low_bit + 1)) - 1
            field_value = (value_int >> field.low_bit) & mask
            width = field.high_bit - field.low_bit + 1
            hex_width = (width + 3) // 4  # 計算需要多少 hex 位數
            lines.append(f"    [{field.high_bit:2d}:{field.low_bit:2d}] {field.name:<30} = 0x{field_value:0{hex_width}x}")

    return lines


def format_diff_with_fields(addr: str, val1: str, val2: str,
                            reg_map: Dict[int, RegisterInfo]) -> List[str]:
    """
    格式化有差異的 register，顯示每個 field 的差異
    """
    addr_int = int(addr, 16)
    val1_int = safe_hex_to_int(val1) or 0
    val2_int = safe_hex_to_int(val2) or 0
    offset = get_register_offset(addr_int)

    lines = []

    if offset is not None and offset in reg_map:
        reg_info = reg_map[offset]
        for field in reg_info.fields:
            mask = (1 << (field.high_bit - field.low_bit + 1)) - 1
            fval1 = (val1_int >> field.low_bit) & mask
            fval2 = (val2_int >> field.low_bit) & mask
            width = field.high_bit - field.low_bit + 1
            hex_width = (width + 3) // 4

            if fval1 != fval2:
                diff_marker = " <-- DIFF"
            else:
                diff_marker = ""

            v1_str = f"0x{fval1:0{hex_width}x}" if val1 else "-"
            v2_str = f"0x{fval2:0{hex_width}x}" if val2 else "-"

            lines.append(f"    [{field.high_bit:2d}:{field.low_bit:2d}] {field.name:<30} "
                        f"File1={v1_str:<10} File2={v2_str:<10}{diff_marker}")

    return lines


def get_special_range(addr_int: int) -> Optional[Tuple[int, int]]:
    """檢查 address 是否在特殊處理範圍內"""
    for start, end in SPECIAL_RANGES:
        if start <= addr_int <= end:
            return (start, end)
    return None


def get_trigger_addr(range_start: int) -> int:
    """取得該 range 的 trigger address (x100)"""
    return range_start


def parse_register_file_with_snapshots(filepath: str) -> Tuple[Dict, Dict[int, List[TriggerSnapshot]]]:
    """
    解析 register 檔案，並記錄特殊範圍的 snapshots
    """
    registers = {}
    special_state = {}
    for start, end in SPECIAL_RANGES:
        special_state[start] = {
            'current': {},
            'snapshots': []
        }

    # 匹配註解行 (以 // 開頭，前面可有空白)
    pattern_comment = re.compile(r'^\s*//')
    pattern_outl = re.compile(r'rtd_outl\s*\(\s*(0x[0-9a-fA-F]+)\s*,\s*(0x[0-9a-fA-F]+)\s*\)')
    pattern_inl = re.compile(r'rtd_inl\s*\(\s*(0x[0-9a-fA-F]+)\s*\).*?//\s*(0x[0-9a-fA-F]+)')
    # 新格式: rbus log
    # 例如: 677111 [rbus] W [b80c2300]<=02020c19 [dcmc1  ]<-[vcpu]
    pattern_rbus_write = re.compile(r'\[rbus\]\s+W\s+\[([0-9a-fA-F]+)\]<=([0-9a-fA-F]+)')
    # R (read) 格式會被忽略: [rbus] R [addr]=>value

    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            # 跳過註解行
            if pattern_comment.match(line):
                continue

            addr = None
            value = None
            op_type = None

            match = pattern_outl.search(line)
            if match:
                addr = normalize_address(match.group(1))
                value = match.group(2).lower()
                op_type = 'outl'
            else:
                match = pattern_inl.search(line)
                if match:
                    addr = normalize_address(match.group(1))
                    value = match.group(2).lower()
                    op_type = 'inl'
                else:
                    # 嘗試匹配 rbus write 格式
                    match = pattern_rbus_write.search(line)
                    if match:
                        # 地址需要加上 0x 前綴
                        addr = normalize_address('0x' + match.group(1))
                        value = '0x' + match.group(2).lower()
                        op_type = 'outl'

            if addr is None:
                continue

            addr_int = int(addr, 16)
            special_range = get_special_range(addr_int)

            if special_range:
                range_start, range_end = special_range
                state = special_state[range_start]
                trigger_addr = get_trigger_addr(range_start)

                if op_type == 'outl':
                    state['current'][addr] = value

                    if addr_int == trigger_addr:
                        value_int = int(value, 16)
                        if value_int & 0x80000000:
                            snapshot = TriggerSnapshot(
                                trigger_line=line_num,
                                trigger_value=value,
                                registers=dict(state['current'])
                            )
                            state['snapshots'].append(snapshot)
            else:
                if addr not in registers:
                    registers[addr] = []
                registers[addr].append((line_num, op_type, value))

    snapshots = {start: state['snapshots'] for start, state in special_state.items()}
    return registers, snapshots


def compare_snapshots(snaps1: List[TriggerSnapshot], snaps2: List[TriggerSnapshot],
                      range_start: int) -> List[dict]:
    """比較兩個檔案的 snapshots"""
    diffs = []
    max_len = max(len(snaps1), len(snaps2)) if snaps1 or snaps2 else 0

    for i in range(max_len):
        snap1 = snaps1[i] if i < len(snaps1) else None
        snap2 = snaps2[i] if i < len(snaps2) else None

        diff_entry = {
            'trigger_index': i + 1,
            'file1_line': snap1.trigger_line if snap1 else None,
            'file2_line': snap2.trigger_line if snap2 else None,
            'file1_trigger': snap1.trigger_value if snap1 else None,
            'file2_trigger': snap2.trigger_value if snap2 else None,
            'reg_diffs': []
        }

        if snap1 is None:
            diff_entry['status'] = 'only_in_file2'
            diff_entry['reg_diffs'] = [(addr, None, val) for addr, val in sorted(snap2.registers.items())]
        elif snap2 is None:
            diff_entry['status'] = 'only_in_file1'
            diff_entry['reg_diffs'] = [(addr, val, None) for addr, val in sorted(snap1.registers.items())]
        else:
            all_addrs = sorted(set(snap1.registers.keys()) | set(snap2.registers.keys()))
            has_diff = False
            for addr in all_addrs:
                val1 = snap1.registers.get(addr)
                val2 = snap2.registers.get(addr)
                if val1 != val2:
                    diff_entry['reg_diffs'].append((addr, val1, val2))
                    has_diff = True
            diff_entry['status'] = 'different' if has_diff else 'same'

        diffs.append(diff_entry)

    return diffs


def compare_registers(file1_regs: Dict, file2_regs: Dict) -> dict:
    """比較兩個檔案的一般 register 差異"""
    all_addresses = sorted(set(file1_regs.keys()) | set(file2_regs.keys()))

    result = {
        'only_in_file1': [],
        'only_in_file2': [],
        'value_diff': [],
        'same': []
    }

    for addr in all_addresses:
        in_file1 = addr in file1_regs
        in_file2 = addr in file2_regs

        if in_file1 and not in_file2:
            result['only_in_file1'].append((addr, file1_regs[addr]))
        elif in_file2 and not in_file1:
            result['only_in_file2'].append((addr, file2_regs[addr]))
        else:
            vals1 = [v for v in file1_regs[addr] if v[1] == 'outl']
            vals2 = [v for v in file2_regs[addr] if v[1] == 'outl']

            if vals1 and vals2:
                last_val1 = vals1[-1][2]
                last_val2 = vals2[-1][2]

                if last_val1 != last_val2:
                    result['value_diff'].append({
                        'address': addr,
                        'file1_value': last_val1,
                        'file2_value': last_val2,
                        'file1_line': vals1[-1][0],
                        'file2_line': vals2[-1][0]
                    })
                else:
                    result['same'].append(addr)
            elif not vals1 and not vals2:
                result['same'].append(addr)

    return result


def format_snapshot_report(all_snap_diffs: Dict[int, List[dict]], file1_name: str,
                           file2_name: str, reg_map: Dict[int, RegisterInfo],
                           ddr_type: str = "LPDDR4") -> str:
    """
    格式化 snapshot 比較報告，回傳字串

    Args:
        all_snap_diffs: snapshot 差異資料
        file1_name: 第一個檔案名稱
        file2_name: 第二個檔案名稱
        reg_map: register 定義 mapping
        ddr_type: DDR 類型 ("LPDDR4" 或 "LPDDR5")，用於 CMD 解析
    """
    lines = []
    lines.append("\n" + "=" * 80)
    lines.append("SPECIAL RANGE COMPARISON (Trigger-based Snapshots)")
    lines.append("=" * 80)

    channel_names = {
        0xb80c2100: "Channel 0 (0xb80c2100~0xb80c2140)",
        0xb80c3100: "Channel 1 (0xb80c3100~0xb80c3140)",
        0xb80c4100: "Channel 2 (0xb80c4100~0xb80c4140)",
        0xb80c5100: "Channel 3 (0xb80c5100~0xb80c5140)",
    }

    for range_start, diffs in all_snap_diffs.items():
        lines.append(f"\n[{channel_names.get(range_start, hex(range_start))}]")
        lines.append(f"  Trigger count: File1={sum(1 for d in diffs if d['file1_line'])} / "
                     f"File2={sum(1 for d in diffs if d['file2_line'])}")
        lines.append("-" * 80)

        for diff in diffs:
            idx = diff['trigger_index']
            status = diff['status']

            if status == 'same':
                lines.append(f"  Trigger #{idx}: SAME (Line {diff['file1_line']} vs {diff['file2_line']})")
            elif status == 'only_in_file1':
                lines.append(f"  Trigger #{idx}: ONLY IN FILE1 (Line {diff['file1_line']})")
            elif status == 'only_in_file2':
                lines.append(f"  Trigger #{idx}: ONLY IN FILE2 (Line {diff['file2_line']})")
            else:
                lines.append(f"  Trigger #{idx}: DIFFERENT (Line {diff['file1_line']} vs {diff['file2_line']})")
                lines.append(f"    {'Address':<14} {'File1':<14} {'File2':<14} {'CMD (if LPDDR4)':<20}")

                for addr, val1, val2 in diff['reg_diffs']:
                    v1 = val1 if val1 else '-'
                    v2 = val2 if val2 else '-'

                    # 檢查是否為 CMD 地址 (0x2110~0x2120) 並解析 CMD
                    cmd_info = ""
                    mr_info = ""
                    if ddr_type == "LPDDR4":
                        addr_int = int(addr, 16)
                        if is_cmd_addr(addr_int):
                            val1_int = safe_hex_to_int(val1) or 0
                            val2_int = safe_hex_to_int(val2) or 0

                            if val1_int:
                                cmd1 = decode_lpddr4_cmd(val1_int)
                            else:
                                cmd1 = "-"
                            if val2_int:
                                cmd2 = decode_lpddr4_cmd(val2_int)
                            else:
                                cmd2 = "-"

                            if cmd1 == cmd2:
                                cmd_info = f"[{cmd1}]"
                            else:
                                cmd_info = f"[{cmd1} -> {cmd2}]"

                            # 如果是 MRW 命令，顯示 MR 編號、值和 rank 資訊
                            mr_parts = []
                            if val1_int and is_mrw_cmd(val1_int):
                                mr_num1, mr_val1 = decode_mrw(val1_int)
                                r0_en1, r1_en1 = decode_mrw_rank(val1_int)
                                rank_str1 = _format_rank_target(r0_en1, r1_en1)
                                mr_parts.append(f"MR{mr_num1}=0x{mr_val1:02X}{rank_str1}")
                            if val2_int and is_mrw_cmd(val2_int):
                                mr_num2, mr_val2 = decode_mrw(val2_int)
                                r0_en2, r1_en2 = decode_mrw_rank(val2_int)
                                rank_str2 = _format_rank_target(r0_en2, r1_en2)
                                if mr_parts:
                                    mr_parts.append(f"MR{mr_num2}=0x{mr_val2:02X}{rank_str2}")
                                else:
                                    mr_parts.append(f"MR{mr_num2}=0x{mr_val2:02X}{rank_str2}")

                            if mr_parts:
                                mr_info = " -> ".join(mr_parts) if len(mr_parts) > 1 else mr_parts[0]

                    line_output = f"    {addr:<14} {v1:<14} {v2:<14} {cmd_info}"
                    if mr_info:
                        line_output += f" ({mr_info})"
                    lines.append(line_output)

                    # 顯示 field 詳細差異
                    if reg_map:
                        field_lines = format_diff_with_fields(addr, val1, val2, reg_map)
                        for fl in field_lines:
                            lines.append(fl)
                        lines.append("")

    return "\n".join(lines)


def print_snapshot_report(all_snap_diffs: Dict[int, List[dict]], file1_name: str,
                          file2_name: str, reg_map: Dict[int, RegisterInfo],
                          ddr_type: str = "LPDDR4"):
    """輸出 snapshot 比較報告"""
    print(format_snapshot_report(all_snap_diffs, file1_name, file2_name, reg_map, ddr_type))


def format_report(result: dict, file1_name: str, file2_name: str,
                  reg_map: Dict[int, RegisterInfo]) -> str:
    """格式化一般比較報告，回傳字串"""
    lines = []
    lines.append("=" * 80)
    lines.append("Register Address Value Comparison Report")
    lines.append("=" * 80)
    lines.append(f"File 1: {file1_name}")
    lines.append(f"File 2: {file2_name}")
    lines.append("=" * 80)

    if result['value_diff']:
        lines.append(f"\n[VALUE DIFFERENCES] ({len(result['value_diff'])} registers)")
        lines.append("-" * 80)

        for diff in result['value_diff']:
            addr = diff['address']
            val1 = diff['file1_value']
            val2 = diff['file2_value']

            lines.append(f"\n{addr}  (Line {diff['file1_line']} vs {diff['file2_line']})")
            lines.append(f"  File1: {val1}")
            lines.append(f"  File2: {val2}")

            if reg_map:
                field_lines = format_diff_with_fields(addr, val1, val2, reg_map)
                if field_lines:
                    lines.append("  Fields:")
                    for fl in field_lines:
                        lines.append(fl)
    else:
        lines.append("\n[VALUE DIFFERENCES] None")

    if result['only_in_file1']:
        lines.append(f"\n[ONLY IN FILE1] ({len(result['only_in_file1'])} registers)")
        lines.append("-" * 80)
        for addr, ops in result['only_in_file1'][:10]:
            last_val = [v for v in ops if v[1] == 'outl']
            val_str = last_val[-1][2] if last_val else "N/A"
            lines.append(f"  {addr}: {val_str}")

            if reg_map:
                field_lines = format_register_info(addr, val_str, reg_map)
                for fl in field_lines:
                    lines.append(fl)

        if len(result['only_in_file1']) > 10:
            lines.append(f"  ... and {len(result['only_in_file1']) - 10} more")

    if result['only_in_file2']:
        lines.append(f"\n[ONLY IN FILE2] ({len(result['only_in_file2'])} registers)")
        lines.append("-" * 80)
        for addr, ops in result['only_in_file2']:
            last_val = [v for v in ops if v[1] == 'outl']
            val_str = last_val[-1][2] if last_val else "N/A"
            lines.append(f"  {addr}: {val_str}")

            if reg_map:
                field_lines = format_register_info(addr, val_str, reg_map)
                for fl in field_lines:
                    lines.append(fl)

    lines.append("\n" + "=" * 80)
    lines.append("SUMMARY (General Registers)")
    lines.append("=" * 80)
    lines.append(f"  Registers with different values: {len(result['value_diff'])}")
    lines.append(f"  Registers only in File1:         {len(result['only_in_file1'])}")
    lines.append(f"  Registers only in File2:         {len(result['only_in_file2'])}")
    lines.append(f"  Registers with same values:      {len(result['same'])}")
    lines.append("=" * 80)

    return "\n".join(lines)


def print_report(result: dict, file1_name: str, file2_name: str,
                 reg_map: Dict[int, RegisterInfo]):
    """輸出一般比較報告"""
    print(format_report(result, file1_name, file2_name, reg_map))


def format_register_map(reg_map: Dict[int, RegisterInfo]) -> str:
    """格式化 register map 參考表，回傳字串"""
    lines = []
    lines.append("\n" + "=" * 80)
    lines.append("REGISTER MAP REFERENCE")
    lines.append("=" * 80)
    lines.append("Note: Offset is relative to channel base (0xb80c2000/3000/4000/5000)")
    lines.append("-" * 80)

    for offset in sorted(reg_map.keys()):
        reg_info = reg_map[offset]
        lines.append(f"\n0x{offset:04x}:")
        for field in reg_info.fields:
            lines.append(f"  [{field.high_bit:2d}:{field.low_bit:2d}] {field.name}")

    return "\n".join(lines)


def print_register_map(reg_map: Dict[int, RegisterInfo]):
    """輸出 register map 參考表"""
    print(format_register_map(reg_map))


def format_single_file_report(file_name: str, registers: Dict, snapshots: Dict[int, List[TriggerSnapshot]],
                               reg_map: Dict[int, RegisterInfo], ddr_type: str = "LPDDR4") -> str:
    """
    格式化單一檔案解析報告（不進行比較）。

    Args:
        file_name: 檔案名稱
        registers: 解析後的 registers dict
        snapshots: 解析後的 snapshots dict
        reg_map: Register 定義 map
        ddr_type: DDR 類型

    Returns:
        格式化的報告字串
    """
    lines = []
    lines.append("=" * 80)
    lines.append("Register Dump Parse Report (Single File)")
    lines.append("=" * 80)
    lines.append(f"File: {file_name}")
    lines.append(f"DDR Type: {ddr_type}")
    lines.append("=" * 80)

    # General registers
    lines.append(f"\n[GENERAL REGISTERS] ({len(registers)} addresses)")
    lines.append("-" * 80)

    sorted_addrs = sorted(registers.keys(), key=lambda x: int(x, 16))
    for addr in sorted_addrs:
        ops = registers[addr]
        outl_ops = [v for v in ops if v[1] == 'outl']
        if outl_ops:
            last_line, _, last_val = outl_ops[-1]
            lines.append(f"  {addr}: {last_val}  (Line {last_line}, {len(outl_ops)} writes)")
            if reg_map:
                for fl in format_register_info(addr, last_val, reg_map):
                    lines.append(fl)

    # Snapshot section
    lines.append("\n" + "=" * 80)
    lines.append("SPECIAL RANGE SNAPSHOTS (Trigger-based)")
    lines.append("=" * 80)

    channel_names = {
        0xb80c2100: "Channel 0 (0xb80c2100~0xb80c2140)",
        0xb80c3100: "Channel 1 (0xb80c3100~0xb80c3140)",
        0xb80c4100: "Channel 2 (0xb80c4100~0xb80c4140)",
        0xb80c5100: "Channel 3 (0xb80c5100~0xb80c5140)",
    }

    for range_start in [0xb80c2100, 0xb80c3100, 0xb80c4100, 0xb80c5100]:
        snap_list = snapshots.get(range_start, [])
        lines.append(f"\n[{channel_names.get(range_start, hex(range_start))}]")
        lines.append(f"  Trigger count: {len(snap_list)}")
        lines.append("-" * 60)

        for idx, snap in enumerate(snap_list, 1):
            lines.append(f"\n  Trigger #{idx} (Line {snap.trigger_line}, Value: {snap.trigger_value})")
            for addr in sorted(snap.registers.keys(), key=lambda x: int(x, 16)):
                value = snap.registers[addr]
                addr_int = int(addr, 16)
                cmd_info = ""
                mr_info = ""
                if ddr_type == "LPDDR4" and is_cmd_addr(addr_int):
                    value_int = safe_hex_to_int(value) or 0
                    if value_int:
                        cmd_info = f" [{decode_lpddr4_cmd(value_int)}]"
                        if is_mrw_cmd(value_int):
                            mr_num, mr_val = decode_mrw(value_int)
                            r0_en, r1_en = decode_mrw_rank(value_int)
                            rank_str = _format_rank_target(r0_en, r1_en)
                            mr_info = f" (MR{mr_num}=0x{mr_val:02X}{rank_str})"
                lines.append(f"    {addr}: {value}{cmd_info}{mr_info}")
                if reg_map:
                    for fl in format_register_info(addr, value, reg_map):
                        lines.append(fl)

    # MR values summary
    if ddr_type == "LPDDR4":
        mr_values = extract_all_mr_values(snapshots, ddr_type)
        if mr_values.get('rank0') or mr_values.get('rank1'):
            lines.append("\n" + "=" * 80)
            lines.append("MODE REGISTER (MR) VALUES SUMMARY")
            lines.append("=" * 80)
            lines.append("Note: bit27=1 -> Rank1, bit26=1 -> Rank0")
            for rank_name, rank_key in [("RANK0 (bit26=1)", 'rank0'), ("RANK1 (bit27=1)", 'rank1')]:
                mr_dict = mr_values.get(rank_key, {})
                lines.append(f"\n[{rank_name}]")
                lines.append("-" * 40)
                if mr_dict:
                    for mr_num in sorted(mr_dict.keys()):
                        lines.append(f"  MR{mr_num:<3}: 0x{mr_dict[mr_num]:02X}")
                else:
                    lines.append("  (No MR values found)")

    # Summary
    lines.append("\n" + "=" * 80)
    lines.append("SUMMARY")
    lines.append("=" * 80)
    lines.append(f"  General registers: {len(registers)}")
    total_triggers = sum(len(snapshots.get(rs, [])) for rs in [0xb80c2100, 0xb80c3100, 0xb80c4100, 0xb80c5100])
    lines.append(f"  Total triggers: {total_triggers}")
    if ddr_type == "LPDDR4":
        mr_values = extract_all_mr_values(snapshots, ddr_type)
        lines.append(f"  MR entries (Rank0): {len(mr_values.get('rank0', {}))}")
        lines.append(f"  MR entries (Rank1): {len(mr_values.get('rank1', {}))}")
    lines.append("=" * 80)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Compare two register dump files',
        epilog=f'Contact: {__author__}'
    )
    parser.add_argument('--version', '-v', action='version',
                        version=f'%(prog)s {__version__} - Contact: {__author__}')
    parser.add_argument('file1', nargs='?', help=f'First register file (default: {FILE1})')
    parser.add_argument('file2', nargs='?', help=f'Second register file (default: {FILE2})')
    parser.add_argument('--regfile', '-r', help=f'Path to regif.v for register name mapping (default: {REGFILE})')
    parser.add_argument('--ddr-type', '-t', choices=['LPDDR4', 'LPDDR5'], default='LPDDR4',
                        help='DDR type for CMD/MR decoding (default: LPDDR4)')
    parser.add_argument('--show-map', action='store_true', help='Show register map reference')

    args = parser.parse_args()

    script_dir = Path(__file__).parent

    # 使用命令列參數或配置檔案中的預設值
    file1 = Path(args.file1) if args.file1 else script_dir / FILE1
    file2 = Path(args.file2) if args.file2 else script_dir / FILE2
    ddr_type = args.ddr_type

    print(f"Comparing: {file1.name} vs {file2.name}")
    print(f"DDR Type: {ddr_type}\n")

    if not file1.exists():
        print(f"Error: File not found: {file1}")
        return 1
    if not file2.exists():
        print(f"Error: File not found: {file2}")
        return 1

    # 嘗試載入 regif.v
    reg_map = {}
    regfile_path = Path(args.regfile) if args.regfile else script_dir / REGFILE

    if Path(regfile_path).exists():
        print(f"Loading register definitions from: {regfile_path}")
        reg_map = parse_regfile_v(str(regfile_path))
        print(f"  Loaded {len(reg_map)} register definitions\n")
    else:
        print("Note: No regfile.v found, register names will not be shown\n")

    if args.show_map and reg_map:
        print_register_map(reg_map)
        return 0

    print("Parsing files...")
    regs1, snaps1 = parse_register_file_with_snapshots(str(file1))
    regs2, snaps2 = parse_register_file_with_snapshots(str(file2))

    print(f"  File1: {len(regs1)} general addresses")
    print(f"  File2: {len(regs2)} general addresses")

    for range_start in snaps1.keys():
        ch_name = f"0x{range_start:08x}"
        print(f"  {ch_name}: File1={len(snaps1[range_start])} triggers, "
              f"File2={len(snaps2[range_start])} triggers")

    # 比較一般 registers
    result = compare_registers(regs1, regs2)
    print_report(result, file1.name, file2.name, reg_map)

    # 比較 snapshots
    all_snap_diffs = {}
    for range_start, _ in SPECIAL_RANGES[:4]:  # 只取前 4 個 (channel 0-3)
        all_snap_diffs[range_start] = compare_snapshots(
            snaps1[range_start],
            snaps2[range_start],
            range_start
        )

    print_snapshot_report(all_snap_diffs, file1.name, file2.name, reg_map, ddr_type)

    # 提取並比較 MR 值 (僅 LPDDR4)
    mr1 = extract_all_mr_values(snaps1, ddr_type)
    mr2 = extract_all_mr_values(snaps2, ddr_type)
    mr_diff = compare_mr_values(mr1, mr2)

    # 輸出 MR 比較報告
    if ddr_type == "LPDDR4" and (mr1.get('rank0') or mr1.get('rank1') or mr2.get('rank0') or mr2.get('rank1')):
        print(format_mr_report(mr_diff, file1.name, file2.name, mr1, mr2))

        # 輸出 MR 差異摘要
        rank0_diff = len(mr_diff.get('rank0', {}).get('value_diff', []))
        rank1_diff = len(mr_diff.get('rank1', {}).get('value_diff', []))
        print(f"\nMR Summary: {rank0_diff + rank1_diff} MR diff (R0:{rank0_diff}, R1:{rank1_diff})")

    return 0


if __name__ == '__main__':
    exit(main())
