#!/usr/bin/env python3
"""
生成內建 Register Map 資料的腳本

用法:
    python generate_embedded_regmap.py [regfile.v]

預設會讀取 dc_mc1_regfile.v，並更新 embedded_regmap.py 中的 EMBEDDED_REGMAP_DATA
"""

import sys
import re
from pathlib import Path


def parse_regfile_v_to_dict(filepath: str) -> dict:
    """
    解析 regif.v 檔案，輸出適合內嵌的格式

    返回: {offset: [(name, high_bit, low_bit), ...]}
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
                    registers[reg_offset] = []

                registers[reg_offset].append((signal_name, high_bit, low_bit))

    # 對每個 register 的 fields 按 bit 位置排序 (高位在前)
    for offset in registers:
        registers[offset].sort(key=lambda f: f[1], reverse=True)

    return registers


def generate_embedded_file(regmap_data: dict, output_path: str):
    """
    生成 embedded_regmap.py 檔案

    Args:
        regmap_data: {offset: [(name, high_bit, low_bit), ...]}
        output_path: 輸出檔案路徑
    """
    # 讀取現有的模板
    template_path = Path(__file__).parent / "embedded_regmap.py"

    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 格式化 regmap 資料
    lines = ["EMBEDDED_REGMAP_DATA: Dict[int, List[tuple]] = {"]
    for offset in sorted(regmap_data.keys()):
        fields = regmap_data[offset]
        fields_str = ", ".join([f'("{name}", {high}, {low})' for name, high, low in fields])
        lines.append(f"    0x{offset:04x}: [{fields_str}],")
    lines.append("}")
    new_data_str = "\n".join(lines)

    # 替換 EMBEDDED_REGMAP_DATA 區塊
    pattern = r'EMBEDDED_REGMAP_DATA: Dict\[int, List\[tuple\]\] = \{\}'
    if re.search(pattern, content):
        new_content = re.sub(pattern, new_data_str, content)
    else:
        # 如果已經有資料，替換整個區塊
        pattern = r'EMBEDDED_REGMAP_DATA: Dict\[int, List\[tuple\]\] = \{[^}]*\}'
        new_content = re.sub(pattern, new_data_str, content, flags=re.DOTALL)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"Generated {output_path} with {len(regmap_data)} register definitions")


def main():
    script_dir = Path(__file__).parent

    # 預設 regfile 路徑
    if len(sys.argv) > 1:
        regfile_path = Path(sys.argv[1])
    else:
        regfile_path = script_dir / "dc_mc1_regfile.v"

    if not regfile_path.exists():
        print(f"Error: Regfile not found: {regfile_path}")
        return 1

    print(f"Parsing: {regfile_path}")
    regmap_data = parse_regfile_v_to_dict(str(regfile_path))
    print(f"Found {len(regmap_data)} register definitions")

    # 輸出到 embedded_regmap.py
    output_path = script_dir / "embedded_regmap.py"
    generate_embedded_file(regmap_data, str(output_path))

    return 0


if __name__ == "__main__":
    sys.exit(main())
