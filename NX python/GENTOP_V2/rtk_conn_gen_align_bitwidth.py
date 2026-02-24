#!/usr/bin/env python3
"""
Verilog Module Port Alignment with Realtek Annotations Generator

This script compares the ports between two Verilog files, allows user to choose 
alignment target, and generates realtek annotations for port differences.

Features:
- Compare ports between two Verilog files
- Interactive selection of alignment target (align to file A or file B)
- Generate realtek annotations for missing ports
- Support for input/output port direction handling

Usage:
    python rtk_conn_gen_align_bitwidth.py <file1.v> <file2.v>

Example:
    python rtk_conn_gen_align_bitwidth.py aaa.v bbb.v

Based on module_chk_port_diff.py and enhanced with realtek annotation generation.
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
                break
    
    return ports

def extract_module_name(file_path):
    """
    Extract module name from Verilog file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None
    
    # Find module definition
    module_pattern = r'module\s+(\w+)\s*\('
    module_match = re.search(module_pattern, content)
    
    if module_match:
        return module_match.group(1)
    return None

def compare_ports(file1, file2):
    """
    Compare ports between two Verilog files and return differences
    Returns: (ports1, ports2, only_in_file1, only_in_file2, different_common_ports)
    """
    print(f"=== Comparing ports between {file1} and {file2} ===\n")
    
    # Extract ports from both files
    ports1 = extract_module_ports(file1)
    ports2 = extract_module_ports(file2)
    
    if ports1 is None or ports2 is None:
        return None, None, None, None, None
    
    print(f"\n=== Port Comparison Results ===")
    print(f"File 1 ({file1}): {len(ports1)} ports")
    print(f"File 2 ({file2}): {len(ports2)} ports")
    
    # Find differences
    only_in_file1 = set(ports1.keys()) - set(ports2.keys())
    only_in_file2 = set(ports2.keys()) - set(ports1.keys())
    
    # Common ports with differences
    common_ports = set(ports1.keys()) & set(ports2.keys())
    different_common_ports = []
    
    for port in common_ports:
        dir1, width1, bus_str1 = ports1[port]
        dir2, width2, bus_str2 = ports2[port]
        
        if dir1 != dir2 or width1 != width2:
            different_common_ports.append(port)
    
    # Display differences
    differences_found = False
    
    if only_in_file1:
        differences_found = True
        print(f"\n=== Ports only in {file1} ===")
        for port in sorted(only_in_file1):
            direction, bit_width, bus_width_str = ports1[port]
            width_str = f"{bus_width_str}" if bus_width_str else ""
            print(f"  {direction:<7} {width_str:<10} {port:<30} ({bit_width} bits)")
    
    if only_in_file2:
        differences_found = True
        print(f"\n=== Ports only in {file2} ===")
        for port in sorted(only_in_file2):
            direction, bit_width, bus_width_str = ports2[port]
            width_str = f"{bus_width_str}" if bus_width_str else ""
            print(f"  {direction:<7} {width_str:<10} {port:<30} ({bit_width} bits)")
    
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
        return ports1, ports2, only_in_file1, only_in_file2, different_common_ports
    else:
        total_diffs = len(only_in_file1) + len(only_in_file2) + len(different_common_ports)
        print(f"Found {total_diffs} port differences:")
        if only_in_file1:
            print(f"  - {len(only_in_file1)} ports only in {file1}")
        if only_in_file2:
            print(f"  - {len(only_in_file2)} ports only in {file2}")
        if different_common_ports:
            print(f"  - {len(different_common_ports)} common ports with differences")
    
    return ports1, ports2, only_in_file1, only_in_file2, different_common_ports

def get_user_choice(file1, file2):
    """
    Get user's choice for alignment target
    """
    print(f"\n=== Alignment Options ===")
    print(f"1. Align to {file1} (make {file2} ports match {file1})")
    print(f"2. Align to {file2} (make {file1} ports match {file2})")
    
    while True:
        try:
            choice = input("\nEnter your choice (1 or 2): ").strip()
            if choice in ['1', '2']:
                return int(choice)
            else:
                print("Please enter 1 or 2")
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            sys.exit(0)
        except EOFError:
            print("\nOperation cancelled.")
            sys.exit(0)

def extract_instance_name_from_file(file_path, module_name):
    """
    Extract instance name from Verilog file by finding module instantiation
    
    Args:
        file_path: Verilog file path to search in
        module_name: Module name to find instantiation for
    
    Returns:
        Instance name (without _inst suffix if exists)
    """
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found!")
        return module_name  # fallback to module name
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return module_name  # fallback to module name
    
    # Find module instantiation pattern: module_name instance_name (
    inst_pattern = rf'{re.escape(module_name)}\s+(\w+)\s*\('
    inst_match = re.search(inst_pattern, content)
    
    if inst_match:
        instance_name = inst_match.group(1)
        print(f"Found instance: {instance_name} of module {module_name}")
        
        # Remove common suffixes like _inst, _u, etc.
        if instance_name.endswith('_inst'):
            instance_name = instance_name[:-5]  # Remove '_inst'
        elif instance_name.endswith('_u'):
            instance_name = instance_name[:-2]  # Remove '_u'
        
        return instance_name
    else:
        print(f"No instantiation found for module {module_name}, using module name")
        return module_name  # fallback to module name

def extract_pin_to_port_mapping_from_file(file_path):
    """
    Extract pin-to-port mapping from Verilog file by finding all .pin_name(signal_name) patterns
    
    Args:
        file_path: Verilog file path to search in
    
    Returns:
        Dictionary mapping signal_name -> pin_name
    """
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found!")
        return {}

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return {}
    
    signal_to_pin_mapping = {}
    
    # Find all .pin_name(signal_name) patterns in the file
    pin_pattern = r'\.(\w+)\s*\(\s*([^)]+)\s*\)'
    pin_matches = re.findall(pin_pattern, content)
    
    print(f"Searching for .pin_name(signal_name) patterns in {file_path}")
    
    for pin_name, signal_name in pin_matches:
        # Clean up signal name (remove spaces, comments)
        signal_name = signal_name.strip().split('//')[0].strip()
        
        # Skip empty signal names or comments
        if not signal_name or signal_name.startswith('//'):
            continue
            
        signal_to_pin_mapping[signal_name] = pin_name
        print(f"  Found mapping: signal '{signal_name}' -> pin '{pin_name}'")
    
    return signal_to_pin_mapping

def extract_instance_and_pin_mapping(file_path, module_name):
    """
    Extract instance name and pin-to-port mapping for a specific module instantiation
    
    Args:
        file_path: Verilog file path to search in
        module_name: Module name to find instantiation for
    
    Returns:
        Tuple: (instance_name, signal_to_pin_mapping)
    """
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found!")
        return module_name, {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return module_name, {}
    
    signal_to_pin_mapping = {}
    instance_name = module_name  # fallback
    
    # Find module instantiation pattern: module_name instance_name (
    inst_pattern = rf'{re.escape(module_name)}\s+(\w+)\s*\('
    inst_match = re.search(inst_pattern, content)
    
    if inst_match:
        full_instance_name = inst_match.group(1)
        start_pos = inst_match.end() - 1  # Position of opening parenthesis
        
        print(f"Found instance: {full_instance_name} of module {module_name}")
        
        # Remove common suffixes like _inst, _u, etc.
        if full_instance_name.endswith('_inst'):
            instance_name = full_instance_name[:-5]  # Remove '_inst'
        elif full_instance_name.endswith('_u'):
            instance_name = full_instance_name[:-2]  # Remove '_u'
        else:
            instance_name = full_instance_name
        
        print(f"Using instance name: {instance_name}")
        
        # Find the complete instantiation block for this specific instance
        paren_count = 0
        end_pos = start_pos
        for i, char in enumerate(content[start_pos:], start_pos):
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
                if paren_count == 0:
                    end_pos = i + 1
                    break
        
        if end_pos > start_pos:
            inst_block = content[start_pos:end_pos]
            
            # Extract pin connections: .pin_name(signal_name) from this specific instance
            pin_pattern = r'\.(\w+)\s*\(\s*([^)]+)\s*\)'
            pin_matches = re.findall(pin_pattern, inst_block)
            
            print(f"Found {len(pin_matches)} pin connections for instance {full_instance_name}:")
            
            for pin_name, signal_name in pin_matches:
                # Clean up signal name (remove spaces, comments)
                signal_name = signal_name.strip().split('//')[0].strip()
                
                # Skip empty signal names or comments
                if not signal_name or signal_name.startswith('//'):
                    continue
                
                signal_to_pin_mapping[signal_name] = pin_name
                print(f"  {full_instance_name}: signal '{signal_name}' -> pin '{pin_name}'")
    else:
        print(f"No instantiation found for module {module_name}, using module name")
    
    return instance_name, signal_to_pin_mapping

def extract_all_instances_and_pin_mapping(file_path):
    """
    Extract all instances and pin-to-port mappings from all module instantiations
    Look for pattern: module_name instance_name_inst (...) 
    
    Args:
        file_path: Verilog file path to search in
    
    Returns:
        List of tuples: [(instance_name, signal_to_pin_mapping), ...]
    """
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found!")
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return []
    
    instances_info = []
    
    # Find all module instantiation patterns: any_module_name any_instance_name (
    # Look specifically for patterns ending with _inst
    inst_pattern = r'(\w+)\s+(\w+_inst)\s*\('
    inst_matches = re.finditer(inst_pattern, content)
    
    for inst_match in inst_matches:
        module_name = inst_match.group(1)
        full_instance_name = inst_match.group(2)
        start_pos = inst_match.end() - 1  # Position of opening parenthesis
        
        print(f"Found instance: {full_instance_name} of module {module_name}")
        
        # Remove _inst suffix to get clean instance name
        if full_instance_name.endswith('_inst'):
            instance_name = full_instance_name[:-5]  # Remove '_inst'
        else:
            instance_name = full_instance_name
        
        print(f"Using instance name: {instance_name}")
        
        # Find the complete instantiation block for this specific instance
        paren_count = 0
        end_pos = start_pos
        for i, char in enumerate(content[start_pos:], start_pos):
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
                if paren_count == 0:
                    end_pos = i + 1
                    break
        
        if end_pos > start_pos:
            inst_block = content[start_pos:end_pos]
            signal_to_pin_mapping = {}
            
            # Extract pin connections: .pin_name(signal_name) from this specific instance
            pin_pattern = r'\.(\w+)\s*\(\s*([^)]+)\s*\)'
            pin_matches = re.findall(pin_pattern, inst_block)
            
            print(f"Found {len(pin_matches)} pin connections for instance {full_instance_name}:")
            
            for pin_name, signal_name in pin_matches:
                # Clean up signal name (remove spaces, comments)
                signal_name = signal_name.strip().split('//')[0].strip()
                
                # Skip empty signal names or comments
                if not signal_name or signal_name.startswith('//'):
                    continue
                
                signal_to_pin_mapping[signal_name] = pin_name
                print(f"  {full_instance_name}: signal '{signal_name}' -> pin '{pin_name}'")
            
            instances_info.append((instance_name, signal_to_pin_mapping))
    
    if not instances_info:
        print(f"No instantiations found with pattern xxx_inst")
    
    return instances_info

def generate_realtek_annotations_with_bitwidth_mismatch(target_file, ports_only_in_target, ports_only_in_source, 
                                                       different_common_ports, target_ports, source_ports, instance_name, signal_to_pin_mapping=None):
    """
    Generate realtek annotations for port alignment including bitwidth mismatch handling
    
    Args:
        target_file: Target file name (the one being aligned to)
        ports_only_in_target: Set of port names that exist only in target
        ports_only_in_source: Set of port names that exist only in source
        different_common_ports: List of port names with differences (direction or bitwidth)
        target_ports: Ports in target file
        source_ports: Ports in source file
        instance_name: Instance name for conn annotations (e.g., dpi_dll_top_wrap)
        signal_to_pin_mapping: Dictionary mapping signal_name -> pin_name (optional)
    
    Returns:
        List of annotation strings
    """
    annotations = []
    
    if not ports_only_in_target and not ports_only_in_source and not different_common_ports:
        return annotations
    
    # Use provided signal-to-pin mapping or empty dict
    if signal_to_pin_mapping is None:
        signal_to_pin_mapping = {}
    
    annotations.append(f"// ===== Realtek Annotations for aligning to {target_file} =====")
    annotations.append(f"// Instance name: {instance_name}")
    annotations.append("")
    
    # Process ports only in target (need input/output declarations)
    if ports_only_in_target:
        annotations.append("// ===== Ports only in target - need input/output declarations =====")
        
        input_ports = []
        output_ports = []
        inout_ports = []
        
        for port in sorted(ports_only_in_target):
            direction, bit_width, bus_width_str = target_ports[port]
            
            if direction == 'input':
                input_ports.append((port, direction, bit_width, bus_width_str))
            elif direction == 'output':
                output_ports.append((port, direction, bit_width, bus_width_str))
            elif direction == 'inout':
                inout_ports.append((port, direction, bit_width, bus_width_str))
        
        # Generate input declarations
        if input_ports:
            annotations.append("// Input port declarations:")
            for port, direction, bit_width, bus_width_str in input_ports:
                if bit_width > 1:
                    range_str = f"[{bit_width-1}:0]"
                    annotations.append(f"// realtek input {port}.{range_str}")
                else:
                    annotations.append(f"// realtek input {port}")
            annotations.append("")
        
        # Generate output declarations
        if output_ports:
            annotations.append("// Output port declarations:")
            for port, direction, bit_width, bus_width_str in output_ports:
                if bit_width > 1:
                    range_str = f"[{bit_width-1}:0]"
                    annotations.append(f"// realtek output {port}.{range_str}")
                else:
                    annotations.append(f"// realtek output {port}")
            annotations.append("")
        
        # Generate inout declarations
        if inout_ports:
            annotations.append("// Inout port declarations:")
            for port, direction, bit_width, bus_width_str in inout_ports:
                if bit_width > 1:
                    range_str = f"[{bit_width-1}:0]"
                    annotations.append(f"// realtek inout {port}.{range_str}")
                else:
                    annotations.append(f"// realtek inout {port}")
            annotations.append("")
    
    # Process ports only in source (need conn annotations)
    if ports_only_in_source:
        annotations.append("// ===== Ports only in source - need conn annotations =====")
        
        input_ports = []
        output_ports = []
        inout_ports = []
        
        for port in sorted(ports_only_in_source):
            direction, bit_width, bus_width_str = source_ports[port]
            
            if direction == 'input':
                input_ports.append((port, direction, bit_width, bus_width_str))
            elif direction == 'output':
                output_ports.append((port, direction, bit_width, bus_width_str))
            elif direction == 'inout':
                inout_ports.append((port, direction, bit_width, bus_width_str))
        
        # Generate conn annotations for input ports
        if input_ports:
            annotations.append("// Input port connections:")
            for port, direction, bit_width, bus_width_str in input_ports:
                # Use pin name if mapping exists, otherwise use port name as pin name
                pin_name = signal_to_pin_mapping.get(port, port)
                annotations.append(f"// realtek conn {instance_name}.{pin_name} {bit_width}'d0")
            annotations.append("")
        
        # Generate conn annotations for output ports
        if output_ports:
            annotations.append("// Output port connections:")
            for port, direction, bit_width, bus_width_str in output_ports:
                # Use pin name if mapping exists, otherwise use port name as pin name
                pin_name = signal_to_pin_mapping.get(port, port)
                annotations.append(f'// realtek conn {instance_name}.{pin_name} ""')
            annotations.append("")
        
        # Generate conn annotations for inout ports
        if inout_ports:
            annotations.append("// Inout port connections:")
            for port, direction, bit_width, bus_width_str in inout_ports:
                # Use pin name if mapping exists, otherwise use port name as pin name
                pin_name = signal_to_pin_mapping.get(port, port)
                annotations.append(f"// realtek conn {instance_name}.{pin_name} {bit_width}'d0")
            annotations.append("")
    
    # Process common ports with bitwidth/direction differences
    if different_common_ports:
        annotations.append("// ===== Common ports with bitwidth/direction mismatch =====")
        
        input_mismatch_ports = []
        output_mismatch_ports = []
        inout_mismatch_ports = []
        
        for port in sorted(different_common_ports):
            # Use target port definition for alignment
            target_direction, target_bit_width, target_bus_width_str = target_ports[port]
            source_direction, source_bit_width, source_bus_width_str = source_ports[port]
            
            if target_direction == 'input':
                input_mismatch_ports.append((port, target_direction, target_bit_width, target_bus_width_str))
            elif target_direction == 'output':
                output_mismatch_ports.append((port, target_direction, target_bit_width, target_bus_width_str))
            elif target_direction == 'inout':
                inout_mismatch_ports.append((port, target_direction, target_bit_width, target_bus_width_str))
        
        # Generate annotations for input ports with mismatch
        if input_mismatch_ports:
            annotations.append("// Input ports with bitwidth mismatch:")
            for port, direction, bit_width, bus_width_str in input_mismatch_ports:
                # Use pin name if mapping exists, otherwise use port name as pin name
                pin_name = signal_to_pin_mapping.get(port, port)
                # First tie the port
                annotations.append(f"// realtek conn {instance_name}.{pin_name} {bit_width}'d0")
                # Then declare with target bitwidth
                if bit_width > 1:
                    range_str = f"[{bit_width-1}:0]"
                    annotations.append(f"// realtek input {port}.{range_str}")
                else:
                    annotations.append(f"// realtek input {port}")
            annotations.append("")
        
        # Generate annotations for output ports with mismatch
        if output_mismatch_ports:
            annotations.append("// Output ports with bitwidth mismatch:")
            for port, direction, bit_width, bus_width_str in output_mismatch_ports:
                # Use pin name if mapping exists, otherwise use port name as pin name
                pin_name = signal_to_pin_mapping.get(port, port)
                # First tie the port
                annotations.append(f'// realtek conn {instance_name}.{pin_name} ""')
                # Then declare with target bitwidth
                if bit_width > 1:
                    range_str = f"[{bit_width-1}:0]"
                    annotations.append(f"// realtek output {port}.{range_str}")
                else:
                    annotations.append(f"// realtek output {port}")
            annotations.append("")
        
        # Generate annotations for inout ports with mismatch
        if inout_mismatch_ports:
            annotations.append("// Inout ports with bitwidth mismatch:")
            for port, direction, bit_width, bus_width_str in inout_mismatch_ports:
                # Use pin name if mapping exists, otherwise use port name as pin name
                pin_name = signal_to_pin_mapping.get(port, port)
                # First tie the port
                annotations.append(f"// realtek conn {instance_name}.{pin_name} {bit_width}'d0")
                # Then declare with target bitwidth
                if bit_width > 1:
                    range_str = f"[{bit_width-1}:0]"
                    annotations.append(f"// realtek inout {port}.{range_str}")
                else:
                    annotations.append(f"// realtek inout {port}")
            annotations.append("")
    
    return annotations

def generate_realtek_annotations_for_multiple_instances(target_file, ports_only_in_target, ports_only_in_source, 
                                                       different_common_ports, target_ports, source_ports, instances_info):
    """
    Generate realtek annotations for port alignment including bitwidth mismatch handling for multiple instances
    
    Args:
        target_file: Target file name (the one being aligned to)
        ports_only_in_target: Set of port names that exist only in target
        ports_only_in_source: Set of port names that exist only in source
        different_common_ports: List of port names with differences (direction or bitwidth)
        target_ports: Ports in target file
        source_ports: Ports in source file
        instances_info: List of (instance_name, signal_to_pin_mapping) tuples
    
    Returns:
        List of annotation strings
    """
    annotations = []
    
    if not ports_only_in_target and not ports_only_in_source and not different_common_ports:
        return annotations
    
    annotations.append(f"// ===== Realtek Annotations for aligning to {target_file} =====")
    if instances_info:
        instance_names = [info[0] for info in instances_info]
        annotations.append(f"// Found instances: {', '.join(instance_names)}")
    annotations.append("")
    
    # Process ports only in target (need input/output declarations)
    if ports_only_in_target:
        annotations.append("// ===== Ports only in target - need input/output declarations =====")
        
        input_ports = []
        output_ports = []
        inout_ports = []
        
        for port in sorted(ports_only_in_target):
            direction, bit_width, bus_width_str = target_ports[port]
            
            if direction == 'input':
                input_ports.append((port, direction, bit_width, bus_width_str))
            elif direction == 'output':
                output_ports.append((port, direction, bit_width, bus_width_str))
            elif direction == 'inout':
                inout_ports.append((port, direction, bit_width, bus_width_str))
        
        # Generate input declarations
        if input_ports:
            annotations.append("// Input port declarations:")
            for port, direction, bit_width, bus_width_str in input_ports:
                if bit_width > 1:
                    range_str = f"[{bit_width-1}:0]"
                    annotations.append(f"// realtek input {port}.{range_str}")
                else:
                    annotations.append(f"// realtek input {port}")
            annotations.append("")
        
        # Generate output declarations
        if output_ports:
            annotations.append("// Output port declarations:")
            for port, direction, bit_width, bus_width_str in output_ports:
                if bit_width > 1:
                    range_str = f"[{bit_width-1}:0]"
                    annotations.append(f"// realtek output {port}.{range_str}")
                else:
                    annotations.append(f"// realtek output {port}")
            annotations.append("")
        
        # Generate inout declarations
        if inout_ports:
            annotations.append("// Inout port declarations:")
            for port, direction, bit_width, bus_width_str in inout_ports:
                if bit_width > 1:
                    range_str = f"[{bit_width-1}:0]"
                    annotations.append(f"// realtek inout {port}.{range_str}")
                else:
                    annotations.append(f"// realtek inout {port}")
            annotations.append("")
    
    # Process ports only in source (need conn annotations for ALL instances)
    if ports_only_in_source:
        annotations.append("// ===== Ports only in source - need conn annotations =====")
        
        for instance_name, signal_to_pin_mapping in instances_info:
            # Only process ports that actually exist in this instance
            instance_has_ports = False
            
            input_ports = []
            output_ports = []
            inout_ports = []
            
            for port in sorted(ports_only_in_source):
                # Check if this port exists in this instance's mapping
                if port in signal_to_pin_mapping:
                    direction, bit_width, bus_width_str = source_ports[port]
                    
                    if direction == 'input':
                        input_ports.append((port, direction, bit_width, bus_width_str))
                        instance_has_ports = True
                    elif direction == 'output':
                        output_ports.append((port, direction, bit_width, bus_width_str))
                        instance_has_ports = True
                    elif direction == 'inout':
                        inout_ports.append((port, direction, bit_width, bus_width_str))
                        instance_has_ports = True
            
            # Only generate annotations when this instance actually has relevant ports
            if instance_has_ports:
                annotations.append(f"// Instance: {instance_name}")
                
                # Generate conn annotations for input ports
                if input_ports:
                    annotations.append("// Input port connections:")
                    for port, direction, bit_width, bus_width_str in input_ports:
                        # port is the signal name, get the actual pin name from mapping
                        pin_name = signal_to_pin_mapping[port]
                        annotations.append(f"// realtek conn {instance_name}.{pin_name} {bit_width}'d0")
                    annotations.append("")
                
                # Generate conn annotations for output ports
                if output_ports:
                    annotations.append("// Output port connections:")
                    for port, direction, bit_width, bus_width_str in output_ports:
                        # port is the signal name, get the actual pin name from mapping
                        pin_name = signal_to_pin_mapping[port]
                        annotations.append(f'// realtek conn {instance_name}.{pin_name} ""')
                    annotations.append("")
                
                # Generate conn annotations for inout ports
                if inout_ports:
                    annotations.append("// Inout port connections:")
                    for port, direction, bit_width, bus_width_str in inout_ports:
                        # port is the signal name, get the actual pin name from mapping
                        pin_name = signal_to_pin_mapping[port]
                        annotations.append(f"// realtek conn {instance_name}.{pin_name} {bit_width}'d0")
                    annotations.append("")
    
    # Process common ports with bitwidth/direction differences (for ALL instances)
    if different_common_ports:
        annotations.append("// ===== Common ports with bitwidth/direction mismatch =====")
        
        for instance_name, signal_to_pin_mapping in instances_info:
            # Only process ports that actually exist in this instance
            instance_has_ports = False
            
            input_mismatch_ports = []
            output_mismatch_ports = []
            inout_mismatch_ports = []
            
            for port in sorted(different_common_ports):
                # Check if this port exists in this instance's mapping
                # If port name exists as signal name in mapping, this instance has this port
                if port in signal_to_pin_mapping:
                    # Use target port definition for alignment
                    target_direction, target_bit_width, target_bus_width_str = target_ports[port]
                    source_direction, source_bit_width, source_bus_width_str = source_ports[port]
                    
                    if target_direction == 'input':
                        input_mismatch_ports.append((port, target_direction, target_bit_width, target_bus_width_str))
                        instance_has_ports = True
                    elif target_direction == 'output':
                        output_mismatch_ports.append((port, target_direction, target_bit_width, target_bus_width_str))
                        instance_has_ports = True
                    elif target_direction == 'inout':
                        inout_mismatch_ports.append((port, target_direction, target_bit_width, target_bus_width_str))
                        instance_has_ports = True
            
            # Only generate annotations when this instance actually has relevant ports
            if instance_has_ports:
                annotations.append(f"// Instance: {instance_name}")
                
                # Generate annotations for input ports with mismatch
                if input_mismatch_ports:
                    annotations.append("// Input ports with bitwidth mismatch:")
                    for port, direction, bit_width, bus_width_str in input_mismatch_ports:
                        pin_name = signal_to_pin_mapping[port]  # Must exist since we already checked
                        signal_name = port
                        
                        # Get source bitwidth for conn (original bitwidth to tie off)
                        source_direction, source_bit_width, source_bus_width_str = source_ports[port]
                        # bit_width is target bitwidth for input declaration
                        
                        # First tie the port using pin name with SOURCE bitwidth
                        annotations.append(f"// realtek conn {instance_name}.{pin_name} {source_bit_width}'d0")
                        # Then declare with TARGET bitwidth using signal name (port name)
                        if bit_width > 1:
                            range_str = f"[{bit_width-1}:0]"
                            annotations.append(f"// realtek input {signal_name}.{range_str}")
                        else:
                            annotations.append(f"// realtek input {signal_name}")
                    annotations.append("")
                
                # Generate annotations for output ports with mismatch
                if output_mismatch_ports:
                    annotations.append("// Output ports with bitwidth mismatch:")
                    for port, direction, bit_width, bus_width_str in output_mismatch_ports:
                        pin_name = signal_to_pin_mapping[port]  # Must exist
                        signal_name = port
                        
                        # Get source bitwidth for conn (original bitwidth to tie off)
                        source_direction, source_bit_width, source_bus_width_str = source_ports[port]
                        # bit_width is target bitwidth for output declaration
                        
                        # First tie the port using pin name (output ports use empty string)
                        annotations.append(f'// realtek conn {instance_name}.{pin_name} ""')
                        # Then declare with TARGET bitwidth using signal name (port name)
                        if bit_width > 1:
                            range_str = f"[{bit_width-1}:0]"
                            annotations.append(f"// realtek output {signal_name}.{range_str}")
                        else:
                            annotations.append(f"// realtek output {signal_name}")
                    annotations.append("")
                
                # Generate annotations for inout ports with mismatch
                if inout_mismatch_ports:
                    annotations.append("// Inout ports with bitwidth mismatch:")
                    for port, direction, bit_width, bus_width_str in inout_mismatch_ports:
                        pin_name = signal_to_pin_mapping[port]  # Must exist
                        signal_name = port
                        
                        # Get source bitwidth for conn (original bitwidth to tie off)
                        source_direction, source_bit_width, source_bus_width_str = source_ports[port]
                        # bit_width is target bitwidth for inout declaration
                        
                        # First tie the port using pin name with SOURCE bitwidth
                        annotations.append(f"// realtek conn {instance_name}.{pin_name} {source_bit_width}'d0")
                        # Then declare with TARGET bitwidth using signal name (port name)
                        if bit_width > 1:
                            range_str = f"[{bit_width-1}:0]"
                            annotations.append(f"// realtek inout {signal_name}.{range_str}")
                        else:
                            annotations.append(f"// realtek inout {signal_name}")
            annotations.append("")
    
    return annotations

def generate_realtek_annotations(source_file, target_file, source_ports, target_ports, 
                                 missing_ports, module_name):
    """
    Generate realtek annotations for missing ports (legacy function)
    
    Args:
        source_file: Source file name (the one being aligned to)
        target_file: Target file name (the one that needs alignment)
        source_ports: Ports in source file
        target_ports: Ports in target file
        missing_ports: Set of port names that exist in source but not in target
        module_name: Module name for annotations
    
    Returns:
        List of annotation strings
    """
    annotations = []
    
    if not missing_ports:
        return annotations
    
    annotations.append(f"// ===== Realtek Annotations for {target_file} =====")
    annotations.append(f"// Align {target_file} to match {source_file}")
    annotations.append(f"// Module: {module_name}")
    annotations.append("")
    
    # Separate by port direction
    input_ports = []
    output_ports = []
    inout_ports = []
    
    for port in sorted(missing_ports):
        direction, bit_width, bus_width_str = source_ports[port]
        
        if direction == 'input':
            input_ports.append((port, direction, bit_width, bus_width_str))
        elif direction == 'output':
            output_ports.append((port, direction, bit_width, bus_width_str))
        elif direction == 'inout':
            inout_ports.append((port, direction, bit_width, bus_width_str))
    
    # Generate annotations for input ports
    if input_ports:
        annotations.append("// ===== Input Port Annotations =====")
        for port, direction, bit_width, bus_width_str in input_ports:
            # For input ports: // realtek conn module.port N'd0
            annotations.append(f"// realtek conn {module_name}.{port} {bit_width}'d0")
        annotations.append("")
    
    # Generate annotations for output ports
    if output_ports:
        annotations.append("// ===== Output Port Annotations =====")
        for port, direction, bit_width, bus_width_str in output_ports:
            # For output ports: // realtek conn module.port ""
            annotations.append(f'// realtek conn {module_name}.{port} ""')
        annotations.append("")
    
    # Generate annotations for inout ports
    if inout_ports:
        annotations.append("// ===== Inout Port Annotations =====")
        for port, direction, bit_width, bus_width_str in inout_ports:
            # For inout ports: treat as input
            annotations.append(f"// realtek conn {module_name}.{port} {bit_width}'d0")
        annotations.append("")
    
    return annotations

def main():
    """Main function"""
    if len(sys.argv) != 3:
        print("Error: Please provide exactly two Verilog file paths")
        print("\nUsage:")
        print("  python rtk_conn_gen_align_bitwidth.py <file1.v> <file2.v>")
        print("\nExample:")
        print("  python rtk_conn_gen_align_bitwidth.py aaa.v bbb.v")
        print("\nThis script will:")
        print("  1. Compare ports between the two files")
        print("  2. Ask you to choose alignment target")
        print("  3. Generate realtek annotations for missing ports and bitwidth mismatches")
        print("  4. Automatically extract pin-to-port mapping for ALL instances")
        print("  5. Generate realtek conn for each instance separately")
        sys.exit(1)
    
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    
    # Compare ports
    ports1, ports2, only_in_file1, only_in_file2, different_common_ports = compare_ports(file1, file2)
    
    if ports1 is None or ports2 is None:
        sys.exit(1)
    
    # Check if there are any differences
    total_diffs = len(only_in_file1) + len(only_in_file2) + len(different_common_ports)
    if total_diffs == 0:
        print("\nNo differences found. No realtek annotations needed.")
        sys.exit(0)
    
    # Get user choice
    choice = get_user_choice(file1, file2)
    
    # Generate annotations based on choice
    if choice == 1:
        # Align to file1 - generate annotations for both directions
        target_file = file1
        ports_only_in_target = only_in_file1  # Ports only in file1 (target)
        ports_only_in_source = only_in_file2  # Ports only in file2 (source)
        target_ports = ports1
        source_ports = ports2
        search_file = file2  # Search for instantiation in source file (where ports_only_in_source exist)
    else:
        # Align to file2 - generate annotations for both directions
        target_file = file2
        ports_only_in_target = only_in_file2  # Ports only in file2 (target)
        ports_only_in_source = only_in_file1  # Ports only in file1 (source)
        target_ports = ports2
        source_ports = ports1
        search_file = file1  # Search for instantiation in source file (where ports_only_in_source exist)
    
    # Extract ALL instances and pin mappings from target file
    print(f"\n=== Extracting ALL instances and pin mappings from {search_file} ===")
    instances_info = extract_all_instances_and_pin_mapping(search_file)
    
    if instances_info:
        total_mappings = sum(len(mapping) for _, mapping in instances_info)
        print(f"Found {len(instances_info)} instances with total {total_mappings} signal-to-pin mappings")
    else:
        print(f"No instances found with pattern xxx_inst")
        # Create a dummy instance for fallback
        instances_info = [("unknown_instance", {})]
    
    # Generate realtek annotations with bitwidth mismatch handling for all instances
    annotations = generate_realtek_annotations_for_multiple_instances(
        target_file, ports_only_in_target, ports_only_in_source, different_common_ports,
        target_ports, source_ports, instances_info
    )
    
    # Output results
    print(f"\n=== Generated Realtek Annotations ===")
    if annotations:
        for annotation in annotations:
            print(annotation)
        
        # Ask if user wants to save to file
        while True:
            try:
                save_choice = input(f"\nSave annotations to file? (y/n): ").strip().lower()
                if save_choice in ['y', 'yes']:
                    # Use target file name for output
                    target_name = os.path.splitext(os.path.basename(target_file))[0]
                    output_file = f"{target_name}_realtek_annotations.txt"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(annotations))
                    print(f"Annotations saved to: {output_file}")
                    break
                elif save_choice in ['n', 'no']:
                    break
                else:
                    print("Please enter y or n")
            except (KeyboardInterrupt, EOFError):
                print("\nOperation cancelled.")
                break
    else:
        print("No annotations generated for the selected alignment.")

if __name__ == "__main__":
    main()
