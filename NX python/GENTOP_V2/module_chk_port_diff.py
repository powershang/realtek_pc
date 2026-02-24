#!/usr/bin/env python3.11
"""
Verilog Module Port Difference Analyzer

This script compares the ports between two Verilog files and identifies differences.
It can detect:
- Ports that exist in one file but not the other
- Ports with the same name but different bit widths
- Ports with the same name but different directions (input/output)

Usage:
    python module_chk_port_diff.py <file1.v> <file2.v>

Example:
    python module_chk_port_diff.py aaa.v bbb.v

Based on the proven port parsing logic from rtk_conn_by_pattern.py
"""

import re
import sys
import os

def parse_bus_width(bus_width_str):
    """
    Convert bus width string [N:0] to decimal number
    Example: [2:0] -> 3, [31:0] -> 32
    """
    if not bus_width_str:
        return 1
    match = re.match(r'\[(\d+):(\d+)\]', bus_width_str)
    if match:
        high = int(match.group(1))
        low = int(match.group(2))
        return high - low + 1
    return 1

def extract_module_ports(file_path):
    """
    Extract all module ports from a Verilog file
    Returns a dictionary with port_name as key and (direction, bit_width, bus_width_str) as value
    """
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found!")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None
    
    ports = {}
    
    # Find module definition
    module_pattern = r'module\s+(\w+)\s*\((.*?)\);'
    module_match = re.search(module_pattern, content, re.DOTALL)
    
    if not module_match:
        print(f"Warning: No module definition found in {file_path}")
        return ports
    
    module_name = module_match.group(1)
    print(f"Found module: {module_name} in {file_path}")
    
    # Extract port declarations from module body
    # Look for input, output, and inout declarations
    port_patterns = [
        r'^\s*(input|output|inout)\s+(?:wire\s+)?(?:reg\s+)?(\[[\d:]+\])?\s*(\w+)\s*[,;]',
        r'^\s*(input|output|inout)\s+(\[[\d:]+\])?\s*(?:wire\s+)?(?:reg\s+)?(\w+)\s*[,;]'
    ]
    
    lines = content.split('\n')
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('//'):
            continue
            
        for pattern in port_patterns:
            match = re.match(pattern, line)
            if match:
                if len(match.groups()) == 3:
                    direction = match.group(1)
                    bus_width_str = match.group(2) if match.group(2) else ""
                    port_name = match.group(3)
                else:
                    continue
                
                bit_width = parse_bus_width(bus_width_str)
                ports[port_name] = (direction, bit_width, bus_width_str)
                # print(f"  Found port: {direction} {bus_width_str if bus_width_str else ''} {port_name} (line {line_num})")
                break
    
    return ports

def compare_ports(file1, file2):
    """
    Compare ports between two Verilog files and report differences
    """
    print(f"=== Comparing ports between {file1} and {file2} ===\n")
    
    # Extract ports from both files
    ports1 = extract_module_ports(file1)
    ports2 = extract_module_ports(file2)
    
    if ports1 is None or ports2 is None:
        return False
    
    print(f"\n=== Port Comparison Results ===")
    print(f"File 1 ({file1}): {len(ports1)} ports")
    print(f"File 2 ({file2}): {len(ports2)} ports")
    
    # Find differences
    differences_found = False
    
    # Ports only in file1
    only_in_file1 = set(ports1.keys()) - set(ports2.keys())
    if only_in_file1:
        differences_found = True
        print(f"\n=== Ports only in {file1} ===")
        for port in sorted(only_in_file1):
            direction, bit_width, bus_width_str = ports1[port]
            width_str = f"{bus_width_str}" if bus_width_str else ""
            print(f"  {direction:<7} {width_str:<10} {port:<30} ({bit_width} bits)")
    
    # Ports only in file2
    only_in_file2 = set(ports2.keys()) - set(ports1.keys())
    if only_in_file2:
        differences_found = True
        print(f"\n=== Ports only in {file2} ===")
        for port in sorted(only_in_file2):
            direction, bit_width, bus_width_str = ports2[port]
            width_str = f"{bus_width_str}" if bus_width_str else ""
            print(f"  {direction:<7} {width_str:<10} {port:<30} ({bit_width} bits)")
    
    # Common ports with differences
    common_ports = set(ports1.keys()) & set(ports2.keys())
    different_common_ports = []
    
    for port in common_ports:
        dir1, width1, bus_str1 = ports1[port]
        dir2, width2, bus_str2 = ports2[port]
        
        if dir1 != dir2 or width1 != width2:
            different_common_ports.append(port)
    
    if different_common_ports:
        differences_found = True
        print(f"\n=== Common ports with differences ===")
        for port in sorted(different_common_ports):
            dir1, width1, bus_str1 = ports1[port]
            dir2, width2, bus_str2 = ports2[port]
            width_str1 = f"{bus_str1}" if bus_str1 else ""
            width_str2 = f"{bus_str2}" if bus_str2 else ""
            print(f"  {dir1:<7} {width_str1:<10} {port:<30} ({file1})")
            print(f"  {dir2:<7} {width_str2:<10} {port:<30} ({file2})")
    
    # Summary
    print(f"\n=== Summary ===")
    if not differences_found:
        print("OK No port differences found! The modules have identical ports.")
    else:
        total_diffs = len(only_in_file1) + len(only_in_file2) + len(different_common_ports)
        print(f"ERROR Found {total_diffs} port differences:")
        if only_in_file1:
            print(f"  - {len(only_in_file1)} ports only in {file1}")
        if only_in_file2:
            print(f"  - {len(only_in_file2)} ports only in {file2}")
        if different_common_ports:
            print(f"  - {len(different_common_ports)} common ports with differences")
    
    return True

def main():
    if len(sys.argv) != 3:
        print("Error: Please provide exactly two Verilog file paths")
        print("\nUsage:")
        print("  python module_chk_port_diff.py <file1.v> <file2.v>")
        print("\nExample:")
        print("  python module_chk_port_diff.py aaa.v bbb.v")
        sys.exit(1)
    
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    
    success = compare_ports(file1, file2)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
