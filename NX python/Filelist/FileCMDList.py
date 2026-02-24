#!/usr/bin/env python3

"""
README:
This script executes a specified command in each directory from the path list.

Usage:
    python FileCMDList.py "<command>" <path_list_file>

Example:
    python FileCMDList.py 'grep "pass" test.log' paths.list
    python FileCMDList.py "find . -name '*.py'" directories.txt

Notes:
    - Each line in the path list file should contain a valid directory path
    - Environment variables in paths will be expanded (e.g., $HOME, %USERPROFILE%)
    - The script will skip directories that don't exist
    - Command output will be displayed for each directory
"""

import os
import sys
import subprocess

def expand_path(path):
    """Expand environment variables in path."""
    return os.path.expandvars(path)

def execute_command(command, path_list_file):
    original_dir = os.getcwd()
    
    # Check if path list file exists
    path_list_file = expand_path(path_list_file)
    if not os.path.exists(path_list_file):
        print("Error: Path list file '{}' does not exist".format(path_list_file))
        sys.exit(1)
    
    # Read the path list file
    try:
        with open(path_list_file, 'r') as f:
            paths = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print("Error reading path list file: {}".format(e))
        sys.exit(1)
    
    # Execute command for each path
    for path in paths:
        try:
            target_path = expand_path(path)
            if not os.path.exists(target_path):
                print("Warning: Path '{}' does not exist, skipping".format(target_path))
                continue
                
            os.chdir(target_path)
            
            # Execute the command
            print("Executing in {}: {}".format(target_path, command))
            # Use shell=True to properly handle commands with quotes
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            # Print command output
            if result.stdout:
                print("Output:\n{}".format(result.stdout))
            
            if result.returncode != 0:
                print("Command failed with return code {}".format(result.returncode))
                if result.stderr:
                    print("Error:\n{}".format(result.stderr))
        
        except Exception as e:
            print("Error processing {}: {}".format(path, e))
        finally:
            os.chdir(original_dir)

def main():
    if len(sys.argv) != 3:
        print("Usage: python FileCMDList.py \"<command>\" <path_list_file>")
        print("Example: python FileCMDList.py 'grep \"pass\" test.log' paths.list")
        sys.exit(1)
    
    command = sys.argv[1]
    path_list_file = sys.argv[2]
    
    execute_command(command, path_list_file)

if __name__ == "__main__":
    main()



