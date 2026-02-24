#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MBIST Area Parser

This script parses MBIST (Memory Built-in Self-Test) area data from synthesis reports.
It extracts unique MBIST instance names and their corresponding areas from files
containing specified instance paths, and provides area breakdown analysis.

Usage:
    python dcmc_mbist_parsing.py                                    # Run demo with test data
    python dcmc_mbist_parsing.py <input_file>                       # Parse with user input for instance name
    python dcmc_mbist_parsing.py <input_file> <pattern1> [pattern2] [pattern3] ...    # Parse multiple patterns
    python dcmc_mbist_parsing.py <input_file> <patterns> --debug    # Enable debug output

Instance Pattern:
    Supports wildcards:
    - * : matches any characters
    - ? : matches single character
    
Examples:
    Single pattern:
        mc_fifo_top_inst_0      # specific fifo instance
        mc_fifo_top_inst_*      # all fifo instances (0, 1, 2, etc.)
        
    Multiple patterns:
        python dcmc_mbist_parsing.py data.txt mc_fifo_top_inst_* mc_ctl_top_inst_*
        python dcmc_mbist_parsing.py data.txt inst_0 inst_1 inst_2

Logic:
    - Find all instances matching any of the patterns
    - For each matching instance, analyze MBIST breakdown separately
    - Show independent results for each matching instance

Author: Generated for synthesis report analysis
"""

import re
import os
import fnmatch

# Global debug flag
DEBUG = False

def debug_print(*args, **kwargs):
    """Print only in debug mode"""
    if DEBUG:
        print(*args, **kwargs)

def find_matching_instances(input_file, instance_patterns):
    """
    Find all instances that match any of the patterns
    
    Args:
        input_file (str): Path to input file
        instance_patterns (list): List of patterns to match instance names
        
    Returns:
        list: List of matching instance names
    """
    matching_instances = set()
    
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and data lines
            if not line or line[0].replace('.', '').replace('-', '').isdigit():
                continue
                
            # Check if line matches any of the instance patterns
            for pattern in instance_patterns:
                if fnmatch.fnmatch(line, f"*{pattern}") or fnmatch.fnmatch(line, f"*{pattern}/*"):
                    # Extract the instance name that matches the pattern
                    parts = line.split('/')
                    for part in parts:
                        if fnmatch.fnmatch(part, pattern):
                            matching_instances.add(part)
                            break
    
    return sorted(list(matching_instances))

def find_total_area(input_file, instance_pattern):
    """
    Find the total area of the specified instance pattern
    
    Args:
        input_file (str): Path to input file
        instance_pattern (str): Pattern to match instance names
        
    Returns:
        float: Total area of the instance, or 0 if not found
    """
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        
        for i in range(len(lines)):
            line = lines[i].strip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Look for line that ends with the instance pattern
            if (line.endswith(f"/{instance_pattern}") or line.endswith(instance_pattern)) and not line[0].replace('.', '').replace('-', '').isdigit():
                
                debug_print(f"Found total area line: {line}")
                
                # Check next line for area data
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    parts = next_line.split()
                    
                    # Confirm next line is data line (starts with number)
                    if parts and parts[0].replace('.', '').replace('-', '').isdigit():
                        try:
                            total_area = float(parts[0])
                            debug_print(f"Total area found: {total_area}")
                            return total_area
                        except ValueError:
                            continue
    
    print(f"Warning: Total area for pattern '{instance_pattern}' not found")
    return 0

def parse_mbist_area(input_file, instance_pattern):
    """
    Parse MBIST area data from input file
    
    Args:
        input_file (str): Path to input file
        instance_pattern (str): Exact instance name to match
        
    Returns:
        dict: Dictionary mapping unique keys to mbist data
    """
    mbist_data = {}
    processed_mbist_paths = set()
    
    debug_print(f"Searching for MBIST instances under: '{instance_pattern}'")
    
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        
        for i in range(len(lines)):
            line = lines[i].strip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Check for path line: contains instance_pattern and mbist_, not starting with digit
            if ('mbist_' in line and instance_pattern in line and
                not line[0].replace('.', '').replace('-', '').isdigit()):
                
                # Check if this is a sub-path of any processed mbist path
                is_subpath = False
                for processed_path in processed_mbist_paths:
                    if line.startswith(processed_path + "/"):
                        debug_print(f"Skipping - this is a sub-path of already processed mbist: {processed_path}")
                        is_subpath = True
                        break
                
                if is_subpath:
                    continue
                
                # Extract mbist instance names from path line
                mbist_instances = re.findall(r'mbist_[^/\s]+', line)
                
                if mbist_instances:
                    # Get the mbist instance path (up to the first mbist instance)
                    first_mbist = mbist_instances[0]
                    mbist_path_pattern = f"/{first_mbist}/"
                    
                    # Find the mbist instance path
                    mbist_idx = line.find(mbist_path_pattern)
                    if mbist_idx != -1:
                        mbist_instance_path = line[:mbist_idx + len(f"/{first_mbist}")]
                    else:
                        # If it ends with mbist instance (no trailing slash)
                        mbist_idx = line.rfind(f"/{first_mbist}")
                        if mbist_idx != -1:
                            mbist_instance_path = line[:mbist_idx + len(f"/{first_mbist}")]
                        else:
                            mbist_instance_path = line
                    
                    debug_print(f"Processing MBIST line: {line}")
                    debug_print(f"First mbist instance: {first_mbist}")
                    debug_print(f"Mbist instance path: {mbist_instance_path}")
                    
                    # Check if this exact mbist instance path is already processed
                    if mbist_instance_path in processed_mbist_paths:
                        debug_print(f"Skipping - mbist instance path already processed: {mbist_instance_path}")
                        continue
                    
                    # Check next line for area data
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        parts = next_line.split()
                        
                        # Confirm next line is data line (starts with number)
                        if parts and parts[0].replace('.', '').replace('-', '').isdigit():
                            try:
                                area = float(parts[0])
                                
                                # Create unique key using both name and path
                                # Extract parent path for better display
                                parent_path = mbist_instance_path.split('/')[-2] if '/' in mbist_instance_path else "unknown"
                                unique_key = f"{first_mbist}@{parent_path}"
                                
                                # Record the mbist instance with unique key
                                mbist_data[unique_key] = {
                                    'area': area,
                                    'path': line,
                                    'mbist_name': first_mbist,
                                    'full_path': mbist_instance_path
                                }
                                processed_mbist_paths.add(mbist_instance_path)
                                debug_print(f"Recorded: {unique_key} with area: {area}")
                                debug_print(f"Marked mbist path as processed: {mbist_instance_path}")
                                            
                            except ValueError:
                                continue

    return mbist_data

def print_area_breakdown(total_area, mbist_data, instance_name):
    """Print comprehensive area breakdown analysis"""
    
    # Calculate MBIST total area
    mbist_total_area = sum(data['area'] for data in mbist_data.values())
    digital_area = total_area - mbist_total_area
    
    print(f"\n{'='*80}")
    print(f"AREA BREAKDOWN ANALYSIS FOR: {instance_name}")
    print(f"{'='*80}")
    
    print(f"\nSUMMARY:")
    print(f"{'Total Area:':<20} {total_area:>15,.4f}")
    print(f"{'MBIST Area:':<20} {mbist_total_area:>15,.4f} ({(mbist_total_area/total_area*100):.1f}%)")
    print(f"{'Digital Area:':<20} {digital_area:>15,.4f} ({(digital_area/total_area*100):.1f}%)")
    
    print(f"\nDETAILED MBIST BREAKDOWN:")
    print(f"Total MBIST instances found: {len(mbist_data)}")
    print(f"\n{'MBIST Instance Name':<55} | {'Parent Path':<20} | {'Area':>12}")
    print("-" * 90)
    
    for unique_key, data in sorted(mbist_data.items()):
        mbist_name = data['mbist_name']
        area = data['area']
        parent_path = unique_key.split('@')[1] if '@' in unique_key else "unknown"
        percentage = (area / total_area * 100) if total_area > 0 else 0
        print(f"{mbist_name:<55} | {parent_path:<20} | {area:>12,.4f} ({percentage:.1f}%)")
    
    print("-" * 90)
    print(f"{'MBIST TOTAL':<55} | {'':<20} | {mbist_total_area:>12,.4f}")
    print(f"{'DIGITAL LOGIC':<55} | {'':<20} | {digital_area:>12,.4f}")
    print(f"{'GRAND TOTAL':<55} | {'':<20} | {total_area:>12,.4f}")

def create_test_data(filename):
    """Create test data file for demo"""
    test_data = [
        # Total area line for mc_fifo_top_inst_0
        "dc_mc_top_tmp_inst/dc1_mc_top_wrap_inst_1/mc_fifo_top_wrap_inst/mc_fifo_top_inst_0",
        "431843.8577    25.3     960.7496      0.0000      0.0000  mc_fifo_top_DBG_NAME02_DBG_NAME11_EXP_RFIFO_USE_CTI1",
        "",
        # MBIST instances under mc_fifo_top_inst_0
        "dc_mc_top_tmp_inst/dc1_mc_top_wrap_inst_1/mc_fifo_top_wrap_inst/mc_fifo_top_inst_0/mc_fifo_exp2_inst/mbist_mc_fifo_rdata_top_1024x132_inst",
        "32044.8727    1.9     152.3956     7.0410      0.0000  mbist_mc_fifo_rdata_top_1024x132_NAMEMC1_MCFIFO_3",
        "",
        "dc_mc_top_tmp_inst/dc1_mc_top_wrap_inst_1/mc_fifo_top_wrap_inst/mc_fifo_top_inst_0/mc_fifo_sys_inst/mbist_mc_fifo_rdata_top_128x132_inst",
        "4106.3261    0.2     0.0000      0.0000      0.0000  mbist_mc_fifo_rdata_128x132_NAMEMC1_MCFIFO_0",
        "",
        # Total area line for mc_fifo_top_inst_1  
        "dc_mc_top_tmp_inst/dc1_mc_top_wrap_inst_1/mc_fifo_top_wrap_inst/mc_fifo_top_inst_1",
        "350000.1234    20.5     800.2500      0.0000      0.0000  mc_fifo_top_inst_1_DBG_NAME",
        "",
        # MBIST instances under mc_fifo_top_inst_1
        "dc_mc_top_tmp_inst/dc1_mc_top_wrap_inst_1/mc_fifo_top_wrap_inst/mc_fifo_top_inst_1/mc_fifo_exp_inst/mbist_mc_fifo_rdata_top_512x132_inst",
        "16020.9802    1.5     50.0      0.0000      0.0000  mc_fifo_rdata_top_512x132_inst",
        "",
        "dc_mc_top_tmp_inst/dc1_mc_top_wrap_inst_1/mc_fifo_top_wrap_inst/mc_fifo_top_inst_1/mc_fifo_sys_inst/mbist_mc_fifo_rdata_top_256x148_inst",
        "8855.4659    1.2     40.0      0.0000      0.0000  mc_fifo_rdata_top_256x148_inst",
        "",
        # Additional test data for mc_ctl_top_inst_0
        "dc_mc_top_tmp_inst/dc1_mc_top_wrap_inst_1/mc_ctl_top_wrap_inst/mc_ctl_top_inst_0",
        "125000.5555    15.0     300.0000      0.0000      0.0000  mc_ctl_top_inst_0_DBG_NAME",
        "",
        "dc_mc_top_tmp_inst/dc1_mc_top_wrap_inst_1/mc_ctl_top_wrap_inst/mc_ctl_top_inst_0/mc_ctl_exp_inst/mbist_mc_ctl_data_256x64_inst",
        "5500.1234    0.8     25.0      0.0000      0.0000  mc_ctl_data_256x64_inst"
    ]
    
    with open(filename, 'w') as f:
        for line in test_data:
            f.write(line + '\n')

def run_demo():
    """Run demonstration with test data"""
    test_file = "mbist_test_data.txt"
    
    print("=== MBIST Area Breakdown Analysis Demo ===")
    create_test_data(test_file)
    
    # Demo multiple patterns
    instance_patterns = ["mc_fifo_top_inst_*", "mc_ctl_top_inst_*"]
    
    print(f"\nAnalyzing patterns: {instance_patterns}")
    
    # Find all matching instances
    matching_instances = find_matching_instances(test_file, instance_patterns)
    print(f"Found matching instances: {matching_instances}")
    
    # Analyze each instance separately
    for instance_name in matching_instances:
        print(f"\n{'#'*100}")
        print(f"Analyzing instance: {instance_name}")
        
        # Find total area for this specific instance
        total_area = find_total_area(test_file, instance_name)
        
        # Find MBIST areas for this specific instance
        mbist_data = parse_mbist_area(test_file, instance_name)
        
        # Print comprehensive breakdown
        print_area_breakdown(total_area, mbist_data, instance_name)
    
    # Clean up test file
    os.remove(test_file)
    print(f"\n{'#'*100}")
    print("Demo completed!")

def get_user_input():
    """Get instance patterns from user input"""
    print("\nEnter instance name patterns (supports wildcards * and ?):")
    print("You can enter multiple patterns separated by spaces or commas.")
    print("\nExamples:")
    print("  mc_fifo_top_inst_0                           - single specific instance")
    print("  mc_fifo_top_inst_* mc_ctl_top_inst_*         - multiple wildcard patterns")
    print("  inst_0,inst_1,inst_2                         - multiple specific instances")
    print("  *eff_meas*                                    - contains eff_meas")
    print()
    
    user_input = input("Instance patterns: ").strip()
    if not user_input:
        patterns = ["mc_fifo_top_inst_*"]  # default
        print(f"Using default patterns: {patterns}")
    else:
        # Split by both spaces and commas, then clean up
        import re
        patterns = re.split(r'[,\s]+', user_input)
        patterns = [p.strip() for p in patterns if p.strip()]
        print(f"Using patterns: {patterns}")
    
    return patterns

def main():
    """Main function: process actual file or run demo"""
    import sys
    
    global DEBUG
    
    # Check for debug flag
    if '--debug' in sys.argv:
        DEBUG = True
        sys.argv.remove('--debug')
        print("Debug mode enabled")
    
    if len(sys.argv) == 1:
        # Run demo
        run_demo()
    elif len(sys.argv) == 2:
        # Process actual file with user input
        input_file = sys.argv[1]
        if os.path.exists(input_file):
            instance_patterns = get_user_input()
            print(f"\nAnalyzing file: {input_file}")
            
            # Find all matching instances
            matching_instances = find_matching_instances(input_file, instance_patterns)
            
            if not matching_instances:
                print(f"No instances found matching patterns: {instance_patterns}")
                return
                
            print(f"Found matching instances: {matching_instances}")
            
            # Analyze each instance separately
            for instance_name in matching_instances:
                print(f"\n{'#'*100}")
                print(f"Analyzing instance: {instance_name}")
                
                # Find total area for this specific instance
                total_area = find_total_area(input_file, instance_name)
                
                # Find MBIST areas for this specific instance
                mbist_data = parse_mbist_area(input_file, instance_name)
                
                # Print comprehensive breakdown
                print_area_breakdown(total_area, mbist_data, instance_name)
            
        else:
            print(f"Error: File not found: {input_file}")
            print("\nUsage:")
            print("  python dcmc_mbist_parsing.py                                    # Run demo")
            print("  python dcmc_mbist_parsing.py <input_file>                       # Parse with user input")
            print("  python dcmc_mbist_parsing.py <input_file> <pattern1> [pattern2] ...  # Parse multiple patterns")
            print("  python dcmc_mbist_parsing.py <input_file> <patterns> --debug    # Enable debug output")
    elif len(sys.argv) >= 3:
        # Process actual file with specified patterns (multiple patterns supported)
        input_file = sys.argv[1]
        instance_patterns = sys.argv[2:]  # All remaining arguments are patterns
        
        if os.path.exists(input_file):
            print(f"Analyzing file: {input_file}")
            print(f"Using patterns: {instance_patterns}")
            
            # Find all matching instances
            matching_instances = find_matching_instances(input_file, instance_patterns)
            
            if not matching_instances:
                print(f"No instances found matching patterns: {instance_patterns}")
                return
                
            print(f"Found matching instances: {matching_instances}")
            
            # Analyze each instance separately
            for instance_name in matching_instances:
                print(f"\n{'#'*100}")
                print(f"Analyzing instance: {instance_name}")
                
                # Find total area for this specific instance
                total_area = find_total_area(input_file, instance_name)
                
                # Find MBIST areas for this specific instance
                mbist_data = parse_mbist_area(input_file, instance_name)
                
                # Print comprehensive breakdown
                print_area_breakdown(total_area, mbist_data, instance_name)
            
        else:
            print(f"Error: File not found: {input_file}")
    else:
        print("Usage:")
        print("  python dcmc_mbist_parsing.py                                    # Run demo")
        print("  python dcmc_mbist_parsing.py <input_file>                       # Parse with user input")
        print("  python dcmc_mbist_parsing.py <input_file> <pattern1> [pattern2] ...  # Parse multiple patterns")
        print("  python dcmc_mbist_parsing.py <input_file> <patterns> --debug    # Enable debug output")

if __name__ == "__main__":
    main()
