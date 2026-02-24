#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Verilog Module Port Wire Prefixer Tool

This script processes Verilog files containing dcmc_tchk_pbk and dcmc_tchk_rank modules,
automatically adding IP_NAME parameter prefixes to all wire connections.

Purpose:
- Extracts IP_NAME parameters from module instances (e.g., "MC0RK0", "MC1RK0", etc.)
- Adds the extracted IP_NAME as a prefix to each wire name in port connections
- Prefixes are added with backtick (`) for hierarchical references
- Example: Changes .mi_cmd_org (mi_cmd_org) to .mi_cmd_org (`MC3RK1.mi_cmd_org)

Usage:
    python module_wire_name_prefixer.py input.v output.v --custom-prefix "MY_PREFIX"

Arguments:
    input.v   - Source Verilog file to process
    output.v  - Output file where the modified Verilog code will be written
    --custom-prefix  - (Optional) Use a custom prefix instead of the IP_NAME parameter value

Limitations:
- Only processes modules starting with 'dcmc_tchk' (e.g., dcmc_tchk_pbk, dcmc_tchk_rank)
- Assumes each port connection follows the format .port_name (wire_name)
- Does not handle complex expressions or nested module instantiations
- Will only modify wire connections that match the exact pattern expected
- Requires the IP_NAME parameter to be defined in the module instantiation

Author: User
Date: 2023
"""

import re
import sys
import argparse

def process_verilog_file(input_file, output_file, custom_prefix=None):
    try:
        # Read the input Verilog file
        with open(input_file, 'r') as f:
            verilog_text = f.read()
        
        # Find all instances with their IP_NAME parameters
        # Updated pattern to match both dcmc_tchk_pbk and dcmc_tchk_rank modules
        
        # NOTE: If you want to process ANY module with IP_NAME parameter (not just dcmc_tchk_*),
        # you can modify the pattern below to:
        # pattern = r'(\w+)\s+#\(\s*\.IP_NAME\("([^"]+)"\)\s*\)\s*(\S+)'
        # This will match any module name with an IP_NAME parameter.
        pattern = r'(dcmc_tchk_\w+)\s+#\(\s*\.IP_NAME\("([^"]+)"\)\s*\)\s*(\S+)'
        instances = re.findall(pattern, verilog_text)
        
        modified_text = verilog_text
        
        print(f"Processing file: {input_file}")
        print(f"Found {len(instances)} instances")
        
        if custom_prefix:
            print(f"Using custom prefix '{custom_prefix}' for all modules")
        
        # Process each instance
        for module_type, ip_name, instance_name in instances:
            print(f"Processing instance: {instance_name} of type {module_type} with IP_NAME: {ip_name}")
            
            # Create a regex to match this instance's port connections
            port_pattern = fr'({re.escape(instance_name)}\s*\().*?\);'
            instance_match = re.search(port_pattern, modified_text, re.DOTALL)
            
            if not instance_match:
                print(f"  Could not find instance block for {instance_name}")
                continue
                
            instance_block = instance_match.group(0)
            start_pos = instance_match.start()
            end_pos = instance_match.end()
            
            # Find all port connections in this block
            port_connections = re.findall(r'\.([\w_]+)\s+\(\s*([\w_]+)\s*\)', instance_block)
            
            if not port_connections:
                print(f"  No port connections found for {instance_name}")
                continue
                
            print(f"  Found {len(port_connections)} port connections")
            
            # Create a modified block with wire names prefixed by IP_NAME
            modified_block = instance_block
            for port, wire in port_connections:
                print(f"    Port: {port}, Wire: {wire}")
                
                # Use a more precise pattern to replace
                # Adding the IP_NAME prefix with backtick
                wire_pattern = fr'\.{port}\s+\(\s*{wire}\s*\)'
                replacement = f".{port} (`{custom_prefix}.{wire})"
                
                modified_block = re.sub(wire_pattern, replacement, modified_block)
            
            # Check if changes were made
            if modified_block == instance_block:
                print(f"  WARNING: No changes made to instance {instance_name}")
            else:
                print(f"  Successfully modified instance {instance_name}")
                
                # Replace the block in the original text
                modified_text = modified_text[:start_pos] + modified_block + modified_text[end_pos:]
        
        # Write the modified code to output file
        with open(output_file, 'w') as f:
            f.write(modified_text)
        
        print(f"Successfully processed. Output written to: {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Add prefixes to wire names in Verilog module port connections.')
    parser.add_argument('input_file', help='Source Verilog file to process')
    parser.add_argument('output_file', help='Output file where the modified Verilog code will be written')
    parser.add_argument('--custom-prefix', help='Use a custom prefix instead of IP_NAME parameter')
    
    args = parser.parse_args()
    
    process_verilog_file(args.input_file, args.output_file, args.custom_prefix)
