#!/usr/bin/env python3.11
"""
Verilog Signal Analyzer and Comment Modifier
==========================================

A Python tool to analyze Verilog files and modify signal comments based on their properties.

Main Purpose
-----------
Convert Verilog signals marked with specific comment patterns to corresponding realtek format.

Supports two comment types:
1. '// realtekshane wire' - for wire signals
2. '// realtekshane port' - for port signals

Conversion Rules:

For '// realtekshane wire' signals:
- Input signals:
  Original: // realtekshane wire
  Converted to:
    // realtek assign signal_name = N'b0;
    // realtek wire signal_name

- Output signals:
  Original: // realtekshane wire
  Converted to: // realtek wire signal_name

For '// realtekshane port' signals:
- Input signals:
  Original: // realtekshane port signal_name
  Converted to: // realtek input signal_name.[N-1:0]  (multi-bit signals)
  Converted to: // realtek input signal_name          (single-bit signals)

- Output signals:
  Original: // realtekshane port signal_name
  Converted to:
    // realtek output signal_name.[N-1:0]  (multi-bit signals)
    // realtek assign signal_name = N'd0;
  Or:
    // realtek output signal_name          (single-bit signals)
    // realtek assign signal_name = 1'd0;

Features
--------
- Supports two comment patterns: '// realtekshane wire' and '// realtekshane port'
- Automatically detects signal direction (input/output) and bit width
- Generates appropriate realtek format comments based on signal type
- Creates assign statements with initial values for input signals (wire type) or input declarations (port type)
- Creates wire declarations for output signals (wire type) or output declarations with tie values (port type)
- Supports multi-bit signals and various signal declaration formats
- Automatically calculates bit width and generates corresponding initial values

Usage
-----
Run the script with a Verilog file as argument:
    python rtk_conn_by_comment.py <verilog_file>

Example:
    python rtk_conn_by_comment.py my_design.v
    python rtk_conn_by_comment.py top.v

Input Format Examples
--------------------
Wire type signals:
    wire my_input;         // realtekshane wire
    wire [7:0] my_output;  // realtekshane wire

Port type signals:
    input enable;          // realtekshane port enable
    output [3:0] result;   // realtekshane port result

Output Format Examples
---------------------
For wire type signals:
Input:
    // realtek assign my_input = 1'b0;
    // realtek wire my_input

Output:
    // realtek wire my_output

For port type signals:
Input:
    // realtek input enable
    // realtek input result.[3:0]

Output:
    // realtek output enable
    // realtek assign enable = 1'd0;
    // realtek output result.[3:0]
    // realtek assign result = 4'd0;

Output File Structure
--------------------
The generated modified file will be organized into two sections:
    //===input===
    (All input signal realtek comments)
    
    //===output===
    (All output signal realtek comments)

The script outputs a table with the following columns:
- Signal Name: The name of the signal found in the comments
- Module: The module name extracted from instance comments
- Direction: Whether the signal is an input or output port
- Bits: Signal width (e.g., [4:0] = 5 bits, no brackets = 1 bit)
- New Comments: The new format that will be applied

Example output:
    Found signals and their properties:
    -------------------------------------------------------------------------
    Signal Name                     Module               Direction  Bits
    -------------------------------------------------------------------------
    s1_mc2_exp_hit_prot            mc_express_lane_top  input     1
                                                                  // realtek assign s1_mc2_exp_hit_prot = 1'b0;
                                                                  // realtek wire s1_mc2_exp_hit_prot
    enable_out                     test_module          output    1
                                                                  // realtek output enable_out
                                                                  // realtek assign enable_out = 1'd0;
    s1_mc2_qfifo_exp_cnt[4:0]      mc_express_lane_top  output    5
                                                                  // realtek wire s1_mc2_qfifo_exp_cnt

Notes
-----
- The script searches for signals marked with '// realtekshane wire' comments
- Module names are extracted from instance comments (xxx_inst.yyy -> xxx)
- Multiple spaces in the comment pattern are handled automatically
- If a signal is not found in any module, it will be marked as "Not found"
- Bit width is calculated from signal declarations ([high:low] or single bit)

Author: Verilog Signal Analysis Tool
Version: 1.0
"""

import re
import os
import sys
import tempfile
import shutil

def calculate_bits(bit_range):
    """
    Calculate number of bits from a Verilog bit range.
    
    Args:
        bit_range (str): Bit range like [4:0] or [127:0] or None
        
    Returns:
        int: Number of bits (e.g., [4:0] = 5 bits, None = 1 bit)
    """
    if not bit_range:
        return 1
        
    match = re.match(r'\[(\d+):(\d+)\]', bit_range)
    if match:
        high = int(match.group(1))
        low = int(match.group(2))
        return high - low + 1
    return 1

def find_signal_info(verilog_file):
    """Find all signals and their properties."""
    results = []
    found_comments = []
    not_found_declarations = []
    
    try:
        with open(verilog_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # Process realtekshane wire - allow flexible spacing
                wire_pattern = r'//\s*realtekshane\s+wire'
                if re.search(wire_pattern, line):
                    signal_match = re.search(r'wire\s+(?:\[\d+:\d+\])?\s*(\w+)', line)
                    if signal_match:
                        signal_name = signal_match.group(1)
                        found_comments.append((line_num, signal_name, "wire"))
                        
                        # Find corresponding port declaration
                        found_declaration = False
                        with open(verilog_file, 'r', encoding='utf-8') as f2:
                            for port_line in f2:
                                if signal_name in port_line and '//' in port_line:
                                    is_input = 'input' in port_line
                                    is_output = 'output' in port_line
                                    
                                    if not (is_input or is_output):
                                        continue
                                    
                                    bit_match = re.search(r'\[(\d+):(\d+)\]', port_line)
                                    if bit_match:
                                        high = int(bit_match.group(1))
                                        low = int(bit_match.group(2))
                                        bit_width = high - low + 1
                                    else:
                                        bit_width = 1
                                        
                                    # Accept both xxx_inst. format and UDC format
                                    comment_match = re.search(r'//.*?(\w+)_inst\.', port_line)
                                    if comment_match:
                                        module_name = comment_match.group(1)
                                    elif '// UDC' in port_line:
                                        module_name = "UDC"
                                    else:
                                        continue
                                        
                                    direction = "input" if is_input else "output"
                                    results.append((line_num, signal_name, module_name, direction, bit_width, "wire"))
                                    found_declaration = True
                                    break
                        
                        if not found_declaration:
                            not_found_declarations.append((line_num, signal_name, "wire"))
                
                # Process realtekshane port - allow flexible spacing
                port_pattern = r'//\s*realtekshane\s+port\s+(\w+)'
                port_match = re.search(port_pattern, line)
                if port_match:
                    signal_name = port_match.group(1)
                    found_comments.append((line_num, signal_name, "port"))
                    
                    # Find corresponding port declaration
                    found_declaration = False
                    with open(verilog_file, 'r', encoding='utf-8') as f2:
                        for port_line in f2:
                            if signal_name in port_line and '//' in port_line:
                                is_input = 'input' in port_line
                                is_output = 'output' in port_line
                                
                                if not (is_input or is_output):
                                    continue
                                
                                bit_match = re.search(r'\[(\d+):(\d+)\]', port_line)
                                if bit_match:
                                    high = int(bit_match.group(1))
                                    low = int(bit_match.group(2))
                                    bit_width = high - low + 1
                                else:
                                    bit_width = 1
                                    
                                # Accept both xxx_inst. format and UDC format
                                comment_match = re.search(r'//.*?(\w+)_inst\.', port_line)
                                if comment_match:
                                    module_name = comment_match.group(1)
                                elif '// UDC' in port_line:
                                    module_name = "UDC"
                                else:
                                    continue
                                    
                                direction = "input" if is_input else "output"
                                results.append((line_num, signal_name, module_name, direction, bit_width, "port"))
                                found_declaration = True
                                break
                    
                    if not found_declaration:
                        not_found_declarations.append((line_num, signal_name, "port"))
        
        # Print diagnostic information
        if found_comments:
            print(f"\nFound {len(found_comments)} comment(s) with 'realtekshane' pattern:")
            for line_num, signal_name, comment_type in found_comments:
                print(f"  Line {line_num}: // realtekshane {comment_type} {signal_name}")
        
        if not_found_declarations:
            print(f"\nWARNING: Found {len(not_found_declarations)} signal(s) with comments but no corresponding input/output declarations:")
            for line_num, signal_name, comment_type in not_found_declarations:
                print(f"  Line {line_num}: Signal '{signal_name}' (from // realtekshane {comment_type}) - no input/output declaration found")
            print("\nPossible reasons:")
            print("1. The signal name in the comment doesn't match the actual signal declaration")
            print("2. The signal is not declared as input/output in the current file")
            print("3. The input/output declaration doesn't have a comment (// xxx_inst.yyy or // UDC)")
            print("4. The signal declaration format is different from expected")
        
        if results:
            print(f"\nSuccessfully matched {len(results)} signal(s) with their declarations.")
        
        return results, found_comments, not_found_declarations
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)

def modify_file(verilog_file, signal_info):
    """Create a new modified version of the file with new comment format."""
    base_name = os.path.splitext(verilog_file)[0]
    output_file = f"{base_name}_modified.v"
    
    # Group signals by direction and type
    input_signals = {"wire": [], "port": []}
    output_signals = {"wire": [], "port": []}
    
    for info in signal_info:
        if info[3] == "input":  # info[3] is direction
            input_signals[info[5]].append(info)  # info[5] is type (wire/port)
        else:
            output_signals[info[5]].append(info)
    
    try:
        with open(output_file, 'w', encoding='utf-8') as out_f:
            # Write input signal comments with header
            out_f.write("//===input===\n")
            # Process wire type inputs
            for _, signal_name, _, _, bit_width, _ in input_signals["wire"]:
                out_f.write(f"// realtek assign {signal_name} = {bit_width}'b0;\n")
                out_f.write(f"// realtek wire {signal_name}\n")
            # Process port type inputs
            for _, signal_name, _, _, bit_width, _ in input_signals["port"]:
                bit_suffix = f".[{bit_width-1}:0]" if bit_width > 1 else ""
                out_f.write(f"// realtek input {signal_name}{bit_suffix}\n")
            
            # Write output signal comments with header
            out_f.write("\n//===output===\n")
            # Process wire type outputs
            for _, signal_name, _, _, _, _ in output_signals["wire"]:
                out_f.write(f"// realtek wire {signal_name}\n")
            # Process port type outputs
            for _, signal_name, _, _, bit_width, _ in output_signals["port"]:
                bit_suffix = f".[{bit_width-1}:0]" if bit_width > 1 else ""
                out_f.write(f"// realtek output {signal_name}{bit_suffix}\n")
                out_f.write(f"// realtek assign {signal_name} = {bit_width}'d0;\n")
        
        print(f"\nModified file has been saved as: {output_file}")
        
    except Exception as e:
        print(f"Error creating modified file: {e}")
        if os.path.exists(output_file):
            os.unlink(output_file)
        sys.exit(1)

def main():
    """Main function to process Verilog file and modify comments."""
    if len(sys.argv) != 2:
        print("Error: Please provide the Verilog file path")
        print("Usage: python rtk_conn_by_comment.py <verilog_file>")
        print("\nExamples:")
        print("  python rtk_conn_by_comment.py design.v")
        print("  python rtk_conn_by_comment.py my_top.v")
        print("\nInput Format Example:")
        print("  input my_input;    // realtekshane port my_input")
        print("  output [3:0] my_output;  // realtekshane port my_output")
        print("  wire my_wire;      // realtekshane wire")
        print("\nNote: Input file must be a Verilog file (.v)")
        print("      The script will search for signals with '// realtekshane wire' or '// realtekshane port' comments")
        print("      and convert them to appropriate realtek format")
        sys.exit(1)
        
    verilog_file = sys.argv[1]
    if not verilog_file.endswith('.v'):
        print("Error: Input file must be a Verilog file (.v)")
        sys.exit(1)
        
    if not os.path.exists(verilog_file):
        print(f"Error: File '{verilog_file}' not found.")
        sys.exit(1)
    
    # Find all signal information with diagnostic info
    signal_info, found_comments, not_found_declarations = find_signal_info(verilog_file)
    
    if not found_comments:
        print("No 'realtekshane wire' or 'realtekshane port' comments found in the file.")
        print("\nPlease check that your comments follow one of these formats:")
        print("  // realtekshane wire")
        print("  // realtekshane port signal_name")
        sys.exit(0)
    
    if not signal_info:
        print("\nNo signals could be processed. Please check the warnings above.")
        sys.exit(0)
    
    # Show what will be modified
    print("\nThe following signals will be processed:")
    print("-" * 120)
    print(f"{'Signal Name':<30} {'Module':<20} {'Direction':<10} {'Bits':<6} {'New Comments'}")
    print("-" * 120)
    
    for _, signal_name, module_name, direction, bit_width, signal_type in signal_info:
        print(f"{signal_name:<30} {module_name:<20} {direction:<10} {bit_width:<6}")
        if direction == "input":
            if signal_type == "wire":
                assign_comment = f"// realtek assign {signal_name} = {bit_width}'b0;"
                wire_comment = f"// realtek wire {signal_name}"
                print(f"{'':30} {'':20} {'':10} {'':6} {assign_comment}")
                print(f"{'':30} {'':20} {'':10} {'':6} {wire_comment}")
            else:  # port
                bit_suffix = f".[{bit_width-1}:0]" if bit_width > 1 else ""
                input_comment = f"// realtek input {signal_name}{bit_suffix}"
                print(f"{'':30} {'':20} {'':10} {'':6} {input_comment}")
        else:  # output
            if signal_type == "wire":
                wire_comment = f"// realtek wire {signal_name}"
                print(f"{'':30} {'':20} {'':10} {'':6} {wire_comment}")
            else:  # port
                bit_suffix = f".[{bit_width-1}:0]" if bit_width > 1 else ""
                output_comment = f"// realtek output {signal_name}{bit_suffix}"
                assign_comment = f"// realtek assign {signal_name} = {bit_width}'d0;"
                print(f"{'':30} {'':20} {'':10} {'':6} {output_comment}")
                print(f"{'':30} {'':20} {'':10} {'':6} {assign_comment}")
    
    # Create modified version of the file
    modify_file(verilog_file, signal_info)

if __name__ == "__main__":
    main()
