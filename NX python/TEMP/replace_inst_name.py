#!/usr/bin/env python3

import re
import sys
import os
import glob
import shutil
from pathlib import Path

def find_file_recursive(filename, search_dir="."):
    """
    Find file recursively in subdirectories
    """
    for root, dirs, files in os.walk(search_dir):
        if filename in files:
            return os.path.join(root, filename)
    return None

def backup_file(file_path):
    """
    Create backup of file before modification
    """
    backup_path = file_path + ".backup"
    shutil.copy2(file_path, backup_path)
    print(f"Backup created: {backup_path}")
    return backup_path

def replace_names_in_line(line, inst_name, new_inst_name, design_unit, new_design_unit):
    """
    Replace instance name and design unit name in a line
    """
    modified = False
    original_line = line
    
    # Replace instance name
    if inst_name in line:
        line = line.replace(inst_name, new_inst_name)
        modified = True
        print(f"  Replaced instance: {inst_name} -> {new_inst_name}")
    
    # Replace design unit name  
    if design_unit in line:
        line = line.replace(design_unit, new_design_unit)
        modified = True
        print(f"  Replaced design unit: {design_unit} -> {new_design_unit}")
    
    return line, modified

def apply_renames(results, rename_rules):
    """
    Apply rename rules to files based on unresolved instance results
    """
    if not results:
        print("No unresolved instances to process")
        return
    
    success_count = 0
    failed_count = 0
    
    for result in results:
        file_name = result['file']
        line_num = int(result['line'])
        inst_name = result['inst_name']
        design_unit = result['design_unit']
        
        print(f"\nProcessing: {file_name}:{line_num}")
        print(f"Instance: {inst_name}, Design Unit: {design_unit}")
        
        # Find file recursively
        file_path = find_file_recursive(file_name)
        if not file_path:
            print(f"  ERROR: File not found: {file_name}")
            failed_count += 1
            continue
        
        print(f"  Found file: {file_path}")
        
        # Apply rename rules
        new_inst_name = inst_name
        new_design_unit = design_unit
        
        for old_pattern, new_pattern in rename_rules:
            new_inst_name = new_inst_name.replace(old_pattern, new_pattern)
            new_design_unit = new_design_unit.replace(old_pattern, new_pattern)
        
        # Skip if no changes needed
        if new_inst_name == inst_name and new_design_unit == design_unit:
            print(f"  SKIP: No rename needed")
            continue
        
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if line_num > len(lines):
                print(f"  ERROR: Line {line_num} not found in file (file has {len(lines)} lines)")
                failed_count += 1
                continue
            
            # Check if target line contains the instance/design unit
            target_line = lines[line_num - 1]  # Convert to 0-based index
            if inst_name not in target_line and design_unit not in target_line:
                print(f"  ERROR: Instance or design unit not found in line {line_num}")
                print(f"  Line content: {target_line.strip()}")
                failed_count += 1
                continue
            
            # Create backup
            backup_path = backup_file(file_path)
            
            # Apply replacement
            new_line, modified = replace_names_in_line(target_line, inst_name, new_inst_name, design_unit, new_design_unit)
            
            if modified:
                lines[line_num - 1] = new_line
                
                # Write modified file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                print(f"  SUCCESS: File modified")
                success_count += 1
            else:
                print(f"  SKIP: No changes made")
                # Remove unnecessary backup
                os.remove(backup_path)
                
        except Exception as e:
            print(f"  ERROR: {e}")
            failed_count += 1
    
    print(f"\n=== Summary ===")
    print(f"Successfully processed: {success_count}")
    print(f"Failed: {failed_count}")

def parse_unresolved_instances(input_file):
    """
    Parse unresolved instance error messages
    Extract format: file line_number inst_name design_unit_name
    """
    results = []
    
    # Regular expression pattern to match unresolved instance errors
    # Match format: ncelab: *E,CUVMUR (file.v,line|col): instance 'inst_name' of design unit 'design_unit' is unresolved
    pattern = r"ncelab:\s+\*E,\w+\s+\(([^,]+),(\d+)\|\d+\):\s+instance\s+'([^']+)'\s+of\s+design\s+unit\s+'([^']+)'\s+is\s+unresolved"
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                match = re.search(pattern, line)
                if match:
                    file_path = match.group(1).split('/')[-1]  # Extract filename only
                    line_num = match.group(2)
                    inst_name = match.group(3)
                    design_unit = match.group(4)
                    
                    results.append({
                        'file': file_path,
                        'line': line_num,
                        'inst_name': inst_name,
                        'design_unit': design_unit
                    })
    
    except FileNotFoundError:
        print(f"Error: File not found {input_file}")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []
    
    return results

def print_results(results):
    """Print results"""
    if not results:
        print("No unresolved instances found")
        return
    
    print("File\t\t\tLine\tInst_Name\t\t\tDesign_Unit_Name")
    print("-" * 80)
    
    for result in results:
        print(f"{result['file']:<20}\t{result['line']:<6}\t{result['inst_name']:<25}\t{result['design_unit']}")

def save_to_file(results, output_file):
    """Save results to file"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("File\tLine\tInst_Name\tDesign_Unit_Name\n")
            for result in results:
                f.write(f"{result['file']}\t{result['line']}\t{result['inst_name']}\t{result['design_unit']}\n")
        print(f"Results saved to {output_file}")
    except Exception as e:
        print(f"Error saving file: {e}")

def test_regex():
    """Test function to verify regex pattern"""
    test_line = "ncelab: *E,CUVMUR (./hdmi2p2_v2/hd22_gdi_rx/hd22_hdmi_rx/hd22_timegen/hd22_video_retiming.v,751|30): instance 'hd22_video_retiming.rline_cnt_g2b' of design unit 'hd21_gray2bin_13b' is unresolved in 'worklib.hd22_video_retiming'."
    
    pattern = r"ncelab:\s+\*E,\w+\s+\(([^,]+),(\d+)\|\d+\):\s+instance\s+'([^']+)'\s+of\s+design\s+unit\s+'([^']+)'\s+is\s+unresolved"
    
    match = re.search(pattern, test_line)
    if match:
        file_path = match.group(1).split('/')[-1]
        line_num = match.group(2)
        inst_name = match.group(3)
        design_unit = match.group(4)
        
        print("Regex test successful!")
        print(f"File: {file_path}")
        print(f"Line: {line_num}")
        print(f"Instance: {inst_name}")
        print(f"Design Unit: {design_unit}")
    else:
        print("Regex test failed - no match found")

def main():
    if len(sys.argv) < 2:
        print("Usage: python replace_inst_name.py <command> [arguments]")
        print("Commands:")
        print("  parse <error_file> [output_file]     - Parse unresolved instances")
        print("  rename <error_file>                  - Apply renames (hd21->hd22, hdmi21->hdmi22)")
        print("  test                                 - Run regex test")
        print("\nExamples:")
        print("  python replace_inst_name.py parse ncverilog.log")
        print("  python replace_inst_name.py rename ncverilog.log")
        return
    
    command = sys.argv[1]
    
    if command == "test":
        test_regex()
        return
    
    elif command == "parse":
        if len(sys.argv) < 3:
            print("Error: Please specify error message file")
            return
        
        input_file = sys.argv[2]
        output_file = sys.argv[3] if len(sys.argv) > 3 else None
        
        print(f"Parsing file: {input_file}")
        results = parse_unresolved_instances(input_file)
        
        if results:
            print(f"\nFound {len(results)} unresolved instances:")
            print_results(results)
            
            if output_file:
                save_to_file(results, output_file)
        else:
            print("No unresolved instances found")
    
    elif command == "rename":
        if len(sys.argv) < 3:
            print("Error: Please specify error message file")
            return
        
        input_file = sys.argv[2]
        
        print(f"Parsing file: {input_file}")
        results = parse_unresolved_instances(input_file)
        
        if results:
            print(f"\nFound {len(results)} unresolved instances:")
            print_results(results)
            
            # Define rename rules: hd21 -> hd22, hdmi21 -> hdmi22
            rename_rules = [
                ("hd21", "hd22"),
                ("hdmi21", "hdmi22")
            ]
            
            print(f"\nApplying rename rules: {rename_rules}")
            apply_renames(results, rename_rules)
        else:
            print("No unresolved instances found")
    
    else:
        print(f"Error: Unknown command '{command}'")
        print("Use 'python replace_inst_name.py' without arguments to see usage")

if __name__ == "__main__":
    main()
