#!/usr/bin/env python3.11
"""
Merge DPI Pad Generator

Uses module_chk_port_diff.py to find new inout signals and generates:
- .name(name) connection statements
- wire name; declarations
- assign name = 1'b1; for signals containing vcc/vdd
- assign name = 1'b0; for signals containing gnd

Also removes old ports that no longer exist and adds new ports:
- Remove .old_port(.old_port) from file A
- Remove wire old_port from file B  
- Remove assign old_port = 1/0 from file C
- Add .new_port(new_port) to file A (if not exists)
- Add wire new_port to file B (if not exists)
- Add assign new_port = 1/0 to file C (if not exists)

Usage:
    python merge_dpi_pad.py <new_file.v> <old_file.v>

Example:
    python merge_dpi_pad.py merlin10.v merlin10_raw.v
"""

import sys
import os
import re
import module_chk_port_diff

# Configure file paths here using environment variable
FILE_A_PATH = "$PROJECT_HOME/verification/system/top_port_wrap.vh"      # File with .port(.port) connections
FILE_B_PATH = "$PROJECT_HOME/verification/system/top_port_declare.vh"   # File with wire declarations  
FILE_C_PATH = "$PROJECT_HOME/verification/system/top_power_pad.vh"      # File with assign statements

def get_expanded_path(path):
    """
    Expand environment variables in path
    """
    return os.path.expandvars(path)

def find_new_inout_ports(new_file, old_file):
    """
    Find new inout signals that exist in new_file but not in old_file
    """
    print("=== Analyzing new inout signals ===\n")
    
    # Extract ports from both files using imported module
    new_ports = module_chk_port_diff.extract_module_ports(new_file)
    old_ports = module_chk_port_diff.extract_module_ports(old_file)
    
    if new_ports is None or old_ports is None:
        return []
    
    # Find ports that only exist in new file (new ports to add)
    new_port_names = set(new_ports.keys()) - set(old_ports.keys())
    
    # Filter out inout type new ports
    new_inout_ports = []
    for port_name in new_port_names:
        direction, bit_width, bus_width_str = new_ports[port_name]
        if direction == 'inout':
            new_inout_ports.append((port_name, direction, bit_width, bus_width_str))
    
    return new_inout_ports

def find_old_ports_to_remove(new_file, old_file):
    """
    Find ports that exist in old_file but not in new_file (old ports to remove)
    """
    print("=== Analyzing old ports to remove ===\n")
    
    # Extract ports from both files
    new_ports = module_chk_port_diff.extract_module_ports(new_file)
    old_ports = module_chk_port_diff.extract_module_ports(old_file)
    
    if new_ports is None or old_ports is None:
        return []
    
    # Find ports that only exist in old file (old ports to remove)
    old_port_names = set(old_ports.keys()) - set(new_ports.keys())
    
    old_ports_list = []
    for port_name in old_port_names:
        direction, bit_width, bus_width_str = old_ports[port_name]
        old_ports_list.append((port_name, direction, bit_width, bus_width_str))
    
    return old_ports_list

def remove_old_connections(file_path, old_port_names):
    """
    Remove .old_port(.old_port) connections from file A
    """
    expanded_path = get_expanded_path(file_path)
    
    if not os.path.exists(expanded_path):
        print(f"Warning: File {expanded_path} not found, skipping connection removal")
        return
    
    try:
        with open(expanded_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        lines_removed = 0
        
        # Remove connection lines for each old port
        for port_name in old_port_names:
            # Pattern to match .port_name(port_name), or .port_name(port_name)
            pattern = rf'^\s*\.{re.escape(port_name)}\s*\(\s*{re.escape(port_name)}\s*\)\s*,?\s*$'
            lines = content.split('\n')
            new_lines = []
            
            for line in lines:
                if not re.match(pattern, line):
                    new_lines.append(line)
                else:
                    lines_removed += 1
                    print(f"  Removed connection: {line.strip()}")
            
            content = '\n'.join(new_lines)
        
        # Write back if changes made
        if content != original_content:
            with open(expanded_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated {expanded_path}: removed {lines_removed} connection lines")
        else:
            print(f"No connection changes needed in {expanded_path}")
            
    except Exception as e:
        print(f"Error processing {expanded_path}: {e}")

def remove_old_wires(file_path, old_port_names):
    """
    Remove wire old_port declarations from file B
    """
    expanded_path = get_expanded_path(file_path)
    
    if not os.path.exists(expanded_path):
        print(f"Warning: File {expanded_path} not found, skipping wire removal")
        return
    
    try:
        with open(expanded_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        lines_removed = 0
        
        # Remove wire declarations for each old port
        for port_name in old_port_names:
            # Pattern to match wire [bus] port_name;
            pattern = rf'^\s*wire\s+(?:\[[^\]]+\]\s+)?{re.escape(port_name)}\s*;\s*$'
            lines = content.split('\n')
            new_lines = []
            
            for line in lines:
                if not re.match(pattern, line):
                    new_lines.append(line)
                else:
                    lines_removed += 1
                    print(f"  Removed wire: {line.strip()}")
            
            content = '\n'.join(new_lines)
        
        # Write back if changes made
        if content != original_content:
            with open(expanded_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated {expanded_path}: removed {lines_removed} wire lines")
        else:
            print(f"No wire changes needed in {expanded_path}")
            
    except Exception as e:
        print(f"Error processing {expanded_path}: {e}")

def remove_old_assigns(file_path, old_port_names):
    """
    Remove assign old_port = 1/0 statements from file C
    """
    expanded_path = get_expanded_path(file_path)
    
    if not os.path.exists(expanded_path):
        print(f"Warning: File {expanded_path} not found, skipping assign removal")
        return
    
    try:
        with open(expanded_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        lines_removed = 0
        
        # Remove assign statements for each old port
        for port_name in old_port_names:
            # Pattern to match assign port_name = 1'b0 or 1'b1 or 1'h0 or 1'h1;
            pattern = rf'^\s*assign\s+{re.escape(port_name)}\s*=\s*1\'[bh][01]\s*;\s*$'
            lines = content.split('\n')
            new_lines = []
            
            for line in lines:
                if not re.match(pattern, line):
                    new_lines.append(line)
                else:
                    lines_removed += 1
                    print(f"  Removed assign: {line.strip()}")
            
            content = '\n'.join(new_lines)
        
        # Write back if changes made
        if content != original_content:
            with open(expanded_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated {expanded_path}: removed {lines_removed} assign lines")
        else:
            print(f"No assign changes needed in {expanded_path}")
            
    except Exception as e:
        print(f"Error processing {expanded_path}: {e}")

def add_new_connections(file_path, new_inout_ports):
    """
    Add .new_port(new_port) connections to file A (only if not already exists)
    """
    expanded_path = get_expanded_path(file_path)
    
    if not os.path.exists(expanded_path):
        print(f"Warning: File {expanded_path} not found, skipping connection addition")
        return
    
    if not new_inout_ports:
        return
    
    try:
        with open(expanded_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check which connections already exist
        existing_ports = []
        new_ports_to_add = []
        
        for port_name, direction, bit_width, bus_width_str in new_inout_ports:
            # Check if connection already exists
            pattern = rf'^\s*\.{re.escape(port_name)}\s*\(\s*{re.escape(port_name)}\s*\)\s*,?\s*$'
            if re.search(pattern, content, re.MULTILINE):
                existing_ports.append(port_name)
                print(f"  Connection already exists: .{port_name}({port_name})")
            else:
                new_ports_to_add.append((port_name, direction, bit_width, bus_width_str))
        
        # Generate new connection lines for ports that don't exist
        if new_ports_to_add:
            new_connections = []
            for port_name, direction, bit_width, bus_width_str in new_ports_to_add:
                new_connections.append(f"    .{port_name}({port_name}),")
            
            # Add new connections at the end of file
            content += "\n// New inout connections:\n"
            content += "\n".join(new_connections) + "\n"
            
            with open(expanded_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Updated {expanded_path}: added {len(new_connections)} connection lines")
            for line in new_connections:
                print(f"  Added connection: {line.strip()}")
        else:
            print(f"No new connections to add to {expanded_path}")
        
    except Exception as e:
        print(f"Error processing {expanded_path}: {e}")

def add_new_wires(file_path, new_inout_ports):
    """
    Add wire new_port declarations to file B (only if not already exists)
    """
    expanded_path = get_expanded_path(file_path)
    
    if not os.path.exists(expanded_path):
        print(f"Warning: File {expanded_path} not found, skipping wire addition")
        return
    
    if not new_inout_ports:
        return
    
    try:
        with open(expanded_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check which wire declarations already exist
        existing_ports = []
        new_ports_to_add = []
        
        for port_name, direction, bit_width, bus_width_str in new_inout_ports:
            # Check if wire declaration already exists
            pattern = rf'^\s*wire\s+(?:\[[^\]]+\]\s+)?{re.escape(port_name)}\s*;\s*$'
            if re.search(pattern, content, re.MULTILINE):
                existing_ports.append(port_name)
                print(f"  Wire already exists: wire {port_name};")
            else:
                new_ports_to_add.append((port_name, direction, bit_width, bus_width_str))
        
        # Generate new wire declarations for ports that don't exist
        if new_ports_to_add:
            new_wires = []
            for port_name, direction, bit_width, bus_width_str in new_ports_to_add:
                if bus_width_str:
                    new_wires.append(f"wire {bus_width_str} {port_name};")
                else:
                    new_wires.append(f"wire {port_name};")
            
            # Add new wire declarations at the end of file
            content += "\n// New inout wire declarations:\n"
            content += "\n".join(new_wires) + "\n"
            
            with open(expanded_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Updated {expanded_path}: added {len(new_wires)} wire lines")
            for line in new_wires:
                print(f"  Added wire: {line.strip()}")
        else:
            print(f"No new wires to add to {expanded_path}")
        
    except Exception as e:
        print(f"Error processing {expanded_path}: {e}")

def add_new_assigns(file_path, new_inout_ports):
    """
    Add assign new_port = 1/0 statements to file C (only for vcc/vdd/gnd ports and if not already exists)
    """
    expanded_path = get_expanded_path(file_path)
    
    if not os.path.exists(expanded_path):
        print(f"Warning: File {expanded_path} not found, skipping assign addition")
        return
    
    if not new_inout_ports:
        return
    
    try:
        with open(expanded_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check which assign statements already exist for vcc/vdd/gnd ports
        existing_ports = []
        new_ports_to_add = []
        
        for port_name, direction, bit_width, bus_width_str in new_inout_ports:
            if 'vcc' in port_name.lower() or 'vdd' in port_name.lower() or 'gnd' in port_name.lower():
                # Check if assign statement already exists (match both 1'b and 1'h)
                pattern = rf'^\s*assign\s+{re.escape(port_name)}\s*=\s*1\'[bh][01]\s*;\s*$'
                if re.search(pattern, content, re.MULTILINE):
                    existing_ports.append(port_name)
                    print(f"  Assign already exists: assign {port_name} = 1'b?;")
                else:
                    new_ports_to_add.append((port_name, direction, bit_width, bus_width_str))
        
        # Generate new assign statements for vcc/vdd/gnd ports that don't exist
        if new_ports_to_add:
            new_assigns = []
            for port_name, direction, bit_width, bus_width_str in new_ports_to_add:
                if 'vcc' in port_name.lower() or 'vdd' in port_name.lower():
                    new_assigns.append(f"assign {port_name} = 1'b1;")
                elif 'gnd' in port_name.lower():
                    new_assigns.append(f"assign {port_name} = 1'b0;")
            
            # Add new assign statements at the end of file
            if new_assigns:
                content += "\n// New inout assign statements:\n"
                content += "\n".join(new_assigns) + "\n"
                
                with open(expanded_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"Updated {expanded_path}: added {len(new_assigns)} assign lines")
                for line in new_assigns:
                    print(f"  Added assign: {line.strip()}")
            else:
                print(f"No new assigns to add to {expanded_path}")
        else:
            print(f"No new assign statements needed for {expanded_path} (no new vcc/vdd/gnd ports or already exist)")
        
    except Exception as e:
        print(f"Error processing {expanded_path}: {e}")

def generate_verilog_code(new_inout_ports):
    """
    Generate Verilog code for new inout ports
    """
    if not new_inout_ports:
        print("No new inout signals found")
        return
    
    print(f"=== Found {len(new_inout_ports)} new inout signals ===\n")
    
    # Generate code
    connection_lines = []
    wire_declarations = []
    assign_statements = []
    
    for port_name, direction, bit_width, bus_width_str in new_inout_ports:
        print(f"  {direction} {bus_width_str if bus_width_str else ''} {port_name} ({bit_width} bits)")
        
        # Generate connection statement .name(name)
        connection_lines.append(f"    .{port_name}({port_name}),")
        
        # Generate wire declaration
        if bus_width_str:
            wire_declarations.append(f"wire {bus_width_str} {port_name};")
        else:
            wire_declarations.append(f"wire {port_name};")
        
        # Generate assign statements based on name
        if 'vcc' in port_name.lower() or 'vdd' in port_name.lower():
            assign_statements.append(f"assign {port_name} = 1'b1;")
        elif 'gnd' in port_name.lower():
            assign_statements.append(f"assign {port_name} = 1'b0;")
    
    # Output generated code
    print("\n=== Generated Verilog Code ===\n")
    
    print("// Module connection statements:")
    for line in connection_lines:
        print(line)
    
    print("\n// Wire declarations:")
    for line in wire_declarations:
        print(line)
    
    if assign_statements:
        print("\n// Assign statements:")
        for line in assign_statements:
            print(line)
    
    # Save to file
    output_file = "generated_inout_code.v"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("// Generated Verilog code for new inout ports\n\n")
            
            f.write("// Module connections:\n")
            for line in connection_lines:
                f.write(line + "\n")
            
            f.write("\n// Wire declarations:\n")
            for line in wire_declarations:
                f.write(line + "\n")
            
            if assign_statements:
                f.write("\n// Assign statements:\n")
                for line in assign_statements:
                    f.write(line + "\n")
        
        print(f"\n=== Code saved to {output_file} ===")
        
    except Exception as e:
        print(f"Error writing to {output_file}: {e}")

def main():
    # Check if PROJECT_HOME environment variable is set
    if 'PROJECT_HOME' not in os.environ:
        print("Error: PROJECT_HOME environment variable is not set!")
        print("Please set PROJECT_HOME before running this script")
        sys.exit(1)
    
    if len(sys.argv) != 3:
        print("Error: Please provide two Verilog file paths")
        print("\nUsage:")
        print("  python merge_dpi_pad.py <new_file.v> <old_file.v>")
        print("\nExample:")
        print("  python merge_dpi_pad.py merlin10.v merlin10_raw.v")
        print(f"\nConfigured file paths:")
        print(f"  PROJECT_HOME: {os.environ.get('PROJECT_HOME', 'NOT SET')}")
        print(f"  File A (connections): {get_expanded_path(FILE_A_PATH)}")
        print(f"  File B (wires): {get_expanded_path(FILE_B_PATH)}")
        print(f"  File C (assigns): {get_expanded_path(FILE_C_PATH)}")
        sys.exit(1)
    
    new_file = sys.argv[1]  # merlin10.v (has new ports)
    old_file = sys.argv[2]  # merlin10_raw.v (has old ports)
    
    print(f"PROJECT_HOME: {os.environ['PROJECT_HOME']}")
    print(f"New file (merlin10.v): {new_file}")
    print(f"Old file (merlin10_raw.v): {old_file}")
    print(f"File A: {get_expanded_path(FILE_A_PATH)}")
    print(f"File B: {get_expanded_path(FILE_B_PATH)}")
    print(f"File C: {get_expanded_path(FILE_C_PATH)}\n")
    
    # Find new inout ports (in new_file but not in old_file)
    new_inout_ports = find_new_inout_ports(new_file, old_file)
    
    # Find old ports to remove (in old_file but not in new_file)
    old_ports_to_remove = find_old_ports_to_remove(new_file, old_file)
    
    # Generate Verilog code for new ports
    generate_verilog_code(new_inout_ports)
    
    # Remove old ports from files A, B, C
    if old_ports_to_remove:
        print(f"\n=== Found {len(old_ports_to_remove)} old ports to remove ===\n")
        
        old_port_names = [port[0] for port in old_ports_to_remove]
        for port_name, direction, bit_width, bus_width_str in old_ports_to_remove:
            print(f"  {direction} {bus_width_str if bus_width_str else ''} {port_name} ({bit_width} bits)")
        
        print(f"\n=== Removing old ports from configured files ===\n")
        
        # Remove from file A (connections)
        print(f"Processing File A: {get_expanded_path(FILE_A_PATH)}")
        remove_old_connections(FILE_A_PATH, old_port_names)
        
        # Remove from file B (wires)
        print(f"\nProcessing File B: {get_expanded_path(FILE_B_PATH)}")
        remove_old_wires(FILE_B_PATH, old_port_names)
        
        # Remove from file C (assigns)
        print(f"\nProcessing File C: {get_expanded_path(FILE_C_PATH)}")
        remove_old_assigns(FILE_C_PATH, old_port_names)
        
    else:
        print("\n=== No old ports to remove ===")
    
    # Add new ports to files A, B, C (only if not already exists)
    if new_inout_ports:
        print(f"\n=== Adding {len(new_inout_ports)} new ports to configured files ===\n")
        
        # Add to file A (connections)
        print(f"Processing File A: {get_expanded_path(FILE_A_PATH)}")
        add_new_connections(FILE_A_PATH, new_inout_ports)
        
        # Add to file B (wires)
        print(f"\nProcessing File B: {get_expanded_path(FILE_B_PATH)}")
        add_new_wires(FILE_B_PATH, new_inout_ports)
        
        # Add to file C (assigns) - only for vcc/vdd/gnd ports
        print(f"\nProcessing File C: {get_expanded_path(FILE_C_PATH)}")
        add_new_assigns(FILE_C_PATH, new_inout_ports)
        
    else:
        print("\n=== No new ports to add ===")

if __name__ == "__main__":
    main()
