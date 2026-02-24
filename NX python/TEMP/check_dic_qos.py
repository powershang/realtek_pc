#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dic_Qos.tbl File Version Analyzer

This script searches for all dic_Qos.tbl files in the current directory and subdirectories,
analyzes their content, identifies different versions, and reports which folders contain
each version.

USAGE:
    python check_dic_qos.py [target_filename] [regif_file]
    
    Arguments:
        target_filename    Optional. Target filename to search (default: dic_Qos.tbl)
        regif_file        Optional. Register interface file path (default: mc_regif.v)
    
    Examples:
        python check_dic_qos.py
            # Search for dic_Qos.tbl, use mc_regif.v for bit field mapping
        
        python check_dic_qos.py dic_Qos.tbl
            # Search for dic_Qos.tbl, use mc_regif.v
        
        python check_dic_qos.py dic_Qos.tbl ./hardware/rtl/mc_regif.v
            # Search for dic_Qos.tbl, use custom regif file path
        
        python check_dic_qos.py my_config.txt ../common/my_regif.v
            # Search for my_config.txt, use custom regif file

DESCRIPTION:
    The script will:
    1. Recursively search for specified files in current directory and subdirectories
    2. Calculate MD5 hash for each file to identify unique versions
    3. Group files with identical content together
    4. **Analyze rtd_outl() differences between versions**
       - Parse rtd_outl(address, data) entries
       - Keep only last occurrence of each address (overwrite rule)
       - Compare address/data pairs across versions
       - Identify which addresses have different values
    5. Display analysis results on console
    6. Save complete analysis results to output file
    
    Default mode is SIMPLE MODE (only shows version and paths, no content).
    To see detailed content, set SIMPLE_MODE = False in configuration section.
    
    rtd_outl Analysis:
    - Only lines starting with 'rtd_outl' are analyzed
    - Format: rtd_outl(address, data) where both are hex values
    - If same address appears multiple times, last value wins (overwrite)
    - Compares final address/data pairs between versions
    
    Bit Field Analysis (NEW):
    - Parses register interface file (mc_regif.v) for bit field mappings
    - Extracts signal names from assign statements like: assign mcx2_mode = reg180c2028[9:8]
    - Address matching uses LSB 12 bits (0xb80c2028, 0x180c3028 both match 0x028)
    - When data differs, shows which specific bit fields changed
    - Displays signal name, bit range, and values for both versions

OUTPUT:
    - Console: Summary of findings with file locations (and content if not in simple mode)
    - File: '<filename>_analysis_result.txt' with analysis results

REQUIREMENTS:
    - Python 3.6+
    - Standard library only (no external dependencies)

EXAMPLE OUTPUT (Simple Mode - Default):
    ================================================================================
    File Version Analysis Tool
    ================================================================================
    Current working directory: D:\python_work\project
    Target filename: dic_Qos.tbl
    Register interface file: mc_regif.v
    
    Found 2 different version(s)
    ================================================================================
    
    [Version 1]
    MD5: abc123def456...
    Occurrences: 1 time(s)
    
    Found in folders:
      - D:\python_work\project\folder1
    
    [Version 2]
    MD5: def789ghi012...
    Occurrences: 1 time(s)
    
    Found in folders:
      - D:\python_work\project\folder2
    
    ================================================================================
    rtd_outl DIFFERENCES ANALYSIS (Version 1 as Golden Reference)
    ================================================================================
    
    [Version 2] vs [Version 1 - Golden]
    Version 2 MD5: def789ghi012...
    Version 1 MD5: abc123def456...
    --------------------------------------------------------------------------------
      Found 3 address(es) with differences:
    
      Address: 0xb80c2a60
        [Version 1 - Golden]: 0x0984080e
          Line: rtd_outl(0xb80c2a60,0x0984080e); //CH0
        [Version 2]:        0x0984080f
          Line: rtd_outl(0xb80c2a60,0x0984080f); //CH0
    
      Address: 0xb80c2a64
        [Version 1 - Golden]: 0x4f004f00
          Line: rtd_outl(0xb80c2a64,0x4f004f00); //CH0
        [Version 2]:        0x4e004e00
          Line: rtd_outl(0xb80c2a64,0x4e004e00); //CH0
    
      Address: 0xb80c2a68
        [Version 1 - Golden]: 0x80002008
          Line: rtd_outl(0xb80c2a68,0x80002008); //CH0
        [Version 2]:        >>> NOT PRESENT
    
      Address: 0xb80c2028
        [Version 1 - Golden]: 0x00000100
          Line: rtd_outl(0xb80c2028,0x00000100);
        [Version 2]:        0x00000300
          Line: rtd_outl(0xb80c2028,0x00000300);
        
        >>> Bit Field Differences:
            mcx2_mode                      [9:8]     Golden: 0x1 (1)  vs  Version2: 0x3 (3)
    
    ================================================================================
    SUMMARY
    ================================================================================
    [Version 1 - Golden] Total unique rtd_outl addresses: 150
    [Version 2]           Total unique rtd_outl addresses: 149
    
    Total addresses with differences across all versions: 3
    ================================================================================
    
    Results saved to: dic_Qos_analysis_result.txt

CONFIGURATION:
    Two ways to configure:
    
    1. Command Line Arguments (Recommended):
       python check_dic_qos.py [target_filename] [regif_file]
       
    2. Modify constants in the CONFIGURATION SECTION below:
       - TARGET_FILENAME: Default filename to search for (default: "dic_Qos.tbl")
       - REGIF_FILE: Register interface file path (default: "mc_regif.v")
       - SIMPLE_MODE: True = only show paths, False = show file content (default: True)
       - PREVIEW_LINES: Number of lines to preview (when SIMPLE_MODE = False)

AUTHOR:
    Created for analyzing file versions across multiple directories
"""

import os
import sys
import hashlib
import re
from pathlib import Path
from collections import defaultdict


# ============================================================================
# CONFIGURATION SECTION - Modify these values as needed
# ============================================================================

# Default target filename to search for
TARGET_FILENAME = "dic_Qos.tbl"

# Register interface file for bit field mapping
REGIF_FILE = "mc_regif.v"

# Simple mode: Only show version info and file paths, no content preview
# Set to True for simplified output, False for detailed output with content
SIMPLE_MODE = True

# Number of lines to preview in console output (0 = show all lines)
# Only used when SIMPLE_MODE = False
PREVIEW_LINES = 20

# ============================================================================


def get_file_hash(filepath):
    """
    Calculate MD5 hash of a file.
    
    Args:
        filepath: Path to the file
        
    Returns:
        str: MD5 hash hexdigest, or None if error occurs
    """
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        print(f"Failed to read file {filepath}: {e}")
        return None


def get_file_content(filepath):
    """
    Read file content as text.
    Tries UTF-8 first, then GBK encoding if UTF-8 fails.
    
    Args:
        filepath: Path to the file
        
    Returns:
        str: File content, or None if error occurs
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # If UTF-8 fails, try GBK encoding
        try:
            with open(filepath, 'r', encoding='gbk') as f:
                return f.read()
        except Exception as e:
            print(f"Failed to read file content {filepath}: {e}")
            return None
    except Exception as e:
        print(f"Failed to read file content {filepath}: {e}")
        return None


def parse_regif_file(regif_path):
    """
    Parse register interface file (mc_regif.v) to extract bit field mappings.
    Extracts assign statements like: assign signal_name = regXXXXXXXX[bit_high:bit_low]
    
    Args:
        regif_path: Path to the register interface file
        
    Returns:
        dict: Mapping from LSB 12-bit address to list of (signal_name, bit_high, bit_low)
              Example: {'0x028': [('mcx2_mode', 9, 8), ('mcx2_en', 0, 0), ...]}
    """
    bit_field_map = {}
    
    if not os.path.exists(regif_path):
        print(f"Warning: Register interface file not found: {regif_path}")
        print("Bit field analysis will be skipped.")
        return bit_field_map
    
    try:
        with open(regif_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"Warning: Failed to read register interface file: {e}")
        return bit_field_map
    
    # Pattern to match assign statements
    # Examples:
    # assign mcx2_mode = reg180c2028[9:8];
    # assign mcx2_en = reg180c2028[0];
    pattern = r'assign\s+(\w+)\s*=\s*reg[0-9a-fA-F]+([0-9a-fA-F]{3})\s*\[(\d+)(?::(\d+))?\]'
    
    matches = re.finditer(pattern, content)
    
    for match in matches:
        signal_name = match.group(1)
        addr_lsb12 = '0x' + match.group(2).lower()  # LSB 12 bits
        bit_high = int(match.group(3))
        bit_low_str = match.group(4)
        
        if bit_low_str:
            bit_low = int(bit_low_str)
        else:
            bit_low = bit_high  # Single bit
        
        if addr_lsb12 not in bit_field_map:
            bit_field_map[addr_lsb12] = []
        
        bit_field_map[addr_lsb12].append((signal_name, bit_high, bit_low))
    
    return bit_field_map


def extract_bit_field(data_hex, bit_high, bit_low):
    """
    Extract bit field value from hex data.
    
    Args:
        data_hex: Hex string like '0x12345678'
        bit_high: High bit position
        bit_low: Low bit position
        
    Returns:
        int: Extracted bit field value
    """
    try:
        data_int = int(data_hex, 16)
        mask = (1 << (bit_high - bit_low + 1)) - 1
        field_value = (data_int >> bit_low) & mask
        return field_value
    except:
        return None


def get_lsb12_addr(address_hex):
    """
    Extract LSB 12 bits from address for matching.
    
    Args:
        address_hex: Address string like '0xb80c2028'
        
    Returns:
        str: LSB 12 bits like '0x028'
    """
    try:
        addr_int = int(address_hex, 16)
        lsb12 = addr_int & 0xFFF
        return f'0x{lsb12:03x}'
    except:
        return None


def analyze_bit_field_differences(golden_data_hex, compare_data_hex, address_hex, bit_field_map):
    """
    Analyze bit field differences between two data values.
    
    Args:
        golden_data_hex: Golden version data value (hex string)
        compare_data_hex: Compare version data value (hex string)
        address_hex: Address (hex string)
        bit_field_map: Dictionary mapping addresses to bit fields
        
    Returns:
        list: List of (signal_name, golden_value, compare_value, bit_high, bit_low) for different fields
    """
    differences = []
    
    if golden_data_hex is None or compare_data_hex is None:
        return differences
    
    # Get LSB 12 bits for address matching
    addr_lsb12 = get_lsb12_addr(address_hex)
    
    if addr_lsb12 not in bit_field_map:
        return differences
    
    # Check each bit field
    for signal_name, bit_high, bit_low in bit_field_map[addr_lsb12]:
        golden_field = extract_bit_field(golden_data_hex, bit_high, bit_low)
        compare_field = extract_bit_field(compare_data_hex, bit_high, bit_low)
        
        if golden_field != compare_field:
            differences.append((signal_name, golden_field, compare_field, bit_high, bit_low))
    
    return differences


def parse_rtd_outl(content):
    """
    Parse rtd_outl lines from file content.
    Extract address and data pairs, keeping only the last occurrence of each address.
    
    Args:
        content: File content string
        
    Returns:
        dict: Dictionary mapping address to (data, line_text)
              Only the last occurrence of each address is kept
    """
    if not content:
        return {}
    
    # Pattern to match rtd_outl(address, data)
    # Matches: rtd_outl(0xb80c2a00,0x00000643);
    pattern = r'rtd_outl\s*\(\s*(0x[0-9a-fA-F]+)\s*,\s*(0x[0-9a-fA-F]+)\s*\)'
    
    address_data_map = {}  # {address: (data, line_text)}
    
    lines = content.split('\n')
    for line in lines:
        line_stripped = line.strip()
        if line_stripped.startswith('rtd_outl'):
            match = re.search(pattern, line_stripped)
            if match:
                address = match.group(1).lower()  # Normalize to lowercase
                data = match.group(2).lower()     # Normalize to lowercase
                # Keep only the last occurrence (will overwrite previous)
                address_data_map[address] = (data, line_stripped)
    
    return address_data_map


def compare_rtd_outl_versions(hash_to_content):
    """
    Compare rtd_outl entries across different versions.
    
    Args:
        hash_to_content: Dictionary mapping hash to file content
        
    Returns:
        dict: Analysis results including differences between versions
    """
    version_rtd_data = {}  # {hash: {address: (data, line)}}
    
    # Parse rtd_outl for each version
    for file_hash, content in hash_to_content.items():
        version_rtd_data[file_hash] = parse_rtd_outl(content)
    
    return version_rtd_data


def find_rtd_outl_differences(version_rtd_data):
    """
    Find differences in rtd_outl entries between versions.
    
    Args:
        version_rtd_data: Dict mapping version hash to {address: (data, line)}
        
    Returns:
        dict: Differences organized by address
    """
    if len(version_rtd_data) < 2:
        return {}
    
    # Collect all addresses across all versions
    all_addresses = set()
    for rtd_data in version_rtd_data.values():
        all_addresses.update(rtd_data.keys())
    
    differences = {}  # {address: {hash: (data, line)}}
    
    # Check each address to see if it has different values across versions
    for address in sorted(all_addresses):
        version_values = {}
        for version_hash, rtd_data in version_rtd_data.items():
            if address in rtd_data:
                data, line = rtd_data[address]
                version_values[version_hash] = (data, line)
            else:
                version_values[version_hash] = (None, None)  # Address not present
        
        # Check if this address has different values across versions
        unique_values = set(data for data, _ in version_values.values() if data is not None)
        
        # If more than one unique value, or some versions missing this address
        has_none = any(data is None for data, _ in version_values.values())
        if len(unique_values) > 1 or (len(unique_values) == 1 and has_none):
            differences[address] = version_values
    
    return differences


def print_rtd_outl_analysis(version_rtd_data, hash_to_files, bit_field_map):
    """
    Print rtd_outl analysis showing differences between versions.
    Uses Version 1 as golden reference and compares other versions against it.
    
    Args:
        version_rtd_data: Dict mapping version hash to {address: (data, line)}
        hash_to_files: Dictionary mapping hash to file paths
        bit_field_map: Dictionary mapping addresses to bit fields
    """
    if len(version_rtd_data) < 2:
        print("\nOnly one version found, no comparison needed.")
        return
    
    print("\n" + "=" * 80)
    print("rtd_outl DIFFERENCES ANALYSIS (Version 1 as Golden Reference)")
    print("=" * 80)
    
    if bit_field_map:
        print(f"Bit field mapping loaded: {sum(len(v) for v in bit_field_map.values())} fields across {len(bit_field_map)} addresses")
    else:
        print("No bit field mapping available - showing address/data differences only")
    
    version_list = list(version_rtd_data.keys())
    golden_hash = version_list[0]  # Version 1 is golden
    golden_data = version_rtd_data[golden_hash]
    
    total_differences = 0
    
    # Compare each version against golden (Version 1)
    for idx, compare_hash in enumerate(version_list[1:], 2):  # Start from Version 2
        compare_data = version_rtd_data[compare_hash]
        
        # Find all differences between golden and this version
        diff_addresses = []
        
        # Collect all unique addresses
        all_addresses = set(golden_data.keys()) | set(compare_data.keys())
        
        for address in all_addresses:
            golden_value = golden_data.get(address, (None, None))
            compare_value = compare_data.get(address, (None, None))
            
            # Check if different
            if golden_value[0] != compare_value[0]:  # Compare data values
                diff_addresses.append(address)
        
        # Print differences for this version
        print(f"\n[Version {idx}] vs [Version 1 - Golden]")
        print(f"Version {idx} MD5: {compare_hash[:16]}...")
        print(f"Version 1 MD5: {golden_hash[:16]}...")
        print("-" * 80)
        
        if not diff_addresses:
            print("  >>> No differences found! Identical to Golden version.\n")
        else:
            print(f"  Found {len(diff_addresses)} address(es) with differences:\n")
            total_differences += len(diff_addresses)
            
            for address in sorted(diff_addresses):
                golden_value = golden_data.get(address, (None, None))
                compare_value = compare_data.get(address, (None, None))
                
                print(f"  Address: {address}")
                
                # Golden version value
                if golden_value[0] is None:
                    print(f"    [Version 1 - Golden]: >>> NOT PRESENT")
                else:
                    print(f"    [Version 1 - Golden]: {golden_value[0]}")
                    print(f"      Line: {golden_value[1]}")
                
                # Comparing version value
                if compare_value[0] is None:
                    print(f"    [Version {idx}]:        >>> NOT PRESENT")
                else:
                    print(f"    [Version {idx}]:        {compare_value[0]}")
                    print(f"      Line: {compare_value[1]}")
                
                # Bit field analysis
                if bit_field_map and golden_value[0] and compare_value[0]:
                    bit_diffs = analyze_bit_field_differences(
                        golden_value[0], compare_value[0], address, bit_field_map
                    )
                    
                    if bit_diffs:
                        print(f"\n    >>> Bit Field Differences:")
                        for signal_name, golden_field, compare_field, bit_high, bit_low in bit_diffs:
                            if bit_high == bit_low:
                                bit_range = f"[{bit_high}]"
                            else:
                                bit_range = f"[{bit_high}:{bit_low}]"
                            
                            print(f"        {signal_name:30s} {bit_range:8s}  Golden: 0x{golden_field:x} ({golden_field})  vs  Version{idx}: 0x{compare_field:x} ({compare_field})")
                
                print()
    
    # Summary statistics
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"[Version 1 - Golden] Total unique rtd_outl addresses: {len(golden_data)}")
    for idx, version_hash in enumerate(version_list[1:], 2):
        rtd_data = version_rtd_data[version_hash]
        print(f"[Version {idx}]           Total unique rtd_outl addresses: {len(rtd_data)}")
    print(f"\nTotal addresses with differences across all versions: {total_differences}")
    print("=" * 80)


def find_files(root_dir, target_filename):
    """
    Find all files with specified filename in directory and subdirectories.
    
    Args:
        root_dir: Root directory to start search
        target_filename: Name of file to search for
        
    Returns:
        list: List of Path objects for found files
    """
    found_files = []
    root_path = Path(root_dir)
    
    print(f"Starting search in: {root_dir}")
    print("=" * 80)
    
    # Recursively search for all files with target filename
    for filepath in root_path.rglob(target_filename):
        if filepath.is_file():
            found_files.append(filepath)
            print(f"Found file: {filepath}")
    
    print(f"\nTotal found: {len(found_files)} {target_filename} files")
    print("=" * 80)
    
    return found_files


def analyze_versions(files):
    """
    Analyze file versions by grouping files with identical content.
    Uses MD5 hash to identify unique versions.
    
    Args:
        files: List of file paths
        
    Returns:
        tuple: (hash_to_files dict, hash_to_content dict)
            - hash_to_files: Maps MD5 hash to list of file paths
            - hash_to_content: Maps MD5 hash to file content
    """
    # Use hash as key, store list of file paths
    hash_to_files = defaultdict(list)
    # Store hash corresponding to content
    hash_to_content = {}
    
    print("\nAnalyzing file contents...")
    print("=" * 80)
    
    for filepath in files:
        file_hash = get_file_hash(filepath)
        if file_hash:
            hash_to_files[file_hash].append(filepath)
            # Only need to read content once per unique hash
            if file_hash not in hash_to_content:
                content = get_file_content(filepath)
                hash_to_content[file_hash] = content
    
    return hash_to_files, hash_to_content


def print_results(hash_to_files, hash_to_content, simple_mode=SIMPLE_MODE, preview_lines=PREVIEW_LINES):
    """
    Print analysis results to console.
    Shows version info, locations, and optionally content preview.
    
    Args:
        hash_to_files: Dictionary mapping hash to file paths
        hash_to_content: Dictionary mapping hash to file content
        simple_mode: If True, only show version and paths (no content)
        preview_lines: Number of lines to preview (0 = show all lines, only used when simple_mode=False)
    """
    num_versions = len(hash_to_files)
    
    print(f"\nFound {num_versions} different version(s)")
    print("=" * 80)
    
    for idx, (file_hash, filepaths) in enumerate(hash_to_files.items(), 1):
        print(f"\n[Version {idx}]")
        print(f"MD5: {file_hash}")
        print(f"Occurrences: {len(filepaths)} time(s)")
        print(f"\nFound in folders:")
        
        for filepath in sorted(filepaths):
            # Display folder path containing the file
            folder = filepath.parent
            print(f"  - {folder}")
        
        # Display file content only if not in simple mode
        if not simple_mode:
            content = hash_to_content.get(file_hash)
            if content:
                lines = content.split('\n')
                print(f"\nFile content ({len(lines)} lines total):")
                print("-" * 80)
                
                # Show all lines or preview based on configuration
                if preview_lines == 0 or len(lines) <= preview_lines:
                    display_lines = lines
                else:
                    display_lines = lines[:preview_lines]
                
                for line in display_lines:
                    print(f"  {line}")
                
                if preview_lines > 0 and len(lines) > preview_lines:
                    print(f"  ... ({len(lines) - preview_lines} more lines)")
                print("-" * 80)
        
        print()


def main():
    """
    Main function to orchestrate the analysis process.
    """
    # Parse command line arguments
    if len(sys.argv) > 1:
        target_filename = sys.argv[1]
    else:
        target_filename = TARGET_FILENAME
    
    if len(sys.argv) > 2:
        regif_file = sys.argv[2]
    else:
        regif_file = REGIF_FILE
    
    # Get current working directory
    current_dir = os.getcwd()
    
    print("=" * 80)
    print("File Version Analysis Tool")
    print("=" * 80)
    print(f"Current working directory: {current_dir}")
    print(f"Target filename: {target_filename}")
    print(f"Register interface file: {regif_file}")
    print(f"Mode: {'Simple (paths only)' if SIMPLE_MODE else 'Detailed (with content)'}\n")
    
    # Find all target files
    files = find_files(current_dir, target_filename)
    
    if not files:
        print(f"\nNo {target_filename} files found")
        return
    
    # Analyze versions
    hash_to_files, hash_to_content = analyze_versions(files)
    
    # Print results to console
    print_results(hash_to_files, hash_to_content)
    
    # Parse register interface file for bit field mapping
    print(f"\nSearching for register interface file: {regif_file}")
    bit_field_map = parse_regif_file(regif_file)
    if bit_field_map:
        print(f"Successfully loaded bit field mappings from {regif_file}")
    
    # Analyze rtd_outl differences
    version_rtd_data = compare_rtd_outl_versions(hash_to_content)
    print_rtd_outl_analysis(version_rtd_data, hash_to_files, bit_field_map)
    
    # Save results to file
    save_results_to_file(hash_to_files, hash_to_content, target_filename, version_rtd_data, bit_field_map, regif_file)


def save_results_to_file(hash_to_files, hash_to_content, target_filename, version_rtd_data, bit_field_map, regif_file, simple_mode=SIMPLE_MODE):
    """
    Save complete analysis results to a text file.
    Output file: <filename_without_ext>_analysis_result.txt
    
    Args:
        hash_to_files: Dictionary mapping hash to file paths
        hash_to_content: Dictionary mapping hash to file content
        target_filename: Name of the target file being analyzed
        version_rtd_data: Dictionary mapping version hash to rtd_outl data
        bit_field_map: Dictionary mapping addresses to bit fields
        regif_file: Path to register interface file
        simple_mode: If True, only save version and paths (no content)
    """
    # Generate output filename based on target filename
    base_name = os.path.splitext(target_filename)[0]
    output_file = f"{base_name}_analysis_result.txt"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"{target_filename} File Analysis Results\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Target filename: {target_filename}\n")
            f.write(f"Register interface file: {regif_file}\n")
            f.write(f"Mode: {'Simple (paths only)' if simple_mode else 'Detailed (with content)'}\n")
            f.write(f"Found {len(hash_to_files)} different version(s)\n\n")
            
            for idx, (file_hash, filepaths) in enumerate(hash_to_files.items(), 1):
                f.write(f"[Version {idx}]\n")
                f.write(f"MD5: {file_hash}\n")
                f.write(f"Occurrences: {len(filepaths)} time(s)\n\n")
                f.write("Found in folders:\n")
                
                for filepath in sorted(filepaths):
                    folder = filepath.parent
                    f.write(f"  - {folder}\n")
                
                # Save file content only if not in simple mode
                if not simple_mode:
                    content = hash_to_content.get(file_hash)
                    if content:
                        lines = content.split('\n')
                        f.write(f"\nFile content ({len(lines)} lines total):\n")
                        f.write("-" * 80 + "\n")
                        for line in lines:
                            f.write(f"{line}\n")
                        f.write("-" * 80 + "\n")
                
                f.write("\n\n")
            
            # Add rtd_outl analysis section
            f.write("\n" + "=" * 80 + "\n")
            f.write("rtd_outl DIFFERENCES ANALYSIS (Version 1 as Golden Reference)\n")
            f.write("=" * 80 + "\n\n")
            
            if len(version_rtd_data) < 2:
                f.write("Only one version found, no comparison needed.\n")
            else:
                version_list = list(version_rtd_data.keys())
                golden_hash = version_list[0]  # Version 1 is golden
                golden_data = version_rtd_data[golden_hash]
                
                total_differences = 0
                
                # Compare each version against golden (Version 1)
                for idx, compare_hash in enumerate(version_list[1:], 2):  # Start from Version 2
                    compare_data = version_rtd_data[compare_hash]
                    
                    # Find all differences between golden and this version
                    diff_addresses = []
                    
                    # Collect all unique addresses
                    all_addresses = set(golden_data.keys()) | set(compare_data.keys())
                    
                    for address in all_addresses:
                        golden_value = golden_data.get(address, (None, None))
                        compare_value = compare_data.get(address, (None, None))
                        
                        # Check if different
                        if golden_value[0] != compare_value[0]:  # Compare data values
                            diff_addresses.append(address)
                    
                    # Write differences for this version
                    f.write(f"\n[Version {idx}] vs [Version 1 - Golden]\n")
                    f.write(f"Version {idx} MD5: {compare_hash[:16]}...\n")
                    f.write(f"Version 1 MD5: {golden_hash[:16]}...\n")
                    f.write("-" * 80 + "\n")
                    
                    if not diff_addresses:
                        f.write("  >>> No differences found! Identical to Golden version.\n\n")
                    else:
                        f.write(f"  Found {len(diff_addresses)} address(es) with differences:\n\n")
                        total_differences += len(diff_addresses)
                        
                        for address in sorted(diff_addresses):
                            golden_value = golden_data.get(address, (None, None))
                            compare_value = compare_data.get(address, (None, None))
                            
                            f.write(f"  Address: {address}\n")
                            
                            # Golden version value
                            if golden_value[0] is None:
                                f.write(f"    [Version 1 - Golden]: >>> NOT PRESENT\n")
                            else:
                                f.write(f"    [Version 1 - Golden]: {golden_value[0]}\n")
                                f.write(f"      Line: {golden_value[1]}\n")
                            
                            # Comparing version value
                            if compare_value[0] is None:
                                f.write(f"    [Version {idx}]:        >>> NOT PRESENT\n")
                            else:
                                f.write(f"    [Version {idx}]:        {compare_value[0]}\n")
                                f.write(f"      Line: {compare_value[1]}\n")
                            
                            # Bit field analysis
                            if bit_field_map and golden_value[0] and compare_value[0]:
                                bit_diffs = analyze_bit_field_differences(
                                    golden_value[0], compare_value[0], address, bit_field_map
                                )
                                
                                if bit_diffs:
                                    f.write(f"\n    >>> Bit Field Differences:\n")
                                    for signal_name, golden_field, compare_field, bit_high, bit_low in bit_diffs:
                                        if bit_high == bit_low:
                                            bit_range = f"[{bit_high}]"
                                        else:
                                            bit_range = f"[{bit_high}:{bit_low}]"
                                        
                                        f.write(f"        {signal_name:30s} {bit_range:8s}  Golden: 0x{golden_field:x} ({golden_field})  vs  Version{idx}: 0x{compare_field:x} ({compare_field})\n")
                            
                            f.write("\n")
                
                # Summary
                f.write("=" * 80 + "\n")
                f.write("SUMMARY\n")
                f.write("=" * 80 + "\n")
                f.write(f"[Version 1 - Golden] Total unique rtd_outl addresses: {len(golden_data)}\n")
                for idx, version_hash in enumerate(version_list[1:], 2):
                    rtd_data = version_rtd_data[version_hash]
                    f.write(f"[Version {idx}]           Total unique rtd_outl addresses: {len(rtd_data)}\n")
                f.write(f"\nTotal addresses with differences across all versions: {total_differences}\n")
                f.write("=" * 80 + "\n")
        
        print(f"\nResults saved to: {output_file}")
        
    except Exception as e:
        print(f"Failed to save results file: {e}")


if __name__ == "__main__":
    main()
