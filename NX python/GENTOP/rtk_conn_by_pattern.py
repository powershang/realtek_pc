#!/usr/bin/env python3.11
"""
Verilog Port Connection Analyzer and Realtek Script Generator (Pattern-Based)

This script generates Realtek scripts by searching for specific port patterns in Verilog files.
Key features:
- Searches ports based on pattern matching (e.g., "dfi_*", "mc_*")
- Supports input, output, inout, and wire port types
- Generates Realtek wire declarations or connection scripts
- Supports both single-bit and bus-width signals

Usage:
    python rtk_conn_by_pattern.py <verilog_file_path> <port_types> <direction> "<pattern1>" ["<pattern2>" ...]

Port Types:
    Comma-separated list of: input, output, inout, wire

Direction:
    wire: Generate connection scripts (receive port)
    io: Generate input/output declarations (send port)

Examples:
    python rtk_conn_by_pattern.py design.v output wire "dfi_*"
    # Generate connection scripts for output ports matching "dfi_*" (receive port)

    python rtk_conn_by_pattern.py design.v input,output io "mc_*" "dfi_*"
    # Generate input/output declarations for input/output ports matching "mc_*" or "dfi_*" (send port)

    python rtk_conn_by_pattern.py design.v inout wire "*_data"
    # Generate connection scripts for inout ports matching "*_data" (receive port)

Note:
    Make sure to use quotes around patterns containing wildcards (*,?)
    Wrong:  python rtk_conn_by_pattern.py design.v output dfi_*
    Right:  python rtk_conn_by_pattern.py design.v output "dfi_*"
"""

import re
import sys
from fnmatch import fnmatch
import os

def parse_bus_width(bus_width_str):
    """
    Convert bus width string [N:0] to decimal number
    Example: [2:0] -> 3
    """
    if not bus_width_str:
        return 1
    match = re.match(r'\[(\d+):(\d+)\]', bus_width_str)
    if match:
        high = int(match.group(1))
        low = int(match.group(2))
        return high - low + 1
    return 1

def parse_port_definition(line):
    """
    Parse port definition line to extract wire_name and ports
    Example: 
    wire signal_name;    // module1_inst.port1 module2_inst.port2
    output [31:0] dc_mc3_secu_rbus_ack;    // dc2_mc_top_wrap_inst.rbus_mc_sec_ack
    input [31:0] signal_name;    // module1_inst.port1 module2_inst.port2
    inout [31:0] signal_name;    // module1_inst.port1 module2_inst.port2
    """
    parts = line.split('//')
    if len(parts) != 2:
        return None, None
    
    wire_part = parts[0].strip()
    # Handle wire, input, output, or inout declarations
    if line.startswith('wire'):
        wire_name = re.sub(r'^\s*wire\s*(\[\d+:\d+\])?\s*', '', wire_part)
    else:
        wire_name = re.sub(r'^\s*(input|output|inout)\s*(\[\d+:\d+\])?\s*', '', wire_part)
    
    wire_name = wire_name.rstrip(';')
    comment = parts[1].strip()
    connections = comment.split()
    
    return wire_name, connections

def generate_conn_script(inst_name, port_name, port_type=None, bus_width_str=None):
    """
    Generate realtek connection script for receive port
    """
    module_name = inst_name[:-5] if inst_name.endswith('_inst') else inst_name
    
    if port_type == 'input':
        # For input ports, generate conn statement with default value
        width = parse_bus_width(bus_width_str) if bus_width_str else 1
        return [f'// realtek conn {module_name}.{port_name} {width}\'d0']
    else:
        # For output, inout, and wire, use connection format
        return [f'// realtek conn {module_name}.{port_name} ""']

def generate_rtk_script(wire_name, port_type, direction, bus_width_str):
    """
    Generate realtek script based on port type and direction
    direction: 'wire' for connection scripts, 'io' for input/output declarations
    """
    width = parse_bus_width(bus_width_str)
    width_str = f"[{width-1}:0]" if width > 1 else ""
    
    if direction == 'io':  # Send port - use wire/input/output declarations
        if port_type == 'input':
            return [f"// realtek input {wire_name}{width_str}"]
        elif port_type == 'output':
            return [f"// realtek output {wire_name}{width_str}"]
        else:  # inout
            return [f"// realtek inout {wire_name}{width_str}"]
    
    # For direction == 'wire' (receive port), we'll use connection scripts
    # This will be handled differently in the main logic
    return []

def analyze_ports(file_path, port_types, direction, signal_patterns):
    """
    Analyze ports in Verilog file
    port_types: list of types to analyze ('input', 'output', 'inout', 'wire')
    direction: 'wire' for connection scripts, 'io' for input/output declarations
    signal_patterns: list of patterns to match signal names
    """
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found!")
        return False

    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    # Group results by module for io direction, or store connection scripts for wire direction
    module_conn_scripts = {}
    module_connections = {}
    
    for line in lines:
        line = line.strip()
        # Original wire handling
        if line.startswith('wire'):
            wire_pattern = r'^\s*wire\s+(\[[\d:]+\])?\s*(\w+)\s*;?\s*\/\/\s*(.*)$'
            match = re.match(wire_pattern, line)
            if match:
                bus_width_str = match.group(1)
                wire_name = match.group(2)
                connection_info = match.group(3)
                
                for pattern in signal_patterns:
                    if fnmatch(wire_name, pattern):
                        print("\n=== Wire Analysis Results ===")
                        print(f"\nWire: {wire_name}")
                        if bus_width_str:
                            print(f"Bus Width: {bus_width_str} ({parse_bus_width(bus_width_str)} bits)")
                        
                        # Extract instance names from comment
                        instances = []
                        for part in connection_info.split():
                            if '.' in part:
                                inst_name, port_name = part.split('.')
                                instances.append((inst_name, port_name))
                        
                        if instances:
                            print("Connections:")
                            print("\nConnection Details:")
                            for inst_name, port_name in instances:
                                print(f"  - {inst_name}.{port_name} (wire)")
                            
                            # Handle based on direction
                            if direction == 'wire':  # Receive port - use connection format
                                if 'wire' not in module_connections:
                                    module_connections['wire'] = []
                                for inst_name, port_name in instances:
                                    module_connections['wire'].extend(generate_conn_script(inst_name, port_name, 'wire', bus_width_str))
                            else:  # io direction
                                for inst_name, port_name in instances:
                                    module_name = inst_name[:-5] if inst_name.endswith('_inst') else inst_name
                                    if module_name not in module_conn_scripts:
                                        module_conn_scripts[module_name] = []
                                    module_conn_scripts[module_name].extend(
                                        generate_rtk_script(port_name, 'wire', direction, bus_width_str)
                                    )
                        else:
                            print(f"Warning: Found matching wire '{wire_name}' but no connection information found in comment: '{connection_info}'")
                            print("Expected format: wire signal_name; // module_inst.port_name")
                        break
        
        # Add input/output/inout handling
        elif line.startswith(('input', 'output', 'inout')):
            if line.startswith('input'):
                port_type = 'input'
            elif line.startswith('output'):
                port_type = 'output'
            else:
                port_type = 'inout'
                
            if port_type in port_types:
                port_pattern = r'^\s*(input|output|inout)\s+(\[[\d:]+\])?\s*(\w+)\s*;?\s*\/\/\s*(.*)$'
                match = re.match(port_pattern, line)
                if match:
                    bus_width_str = match.group(2)
                    port_name = match.group(3)      # Use this directly for realtek wire/assign
                    connection_info = match.group(4)
                    
                    for pattern in signal_patterns:
                        if fnmatch(port_name, pattern):
                            print(f"\n=== {port_type.capitalize()} Analysis Results ===")
                            print(f"\nPort: {port_name}")
                            if bus_width_str:
                                print(f"Bus Width: {bus_width_str} ({parse_bus_width(bus_width_str)} bits)")
                            
                            # Extract instance names from comment
                            instances = []
                            for part in connection_info.split():
                                if '.' in part:
                                    inst_name, conn_port = part.split('.')
                                    instances.append((inst_name, conn_port))
                            
                            if instances:
                                print("Connections:")
                                print("\nConnection Details:")
                                for inst_name, conn_port in instances:
                                    print(f"  - {inst_name}.{conn_port} ({port_type})")
                                
                                # Handle based on direction
                                if direction == 'wire':  # Receive port - use connection format
                                    if port_type not in module_connections:
                                        module_connections[port_type] = []
                                    for inst_name, conn_port in instances:
                                        module_connections[port_type].extend(generate_conn_script(inst_name, conn_port, port_type, bus_width_str))
                                else:  # io direction
                                    # For io direction, use the port name directly for all port types
                                    if 'direct' not in module_conn_scripts:
                                        module_conn_scripts['direct'] = []
                                    module_conn_scripts['direct'].extend(
                                        generate_rtk_script(port_name, port_type, direction, bus_width_str)
                                    )
                            else:
                                print(f"Warning: Found matching {port_type} port '{port_name}' but no connection information found in comment: '{connection_info}'")
                                print(f"Expected format: {port_type} signal_name; // module_inst.port_name")
                            break
    
    # Print results based on direction
    if direction == 'wire':  # Receive port - print connection scripts
        if module_connections:
            print("\n=== All Realtek Connection Scripts ===")
            
            for port_type in ['input', 'output', 'inout', 'wire']:
                if port_type in module_connections and port_type in port_types:
                    print(f"\n//=={port_type}==")
                    for connection in sorted(module_connections[port_type]):
                        print(connection)
    
    else:  # io direction - print input/output declarations
        if module_conn_scripts:
            print("\n=== All Realtek Conn Scripts ===")
            
            # Print input scripts first
            if 'input' in port_types:
                print("\n//==input==")
                for module_name in sorted(module_conn_scripts.keys()):
                    input_scripts = []
                    for script in sorted(module_conn_scripts[module_name]):
                        if script.startswith("// realtek input"):
                            input_scripts.append(script)
                    if input_scripts:
                        print(f"\n// Module: {module_name}")
                        for script in input_scripts:
                            print(script)
            
            # Then print output scripts
            if 'output' in port_types:
                print("\n//==output==")
                for module_name in sorted(module_conn_scripts.keys()):
                    output_scripts = []
                    for script in sorted(module_conn_scripts[module_name]):
                        if script.startswith("// realtek output") or script.startswith("// realtek assign"):
                            output_scripts.append(script)
                    if output_scripts:
                        print(f"\n// Module: {module_name}")
                        for script in output_scripts:
                            print(script)
            
            # Finally print inout scripts
            if 'inout' in port_types:
                print("\n//==inout==")
                for module_name in sorted(module_conn_scripts.keys()):
                    inout_scripts = []
                    for script in sorted(module_conn_scripts[module_name]):
                        if script.startswith("// realtek inout"):
                            inout_scripts.append(script)
                    if inout_scripts:
                        print(f"\n// Module: {module_name}")
                        for script in inout_scripts:
                            print(script)
    
    return True

def main():
    if len(sys.argv) < 5:
        print("Error: Please provide the Verilog file path, port types, direction, and at least one pattern")
        print("\nUsage:")
        print("  python rtk_conn_by_pattern.py <verilog_file_path> <port_types> <direction> \"<pattern1>\" [\"<pattern2>\" ...]")
        print("\nPort Types:")
        print("  Comma-separated list of: input, output, inout, wire")
        print("\nDirection:")
        print("  wire: Generate connection scripts (receive port)")
        print("  io: Generate input/output declarations (send port)")
        print("\nExamples:")
        print("  python rtk_conn_by_pattern.py design.v output wire \"dfi_*\"")
        print("  python rtk_conn_by_pattern.py design.v input,output io \"mc_*\" \"dfi_*\"")
        print("  python rtk_conn_by_pattern.py design.v inout wire \"*_data\"")
        print("\nNote: Make sure to use quotes around patterns containing wildcards (*,?)")
        sys.exit(1)
    
    verilog_file = sys.argv[1]
    port_types = sys.argv[2].split(',')
    direction = sys.argv[3]
    signal_patterns = sys.argv[4:]
    
    if direction not in ['wire', 'io']:
        print("Error: Direction must be either 'wire' or 'io'")
        sys.exit(1)
    
    analyze_ports(verilog_file, port_types, direction, signal_patterns)

if __name__ == "__main__":
    main()
