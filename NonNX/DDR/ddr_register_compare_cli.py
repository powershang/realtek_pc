#!/usr/bin/env python3
"""
DDR Register Address Value Comparer (CLI Version)

Compare two register dump files and report differences.

Special handling: c2100~c2140 range
- Record snapshot when c2100[31]=1
- Compare values at each trigger

Supports reading register name mapping from regif.v

Contact: shane_wu #25696
Version: 1.0.0

Usage:
    python ddr_register_compare_cli.py file1.tbl file2.tbl
    python ddr_register_compare_cli.py file1.tbl file2.tbl --regfile dc_mc1_regfile.v
    python ddr_register_compare_cli.py file1.tbl file2.tbl --ddr-type LPDDR4
    python ddr_register_compare_cli.py --parse file.tbl          # Parse single file without comparison
    python ddr_register_compare_cli.py --help
"""

__author__ = "shane_wu #25696"
__version__ = "1.0.0"

import re
import argparse
import sys
from pathlib import Path


# =============================================================================
# USER CONFIGURATION - Modify this section as needed
# =============================================================================

# Default comparison files
FILE1 = "SW_SDP.tbl"
FILE2 = "SW_DDP.tbl"

# Register definition file (for displaying field names)
REGFILE = "dc_mc1_regfile.v"

# =============================================================================
# END OF USER CONFIGURATION
# =============================================================================


# Special register ranges that need trigger-based snapshot handling (per channel)
# Supports two address formats: 0xb80cXXXX and 0x180cXXXX
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

# Channel base addresses (for mapping)
# Supports two address formats: 0xb80cXXXX and 0x180cXXXX
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
# Used for parsing CMD in 0x2110~0x2120 range
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

# CMD address offsets (relative to channel base)
CMD_ADDR_OFFSETS = [0x110, 0x114, 0x118, 0x11c, 0x120]


def safe_hex_to_int(value, default=0):
    """
    Safely convert hex string to integer.
    Handles "N/A", None and invalid values.

    Args:
        value: Hex string to convert
        default: Default value if conversion fails

    Returns:
        Integer value or None if invalid
    """
    if not value or value.upper() == "N/A":
        return None
    try:
        return int(value, 16)
    except ValueError:
        return None


def normalize_address(addr):
    """
    Normalize address format from 0x180... to 0xb80... format.
    Example: 0x180c52ac -> 0xb80c52ac

    Args:
        addr: Address string

    Returns:
        Normalized address string
    """
    addr_lower = addr.lower()
    if addr_lower.startswith('0x180'):
        return '0xb80' + addr_lower[5:]
    return addr_lower


def decode_lpddr4_cmd(value):
    """
    Decode LPDDR4 CMD from register value's BIT31:BIT28.

    Args:
        value: Complete 32-bit register value

    Returns:
        CMD name string, or "Unknown" if not recognized
    """
    cmd_bits = (value >> 28) & 0xF
    return LPDDR4_CMD_TABLE.get(cmd_bits, f"Unknown (0x{cmd_bits:X})")


def is_mrw_cmd(value):
    """
    Check if value is a MRW (Mode Register Write) command.

    Args:
        value: Register value

    Returns:
        True if MRW command
    """
    cmd_bits = (value >> 28) & 0xF
    return cmd_bits == 0x6  # MRW-1 / MRW-2


def decode_mrw(value):
    """
    Decode MRW command to get Mode Register number and value.

    Args:
        value: Complete 32-bit register value

    Returns:
        (mr_number, mr_value): MR number (BIT13:8) and value (BIT7:0)
    """
    mr_number = (value >> 8) & 0x3F  # BIT13:BIT8 (6 bits)
    mr_value = value & 0xFF          # BIT7:BIT0 (8 bits)
    return mr_number, mr_value


def decode_mrw_rank(value):
    """
    Decode MRW command rank target.

    bit27 = 1: Target rank1
    bit26 = 1: Target rank0
    bit27 = 1 and bit26 = 1: Update both rank0 and rank1

    Args:
        value: Complete 32-bit register value

    Returns:
        (rank0_enable, rank1_enable): Whether rank0/rank1 is targeted
    """
    rank1_enable = bool((value >> 27) & 0x1)  # bit27
    rank0_enable = bool((value >> 26) & 0x1)  # bit26
    return rank0_enable, rank1_enable


def format_rank_target(rank0_enable, rank1_enable):
    """
    Format rank target string.

    Args:
        rank0_enable: Whether rank0 is targeted
        rank1_enable: Whether rank1 is targeted

    Returns:
        Formatted string, e.g., "[R0]", "[R1]", "[R0,R1]", or ""
    """
    if rank0_enable and rank1_enable:
        return "[R0,R1]"
    elif rank0_enable:
        return "[R0]"
    elif rank1_enable:
        return "[R1]"
    else:
        return ""


def is_cmd_addr(addr_int):
    """
    Check if address is in CMD parsing range (0x2110~0x2120).

    Args:
        addr_int: Integer address

    Returns:
        True if in CMD range
    """
    for base in CHANNEL_BASES.keys():
        if base <= addr_int < base + 0x1000:
            offset = addr_int - base
            if offset in CMD_ADDR_OFFSETS:
                return True
    return False


def get_addr_offset(addr_int):
    """
    Get address offset relative to channel base.

    Args:
        addr_int: Integer address

    Returns:
        Offset or None if not in channel range
    """
    for base in CHANNEL_BASES.keys():
        if base <= addr_int < base + 0x1000:
            return addr_int - base
    return None


def get_register_offset(addr_int):
    """
    Get register offset from full address (for querying reg_map).

    Args:
        addr_int: Integer address

    Returns:
        Register offset or None
    """
    for base in CHANNEL_BASES.keys():
        if base <= addr_int < base + 0x1000:
            relative_offset = addr_int - base
            return 0x2000 + relative_offset
    return None


def get_special_range(addr_int):
    """
    Check if address is in special handling range.

    Args:
        addr_int: Integer address

    Returns:
        (start, end) tuple or None
    """
    for start, end in SPECIAL_RANGES:
        if start <= addr_int <= end:
            return (start, end)
    return None


def get_trigger_addr(range_start):
    """
    Get trigger address for a range (x100).

    Args:
        range_start: Range start address

    Returns:
        Trigger address
    """
    return range_start


class BitField:
    """Register bit field definition"""

    def __init__(self, name, high_bit, low_bit):
        self.name = name
        self.high_bit = high_bit
        self.low_bit = low_bit

    def __str__(self):
        if self.high_bit == self.low_bit:
            return f"{self.name}[{self.high_bit}]"
        else:
            return f"{self.name}[{self.high_bit}:{self.low_bit}]"


class RegisterInfo:
    """Register information"""

    def __init__(self, offset):
        self.offset = offset  # Offset relative to channel base (e.g., 0x100)
        self.fields = []

    def get_field_value(self, value, field_name):
        """Get value of a specific field"""
        for f in self.fields:
            if f.name == field_name:
                mask = (1 << (f.high_bit - f.low_bit + 1)) - 1
                return (value >> f.low_bit) & mask
        return None


class TriggerSnapshot:
    """Snapshot at trigger event"""

    def __init__(self, trigger_line, trigger_value):
        self.trigger_line = trigger_line
        self.trigger_value = trigger_value
        self.registers = {}


def parse_regfile_v(filepath):
    """
    Parse regif.v file to extract register definitions.

    Args:
        filepath: Path to regif.v file

    Returns:
        {offset: RegisterInfo}
        offset is relative to channel base (e.g., 0x2100 -> 0x100)
    """
    registers = {}

    # Match: assign signal = reg180cXXXX[high:low] or reg180cXXXX[bit]
    pattern = re.compile(
        r'assign\s+(\w+)\s*=\s*reg180c([0-9a-fA-F]{4})\[(\d+)(?::(\d+))?\]'
    )

    try:
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
    except Exception as e:
        print(f"Warning: Failed to parse regfile: {e}")
        return {}

    # Sort fields by bit position (high bits first)
    for reg in registers.values():
        reg.fields.sort(key=lambda f: f.high_bit, reverse=True)

    return registers


def parse_register_file_with_snapshots(filepath):
    """
    Parse register file and record snapshots for special ranges.

    Args:
        filepath: Path to register dump file

    Returns:
        (registers, snapshots)
        registers: {addr: [(line_num, op_type, value), ...]}
        snapshots: {range_start: [TriggerSnapshot, ...]}
    """
    registers = {}
    special_state = {}
    for start, end in SPECIAL_RANGES:
        special_state[start] = {
            'current': {},
            'snapshots': []
        }

    # Patterns for different log formats
    pattern_comment = re.compile(r'^\s*//')
    pattern_outl = re.compile(r'rtd_outl\s*\(\s*(0x[0-9a-fA-F]+)\s*,\s*(0x[0-9a-fA-F]+)\s*\)')
    pattern_inl = re.compile(r'rtd_inl\s*\(\s*(0x[0-9a-fA-F]+)\s*\).*?//\s*(0x[0-9a-fA-F]+)')
    # rbus log format: 677111 [rbus] W [b80c2300]<=02020c19 [dcmc1]<-[vcpu]
    pattern_rbus_write = re.compile(r'\[rbus\]\s+W\s+\[([0-9a-fA-F]+)\]<=([0-9a-fA-F]+)')

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # Skip comment lines
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
                        # Try rbus write format
                        match = pattern_rbus_write.search(line)
                        if match:
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

                        # Check for trigger (bit 31 = 1)
                        if addr_int == trigger_addr:
                            value_int = int(value, 16)
                            if value_int & 0x80000000:
                                snapshot = TriggerSnapshot(
                                    trigger_line=line_num,
                                    trigger_value=value
                                )
                                snapshot.registers = dict(state['current'])
                                state['snapshots'].append(snapshot)
                else:
                    if addr not in registers:
                        registers[addr] = []
                    registers[addr].append((line_num, op_type, value))

    except Exception as e:
        print(f"Error parsing file {filepath}: {e}")
        return {}, {start: [] for start, _ in SPECIAL_RANGES}

    snapshots = {start: state['snapshots'] for start, state in special_state.items()}
    return registers, snapshots


def compare_registers(file1_regs, file2_regs):
    """
    Compare register values between two files.

    Args:
        file1_regs: Registers from file 1
        file2_regs: Registers from file 2

    Returns:
        {
            'only_in_file1': [(addr, ops), ...],
            'only_in_file2': [(addr, ops), ...],
            'value_diff': [{address, file1_value, file2_value, ...}, ...],
            'same': [addr, ...]
        }
    """
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


def compare_snapshots(snaps1, snaps2, range_start):
    """
    Compare snapshots between two files.

    Args:
        snaps1: Snapshots from file 1
        snaps2: Snapshots from file 2
        range_start: Start address of the range

    Returns:
        List of diff entries
    """
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


def extract_all_mr_values(snapshots, ddr_type="LPDDR4"):
    """
    Extract final MR values from all snapshots across all channels.

    Args:
        snapshots: {range_start: [TriggerSnapshot, ...]}
        ddr_type: DDR type

    Returns:
        {
            'rank0': {mr_number: mr_value},
            'rank1': {mr_number: mr_value}
        }
    """
    if ddr_type != "LPDDR4":
        return {'rank0': {}, 'rank1': {}}

    mr_values = {'rank0': {}, 'rank1': {}}

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


def compare_single_rank_mr(mr1, mr2):
    """
    Compare MR values for a single rank.

    Args:
        mr1: File 1 MR values {mr_number: mr_value}
        mr2: File 2 MR values {mr_number: mr_value}

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


def compare_mr_values(mr1, mr2):
    """
    Compare MR values between two files, independently per rank.

    Args:
        mr1: File 1 MR values {'rank0': {...}, 'rank1': {...}}
        mr2: File 2 MR values {'rank0': {...}, 'rank1': {...}}

    Returns:
        {
            'rank0': {comparison results},
            'rank1': {comparison results}
        }
    """
    return {
        'rank0': compare_single_rank_mr(mr1.get('rank0', {}), mr2.get('rank0', {})),
        'rank1': compare_single_rank_mr(mr1.get('rank1', {}), mr2.get('rank1', {}))
    }


def format_register_info(addr, value, reg_map):
    """
    Format register information with field names and values.

    Args:
        addr: Address string
        value: Value string
        reg_map: Register definition map

    Returns:
        List of formatted strings
    """
    addr_int = int(addr, 16)
    value_int = safe_hex_to_int(value)
    if value_int is None:
        return []
    offset = get_register_offset(addr_int)

    lines = []

    if offset is not None and offset in reg_map:
        reg_info = reg_map[offset]
        for field in reg_info.fields:
            mask = (1 << (field.high_bit - field.low_bit + 1)) - 1
            field_value = (value_int >> field.low_bit) & mask
            width = field.high_bit - field.low_bit + 1
            hex_width = (width + 3) // 4
            lines.append(f"    [{field.high_bit:2d}:{field.low_bit:2d}] {field.name:<30} = 0x{field_value:0{hex_width}x}")

    return lines


def format_diff_with_fields(addr, val1, val2, reg_map):
    """
    Format register difference with field-level details.

    Args:
        addr: Address string
        val1: Value 1 string
        val2: Value 2 string
        reg_map: Register definition map

    Returns:
        List of formatted strings
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


def format_report(result, file1_name, file2_name, reg_map):
    """
    Format general comparison report.

    Args:
        result: Comparison result
        file1_name: File 1 name
        file2_name: File 2 name
        reg_map: Register definition map

    Returns:
        Formatted report string
    """
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


def format_snapshot_report(all_snap_diffs, file1_name, file2_name, reg_map, ddr_type="LPDDR4"):
    """
    Format snapshot comparison report.

    Args:
        all_snap_diffs: Snapshot difference data
        file1_name: File 1 name
        file2_name: File 2 name
        reg_map: Register definition map
        ddr_type: DDR type for CMD parsing

    Returns:
        Formatted report string
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

                    # Check if CMD address and decode CMD
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

                            # If MRW command, show MR number, value and rank info
                            mr_parts = []
                            if val1_int and is_mrw_cmd(val1_int):
                                mr_num1, mr_val1 = decode_mrw(val1_int)
                                r0_en1, r1_en1 = decode_mrw_rank(val1_int)
                                rank_str1 = format_rank_target(r0_en1, r1_en1)
                                mr_parts.append(f"MR{mr_num1}=0x{mr_val1:02X}{rank_str1}")
                            if val2_int and is_mrw_cmd(val2_int):
                                mr_num2, mr_val2 = decode_mrw(val2_int)
                                r0_en2, r1_en2 = decode_mrw_rank(val2_int)
                                rank_str2 = format_rank_target(r0_en2, r1_en2)
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

                    # Show field-level differences
                    if reg_map:
                        field_lines = format_diff_with_fields(addr, val1, val2, reg_map)
                        for fl in field_lines:
                            lines.append(fl)
                        lines.append("")

    return "\n".join(lines)


def format_single_rank_mr_report(rank_diff, rank_name, mr1_values, mr2_values):
    """
    Format MR comparison report for a single rank.

    Args:
        rank_diff: Difference data for this rank
        rank_name: Rank display name
        mr1_values: File1 MR values for this rank
        mr2_values: File2 MR values for this rank

    Returns:
        List of formatted lines
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

    all_mr_nums = sorted(set(mr1_values.keys()) | set(mr2_values.keys()))

    if all_mr_nums:
        lines.append(f"    {'MR#':<6} {'File1':<12} {'File2':<12}")
        lines.append(f"    {'-'*6} {'-'*12} {'-'*12}")
        for mr_num in all_mr_nums:
            val1_str = f"0x{mr1_values[mr_num]:02X}" if mr_num in mr1_values else "-"
            val2_str = f"0x{mr2_values[mr_num]:02X}" if mr_num in mr2_values else "-"
            # Mark differences
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


def format_mr_report(mr_diff, file1_name, file2_name, mr1=None, mr2=None):
    """
    Format MR comparison report with per-rank details.

    Args:
        mr_diff: MR difference data
        file1_name: File 1 name
        file2_name: File 2 name
        mr1: File1 MR values
        mr2: File2 MR values

    Returns:
        Formatted report string
    """
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

    # Rank0 report
    rank0_diff = mr_diff.get('rank0', {'value_diff': [], 'only_in_file1': [], 'only_in_file2': [], 'same': []})
    lines.extend(format_single_rank_mr_report(
        rank0_diff, "RANK0 (bit26=1)",
        mr1.get('rank0', {}), mr2.get('rank0', {})
    ))

    # Rank1 report
    rank1_diff = mr_diff.get('rank1', {'value_diff': [], 'only_in_file1': [], 'only_in_file2': [], 'same': []})
    lines.extend(format_single_rank_mr_report(
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


def format_register_map(reg_map):
    """
    Format register map reference table.

    Args:
        reg_map: Register definition map

    Returns:
        Formatted reference table string
    """
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


def format_single_file_report(file_name, registers, snapshots, reg_map, ddr_type="LPDDR4"):
    """
    Format report for a single parsed file (no comparison).

    Args:
        file_name: Name of the parsed file
        registers: Parsed registers dict
        snapshots: Parsed snapshots dict
        reg_map: Register definition map
        ddr_type: DDR type for CMD/MR decoding

    Returns:
        Formatted report string
    """
    lines = []
    lines.append("=" * 80)
    lines.append("Register Dump Parse Report (Single File)")
    lines.append("=" * 80)
    lines.append(f"File: {file_name}")
    lines.append(f"DDR Type: {ddr_type}")
    lines.append("=" * 80)

    # General registers section
    lines.append(f"\n[GENERAL REGISTERS] ({len(registers)} addresses)")
    lines.append("-" * 80)

    # Sort by address
    sorted_addrs = sorted(registers.keys(), key=lambda x: int(x, 16))

    for addr in sorted_addrs:
        ops = registers[addr]
        outl_ops = [v for v in ops if v[1] == 'outl']
        if outl_ops:
            last_line, _, last_val = outl_ops[-1]
            lines.append(f"  {addr}: {last_val}  (Line {last_line}, {len(outl_ops)} writes)")

            # Show field details if reg_map available
            if reg_map:
                field_lines = format_register_info(addr, last_val, reg_map)
                for fl in field_lines:
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

            sorted_snap_addrs = sorted(snap.registers.keys(), key=lambda x: int(x, 16))
            for addr in sorted_snap_addrs:
                value = snap.registers[addr]
                addr_int = int(addr, 16)

                # CMD info for LPDDR4
                cmd_info = ""
                mr_info = ""
                if ddr_type == "LPDDR4" and is_cmd_addr(addr_int):
                    value_int = safe_hex_to_int(value) or 0
                    if value_int:
                        cmd_info = f" [{decode_lpddr4_cmd(value_int)}]"
                        if is_mrw_cmd(value_int):
                            mr_num, mr_val = decode_mrw(value_int)
                            r0_en, r1_en = decode_mrw_rank(value_int)
                            rank_str = format_rank_target(r0_en, r1_en)
                            mr_info = f" (MR{mr_num}=0x{mr_val:02X}{rank_str})"

                lines.append(f"    {addr}: {value}{cmd_info}{mr_info}")

                # Show field details if reg_map available
                if reg_map:
                    field_lines = format_register_info(addr, value, reg_map)
                    for fl in field_lines:
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
                        mr_val = mr_dict[mr_num]
                        lines.append(f"  MR{mr_num:<3}: 0x{mr_val:02X}")
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
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Compare two DDR register dump files or parse a single file',
        epilog=f'Contact: {__author__}',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--version', '-v', action='version',
                        version=f'%(prog)s {__version__} - Contact: {__author__}')
    parser.add_argument('file1', nargs='?', help=f'First register file (default: {FILE1})')
    parser.add_argument('file2', nargs='?', help=f'Second register file (default: {FILE2})')
    parser.add_argument('--parse', '-p', action='store_true',
                        help='Parse single file only, no comparison')
    parser.add_argument('--regfile', '-r',
                        help=f'Path to regif.v for register name mapping (default: {REGFILE})')
    parser.add_argument('--ddr-type', '-t', choices=['LPDDR4', 'LPDDR5'], default='LPDDR4',
                        help='DDR type for CMD/MR decoding (default: LPDDR4)')
    parser.add_argument('--show-map', action='store_true',
                        help='Show register map reference')
    parser.add_argument('--output', '-o',
                        help='Output file path (default: print to stdout)')

    args = parser.parse_args()

    script_dir = Path(__file__).parent
    ddr_type = args.ddr_type

    # Try to load regif.v
    reg_map = {}
    regfile_path = Path(args.regfile) if args.regfile else script_dir / REGFILE

    if Path(regfile_path).exists():
        reg_map = parse_regfile_v(str(regfile_path))

    # Show register map only
    if args.show_map and reg_map:
        output_lines = []
        output_lines.append(f"Loading register definitions from: {regfile_path}")
        output_lines.append(f"  Loaded {len(reg_map)} register definitions")
        output_lines.append(format_register_map(reg_map))
        output_text = "\n".join(output_lines)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_text)
            print(f"Output written to: {args.output}")
        else:
            print(output_text)
        return 0

    # Single file parse mode
    if args.parse:
        if not args.file1:
            print("Error: Please specify a file to parse")
            print("Usage: python ddr_register_compare_cli.py --parse <file>")
            return 1

        file1 = Path(args.file1)
        if not file1.exists():
            print(f"Error: File not found: {file1}")
            return 1

        output_lines = []
        if reg_map:
            output_lines.append(f"Loading register definitions from: {regfile_path}")
            output_lines.append(f"  Loaded {len(reg_map)} register definitions\n")
        else:
            output_lines.append("Note: No regfile.v found, register names will not be shown\n")

        output_lines.append("Parsing file...")
        regs, snaps = parse_register_file_with_snapshots(str(file1))

        output_lines.append(f"  {len(regs)} general addresses")
        for range_start in [0xb80c2100, 0xb80c3100, 0xb80c4100, 0xb80c5100]:
            ch_name = f"0x{range_start:08x}"
            output_lines.append(f"  {ch_name}: {len(snaps.get(range_start, []))} triggers")

        output_lines.append("")
        output_lines.append(format_single_file_report(file1.name, regs, snaps, reg_map, ddr_type))

        output_text = "\n".join(output_lines)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_text)
            print(f"Output written to: {args.output}")
        else:
            print(output_text)

        return 0

    # Comparison mode (default)
    # Use command line arguments or default values
    file1 = Path(args.file1) if args.file1 else script_dir / FILE1
    file2 = Path(args.file2) if args.file2 else script_dir / FILE2

    output_lines = []

    output_lines.append(f"Comparing: {file1.name} vs {file2.name}")
    output_lines.append(f"DDR Type: {ddr_type}\n")

    if not file1.exists():
        print(f"Error: File not found: {file1}")
        return 1
    if not file2.exists():
        print(f"Error: File not found: {file2}")
        return 1

    if reg_map:
        output_lines.append(f"Loading register definitions from: {regfile_path}")
        output_lines.append(f"  Loaded {len(reg_map)} register definitions\n")
    else:
        output_lines.append("Note: No regfile.v found, register names will not be shown\n")

    output_lines.append("Parsing files...")
    regs1, snaps1 = parse_register_file_with_snapshots(str(file1))
    regs2, snaps2 = parse_register_file_with_snapshots(str(file2))

    output_lines.append(f"  File1: {len(regs1)} general addresses")
    output_lines.append(f"  File2: {len(regs2)} general addresses")

    for range_start in snaps1.keys():
        ch_name = f"0x{range_start:08x}"
        output_lines.append(f"  {ch_name}: File1={len(snaps1[range_start])} triggers, "
                           f"File2={len(snaps2[range_start])} triggers")

    # Compare general registers
    result = compare_registers(regs1, regs2)
    output_lines.append(format_report(result, file1.name, file2.name, reg_map))

    # Compare snapshots
    all_snap_diffs = {}
    for range_start, _ in SPECIAL_RANGES[:4]:  # Only first 4 (channel 0-3)
        all_snap_diffs[range_start] = compare_snapshots(
            snaps1[range_start],
            snaps2[range_start],
            range_start
        )

    output_lines.append(format_snapshot_report(all_snap_diffs, file1.name, file2.name, reg_map, ddr_type))

    # Extract and compare MR values (LPDDR4 only)
    mr1 = extract_all_mr_values(snaps1, ddr_type)
    mr2 = extract_all_mr_values(snaps2, ddr_type)
    mr_diff = compare_mr_values(mr1, mr2)

    # Output MR comparison report
    if ddr_type == "LPDDR4" and (mr1.get('rank0') or mr1.get('rank1') or mr2.get('rank0') or mr2.get('rank1')):
        output_lines.append(format_mr_report(mr_diff, file1.name, file2.name, mr1, mr2))

        # Output MR difference summary
        rank0_diff = len(mr_diff.get('rank0', {}).get('value_diff', []))
        rank1_diff = len(mr_diff.get('rank1', {}).get('value_diff', []))
        output_lines.append(f"\nMR Summary: {rank0_diff + rank1_diff} MR diff (R0:{rank0_diff}, R1:{rank1_diff})")

    # Output results
    output_text = "\n".join(output_lines)
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_text)
        print(f"Output written to: {args.output}")
    else:
        print(output_text)

    return 0


if __name__ == '__main__':
    sys.exit(main())
