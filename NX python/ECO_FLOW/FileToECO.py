#!/usr/bin/env python3
"""
SVN File Backup Tool

A Python utility for backing up modified files in SVN working directories and generating restore scripts.

Features:
- Automatically detects modified files in SVN working directory
- Creates backups of modified files in the specified directory
- Generates TCL restore scripts for easy file restoration
- Detailed logging with debug mode option
- Command-line interface for flexible usage

Basic usage:
    python FileToECO.py -o <output_directory>

Advanced usage with all options:
    python FileToECO.py -w <working_directory> -o <output_directory> -d

Command Line Arguments:
- -w, --work-dir: SVN working directory (default: current directory)
- -o, --output-dir: Output directory path for backup files (required)
- -d, --debug: Enable debug mode for detailed logging

How It Works:
1. The script checks for modified files in the specified SVN working directory
2. Copies all modified files directly to the specified output directory
3. Generates a TCL restore script that can be used to restore files if needed
4. Provides detailed logging of all operations

Output Structure:
    output_directory/
    |-- file1
    |-- file2
    |-- ...
    +-- restore_files_YYYYMMDD_HHMMSS.tcl

Logging:
- Default logging includes basic operation information
- Debug mode (-d) provides detailed logging of all operations
- Logs include timestamps and operation details

Error Handling:
- Comprehensive error handling for file operations
- Detailed error messages in debug mode
- Continues operation even if individual file operations fail

Notes:
- Maintains original file permissions during backup
- Preserves file timestamps
- Generates executable TCL restore scripts
- Safe to run multiple times (creates new restore scripts each time)

Author: shane
"""

import subprocess
import shutil
import os
import argparse
import logging
from datetime import datetime
import re

def setup_logging(debug_mode):
    log_level = logging.DEBUG if debug_mode else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)

def convert_path_to_env_var(path):
    """Convert path containing R4743 and its immediate subdirectory to use PROJECT_HOME environment variable"""
    if isinstance(path, str):
        # Match R4743 and the next directory level
        # This will match patterns like /path/to/R4743/subdirectory/rest/of/path
        return re.sub(r'.*?[/\\]R4743[/\\][^/\\]+[/\\]', '$PROJECT_HOME/', path.replace('\\', '/'))
    return path

def get_modified_files(work_dir, logger):
    """Execute 'svn st' command and get list of modified files"""
    try:
        logger.debug("Executing 'svn st' in directory: {}".format(work_dir))
        
        process = subprocess.Popen(['svn', 'st'], 
                                 cwd=work_dir,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        
        stdout_data, stderr_data = process.communicate()
        
        stdout = stdout_data.decode()
        stderr = stderr_data.decode()
        
        logger.debug("SVN command output:")
        logger.debug("STDOUT:\n{}".format(stdout))
        
        if process.returncode != 0:
            logger.error("SVN command failed with return code: {}".format(process.returncode))
            return []
        
        modified_files = []
        for line in stdout.split('\n'):
            logger.debug("Processing line: {}".format(line))
            if line.startswith('M '):
                file_path = line[2:].strip()
                # Keep original path format
                full_path = os.path.join(work_dir, file_path)
                # Convert path to use environment variable
                env_path = convert_path_to_env_var(full_path)
                logger.debug("Found modified file: {} (converted: {})".format(full_path, env_path))
                modified_files.append((env_path, file_path))
        
        logger.info("Found {} modified files".format(len(modified_files)))
        return modified_files
    except Exception as e:
        logger.exception("Error in get_modified_files:")
        return []

def generate_restore_tcl(work_dir, destination_dir, copied_files, logger):
    """Generate TCL script for restoring files"""
    try:
        # Create TCL filename with current timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        tcl_filename = os.path.join(destination_dir, "restore_files_{}.tcl".format(timestamp))
        
        logger.info("Generating restore TCL script: {}".format(tcl_filename))
        
        with open(tcl_filename, 'w') as tcl_file:
            tcl_file.write("#!/usr/bin/env tclsh\n\n")
            tcl_file.write("# Generated restore script\n")
            tcl_file.write("# Created on: {}\n\n".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            for file_info in copied_files:
                original_path = file_info[0]  # Full path (already converted)
                backup_file = os.path.basename(original_path)
                backup_path = os.path.join(destination_dir, backup_file)
                
                # Convert backup path to use environment variable
                backup_path = convert_path_to_env_var(backup_path)
                
                # Write cp command
                cmd = 'cp {} {}\n'.format(backup_path, original_path)
                tcl_file.write(cmd)
        
        # Make TCL script executable
        os.chmod(tcl_filename, 0o755)
        logger.info("Successfully generated restore TCL script")
        
    except Exception as e:
        logger.exception("Error generating TCL script:")

def copy_modified_files(work_dir, destination_base, logger):
    """Copy modified files to specified directory"""
    logger.info("Starting file copy process")
    
    # Get list of modified files
    modified_files = get_modified_files(work_dir, logger)
    
    if not modified_files:
        logger.warning("No modified files found")
        return
    
    # Use destination_base directly without creating a timestamped subdirectory
    destination_dir = destination_base
    # Convert destination directory to use environment variable
    destination_dir_env = convert_path_to_env_var(destination_dir)
    logger.debug("Using destination directory: {} (converted: {})".format(destination_dir, destination_dir_env))
    
    try:
        os.makedirs(destination_dir, exist_ok=True)
        logger.debug("Destination directory created/verified successfully")
    except Exception as e:
        logger.exception("Failed to create/verify destination directory:")
        return
    
    # Copy files
    successful_copies = []
    for file_info in modified_files:
        file_path = file_info[0]  # Full path (already converted)
        try:
            dest_path = os.path.join(destination_dir, os.path.basename(file_path))
            logger.debug("Copying: {} -> {}".format(file_path, convert_path_to_env_var(dest_path)))
            
            # Use original path for existence check and copy operations
            original_path = file_info[1]
            if not os.path.exists(original_path):
                logger.error("Source file does not exist: {}".format(original_path))
                continue
            
            shutil.copy2(original_path, dest_path)
            
            if os.path.exists(dest_path):
                # Print the cp command that would restore this file
                target_path = convert_path_to_env_var(os.path.join(work_dir, file_info[1]))
                print("cp {} {}".format(convert_path_to_env_var(dest_path), target_path))
                logger.info("Successfully copied: {}".format(file_path))
                successful_copies.append(file_info)
            else:
                logger.error("Failed to verify copy: {}".format(dest_path))
                
        except Exception as e:
            logger.exception("Error copying {}:".format(file_path))
    
    logger.info("\nCopy operation completed")
    logger.info("Destination directory: {}".format(destination_dir_env))
    logger.info("Successfully copied {} of {} files".format(
        len(successful_copies), len(modified_files)))
    
    # Generate restore TCL script
    if successful_copies:
        generate_restore_tcl(work_dir, destination_dir, successful_copies, logger)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Copy SVN modified files to a backup directory')
    parser.add_argument('-w', '--work-dir', 
                      default=os.getcwd(),
                      help='SVN working directory (default: current directory)')
    parser.add_argument('-o', '--output-dir',
                      required=True,
                      help='Output directory path for backup files')
    parser.add_argument('-d', '--debug',
                      action='store_true',
                      help='Enable debug mode for detailed logging')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    logger = setup_logging(args.debug)
    
    # Keep original path format
    work_dir = args.work_dir
    destination = args.output_dir
    
    logger.debug("Script started")
    logger.debug("Python version: {}".format(os.sys.version))
    logger.debug("Arguments: {}".format(args))
    
    # Verify directory exists without converting to absolute path
    if not os.path.exists(work_dir):
        logger.error("Work directory does not exist: {}".format(work_dir))
        exit(1)
    
    logger.info("Using work directory: {}".format(work_dir))
    logger.info("Using destination: {}".format(destination))
    
    copy_modified_files(work_dir, destination, logger)
    
    logger.debug("Script completed")