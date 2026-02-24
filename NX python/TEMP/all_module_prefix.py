#!/usr/bin/env python3
import os
import re
from pathlib import Path

def find_module_name_in_verilog(file_path):
    """
    Extract module name from Verilog file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Match module keyword followed by module name
        # Support formats: module name, module name(, module name #(
        module_pattern = r'module\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[#(;]'
        matches = re.findall(module_pattern, content, re.IGNORECASE)
        
        if matches:
            return matches[0]  # Return first found module name
        else:
            return None
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def replace_module_name_with_filename(file_path, old_module_name, new_module_name):
    """
    Replace module name with filename in Verilog file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace module declaration
        module_pattern = r'(module\s+)' + re.escape(old_module_name) + r'(\s*[#(;])'
        new_content = re.sub(module_pattern, r'\1' + new_module_name + r'\2', content, flags=re.IGNORECASE)
        
        # Replace endmodule comment if exists
        endmodule_pattern = r'(endmodule\s*//\s*)' + re.escape(old_module_name) + r'(\s*$)'
        new_content = re.sub(endmodule_pattern, r'\1' + new_module_name + r'\2', new_content, flags=re.MULTILINE | re.IGNORECASE)
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
    except Exception as e:
        print(f"Error modifying file {file_path}: {e}")
        return False

def check_filename_module_consistency(root_dir, fix_mode=False):
    """
    Check if filename and module name are consistent for all .v files
    If fix_mode is True, automatically fix mismatches
    """
    root_path = Path(root_dir)
    
    if not root_path.exists():
        print(f"Directory {root_dir} does not exist")
        return
    
    # Recursively find all .v files
    v_files = list(root_path.rglob("*.v"))
    
    if not v_files:
        print(f"No .v files found in {root_dir}")
        return
    
    print(f"Found {len(v_files)} .v files")
    if fix_mode:
        print("FIX MODE: Will automatically rename module names to match filenames")
    print("=" * 60)
    
    consistent_count = 0
    inconsistent_count = 0
    error_count = 0
    fixed_count = 0
    
    for v_file in v_files:
        # Get filename without extension
        filename = v_file.stem
        
        # Get module name
        module_name = find_module_name_in_verilog(v_file)
        
        # Get relative path
        relative_path = v_file.relative_to(root_path)
        
        if module_name is None:
            print(f"ERROR: {relative_path}")
            print(f"   Cannot find module name")
            error_count += 1
        elif filename == module_name:
            print(f"OK: {relative_path}")
            print(f"   Filename and module name match: {filename}")
            consistent_count += 1
        else:
            print(f"MISMATCH: {relative_path}")
            print(f"   Filename: {filename}")
            print(f"   Module name: {module_name}")
            
            if fix_mode:
                if replace_module_name_with_filename(v_file, module_name, filename):
                    print(f"   FIXED: Module name changed to {filename}")
                    fixed_count += 1
                else:
                    print(f"   FAILED to fix")
                    error_count += 1
            else:
                inconsistent_count += 1
        
        print()
    
    # Summary
    print("=" * 60)
    print("Check results summary:")
    print(f"OK: {consistent_count} files")
    if fix_mode:
        print(f"FIXED: {fixed_count} files")
        if inconsistent_count > 0:
            print(f"FAILED to fix: {inconsistent_count} files")
    else:
        print(f"MISMATCH: {inconsistent_count} files")
    print(f"ERROR: {error_count} files")
    print(f"TOTAL: {len(v_files)} files")

def main():
    """
    Main function
    """
    # Use current directory
    root_directory = "."
    
    print(f"Checking directory: {os.path.abspath(root_directory)}")
    print()
    print("Choose mode:")
    print("1. Check only (default)")
    print("2. Check and fix mismatches")
    
    choice = input("Enter choice (1 or 2): ").strip()
    fix_mode = choice == "2"
    
    print("=" * 60)
    
    check_filename_module_consistency(root_directory, fix_mode)

if __name__ == "__main__":
    main()