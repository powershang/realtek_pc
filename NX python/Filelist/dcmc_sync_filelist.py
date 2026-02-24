#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-

"""
DCMC Sync Filelist Tool
=======================

USAGE:
    python dcmc_sync_filelist.py <input1.f> [input2.f ...] [source_path] [options]

DESCRIPTION:
    This tool extracts all mbist-related file paths from one or more .f filelists,
    copies those files from a specified source directory to a local subdirectory,
    and generates a new filelist with the copied files.
    
    Supports processing multiple input files simultaneously with automatic deduplication.

ARGUMENTS:
    input.f         One or more input .f filelist files containing $PROJECT_HOME paths
    source_path     (Optional) Path to replace $PROJECT_HOME with
                   If not provided, will prompt for interactive input

OPTIONS:
    -o, --output-dir    Output subdirectory name (default: mbist_files)
    -f, --filelist      Output filelist filename (default: mbist_filelist.f)
    -u, --update-original   Automatically update original .f file(s) to use local paths
    -c, --copy-cells    Automatically extract and copy SRAM cell files
    --cell-path         SRAM cell source path (used with -c)
    -h, --help          Show help message

EXAMPLES:
    # ============ Single File Mode ============
    # Interactive mode - will prompt for source path
    python dcmc_sync_filelist.py dc_mc_top.f
    
    # Direct mode - specify source path directly
    python dcmc_sync_filelist.py dc_mc_top.f /path/to/your/old/project
    
    # Custom output directory and filelist name
    python dcmc_sync_filelist.py dc_mc_top.f /project/v1.2 -o my_mbist -f my_list.f
    
    # Using relative paths
    python dcmc_sync_filelist.py input.f ../old_project -o collected_mbist
    
    # Automatically update original .f file to use local paths
    python dcmc_sync_filelist.py dc_mc_top.f /project/v1.2 -u
    
    # Automatically extract and copy SRAM cell files
    python dcmc_sync_filelist.py dc_mc_top.f /project/v1.2 -c
    
    # Full automation: update original file and copy SRAM cells
    python dcmc_sync_filelist.py dc_mc_top.f /project/v1.2 -u -c --cell-path /path/to/cells
    
    # ============ Multiple Files Mode ============
    # Process multiple files at once
    python dcmc_sync_filelist.py file1.f file2.f file3.f /path/to/project
    
    # Process all .f files in current directory (using shell wildcard)
    python dcmc_sync_filelist.py *.f /path/to/project
    
    # Multiple files with auto-update
    python dcmc_sync_filelist.py dc_mc_top.f dc_mc_sub.f /project/v1.2 -u
    
    # Multiple files with SRAM cell extraction
    python dcmc_sync_filelist.py top.f sub1.f sub2.f /project/v1.2 -u -c --cell-path /cells
    
    # Interactive mode with multiple files (will prompt for paths)
    python dcmc_sync_filelist.py file1.f file2.f file3.f

WORKFLOW:
    1. Scan all input .f file(s) for lines containing 'mbist' and ending with '.v'
    2. Automatically deduplicate paths found across multiple files
    3. Replace $PROJECT_HOME with specified source path
    4. Copy matching files to output subdirectory (flat structure, filename only)
    5. Generate new .f filelist with relative paths to copied files
    6. (Optional) Extract SRAM cellnames from *_block.v files and copy cell files
    7. (Optional) Update all original .f file(s) to use local paths

OUTPUT:
    - Creates subdirectory with copied mbist files (all in root level)
    - Generates new .f filelist pointing to copied files
    - Files are copied with filename only, no directory structure maintained
    - When processing multiple files, paths are deduplicated automatically
    - Each original .f file is updated independently (with backup .f.backup)
"""

import os
import re
import shutil
import argparse
from pathlib import Path

class MbistFilelistProcessor:
    def __init__(self, input_files, source_path=None, output_dir="mbist_files"):
        """
        Initialize the processor
        
        Args:
            input_files: List of paths to input .f files (can be single file or multiple files)
            source_path: Custom path to replace $PROJECT_HOME (optional, will prompt if not provided)
            output_dir: Output subdirectory name
        """
        # Support both single file and multiple files
        if isinstance(input_files, (str, Path)):
            self.input_files = [Path(input_files)]
        else:
            self.input_files = [Path(f) for f in input_files]
            
        self.source_path = Path(source_path) if source_path else None
        self.output_dir = Path(output_dir)
        self.mbist_paths = []
        self.copied_files = []
        # Track which file each mbist path came from
        self.path_to_source_file = {}
        
    def get_source_path(self):
        """Interactively get user-specified path to replace $PROJECT_HOME"""
        if self.source_path:
            return
            
        print("="*60)
        print("Need to specify path to replace $PROJECT_HOME")
        print("="*60)
        
        while True:
            user_path = input("Please enter the project path to replace $PROJECT_HOME: ").strip()
            
            if not user_path:
                print("ERROR: Path cannot be empty, please try again")
                continue
                
            path_obj = Path(user_path)
            if not path_obj.exists():
                print(f"WARNING: Path does not exist: {user_path}")
                retry = input("Do you want to continue with this path? (y/n): ").strip().lower()
                if retry == 'y':
                    self.source_path = path_obj
                    break
                else:
                    continue
            else:
                self.source_path = path_obj
                break
                
        print(f"SUCCESS: Will use path: {self.source_path}")
        print()
        
    def extract_mbist_paths(self):
        """Extract all mbist-related paths from all .f files"""
        all_paths = []
        
        for input_file in self.input_files:
            print(f"\nReading file: {input_file}")
            
            if not input_file.exists():
                print(f"WARNING: File not found: {input_file}, skipping...")
                continue
                
            with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            # Search for paths containing mbist
            mbist_pattern = re.compile(r'.*mbist.*\.v\s*$', re.IGNORECASE)
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if mbist_pattern.match(line):
                    # Remove possible comments
                    if '//' in line:
                        line = line.split('//')[0].strip()
                        
                    if line:
                        all_paths.append(line)
                        # Record which file this path came from
                        self.path_to_source_file[line] = input_file
                        print(f"Found mbist path (line {line_num}): {line}")
        
        # Remove duplicates while preserving order
        seen = set()
        for path in all_paths:
            if path not in seen:
                seen.add(path)
                self.mbist_paths.append(path)
        
        print(f"\n{'='*60}")
        print(f"Summary: Processed {len(self.input_files)} input file(s)")
        print(f"Total found {len(all_paths)} mbist paths ({len(self.mbist_paths)} unique)")
        print(f"{'='*60}")
        return self.mbist_paths
    
    def resolve_path(self, file_path):
        """Resolve $PROJECT_HOME path to actual path by searching in subdirectories"""
        filename = Path(file_path).name
        
        # First try direct path
        direct_path = self.source_path / filename
        if direct_path.exists():
            return direct_path
            
        # If not found, search in subdirectories
        for subdir in self.source_path.iterdir():
            if subdir.is_dir():
                subdir_file = subdir / filename
                if subdir_file.exists():
                    return subdir_file
                    
        # If still not found, return the direct path (will show as not found)
        return direct_path
    
    def copy_files(self):
        """Copy files to output directory"""
        if not self.mbist_paths:
            print("No mbist files found, please run extract_mbist_paths() first")
            return
            
        # Remove existing output directory if it exists
        if self.output_dir.exists():
            print(f"Removing existing directory: {self.output_dir}")
            shutil.rmtree(self.output_dir)
            
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        print(f"Creating output directory: {self.output_dir}")
        
        for file_path in self.mbist_paths:
            source_file = self.resolve_path(file_path)
            
            if source_file.exists():
                # Extract only the filename, ignore directory structure
                filename = Path(file_path).name
                dest_file = self.output_dir / filename
                
                # Copy file directly to root of output directory
                shutil.copy2(source_file, dest_file)
                self.copied_files.append(dest_file)
                print(f"Copied: {source_file} -> {dest_file}")
            else:
                print(f"Warning: File does not exist: {source_file}")
                
        print(f"Total copied {len(self.copied_files)} files")
    
    def generate_filelist(self, output_file="mbist_filelist.f"):
        """Generate new filelist"""
        output_path = Path(output_file)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"// Generated mbist filelist\n")
            f.write(f"// Total files: {len(self.copied_files)}\n")
            f.write(f"// Generated from: {', '.join(str(f) for f in self.input_files)}\n")
            f.write(f"// Source path: {self.source_path}\n\n")
            
            for copied_file in self.copied_files:
                # Write the path directly (already relative to current directory)
                f.write(f"{copied_file}\n")
                
        print(f"Generated filelist: {output_path}")
        print(f"Contains {len(self.copied_files)} copied file paths")
        
    def update_original_filelist(self, output_file=None):
        """Update all original .f files by replacing paths for successfully copied mbist files"""
        # Create a mapping of copied file names to new paths
        copied_filename_to_newpath = {}
        sram_cell_files = []  # Track SRAM cell files separately
        
        for copied_file in self.copied_files:
            filename = copied_file.name
            # Convert to new path format
            new_path = f"$PROJECT_HOME/hardware/rtl/dc_mc/{self.output_dir}/{filename}"
            copied_filename_to_newpath[filename] = new_path
            
            # Check if this is a SRAM cell file (doesn't contain 'mbist')
            if 'mbist' not in filename.lower():
                sram_cell_files.append(new_path)
        
        # Process each input file
        for input_file in self.input_files:
            if not input_file.exists():
                print(f"WARNING: Skipping non-existent file: {input_file}")
                continue
                
            print(f"\n{'='*60}")
            print(f"Updating file: {input_file}")
            print(f"{'='*60}")
            
            # Create backup
            backup_file = input_file.with_suffix('.f.backup')
            shutil.copy2(input_file, backup_file)
            print(f"Created backup: {backup_file}")
            
            # Read original file
            with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            # Process lines: replace paths for copied files, keep originals for not-found files
            modified_lines = []
            replaced_count = 0
            kept_count = 0
            mbist_pattern = re.compile(r'.*mbist.*\.v\s*', re.IGNORECASE)
            last_mbist_line_index = -1  # Track where to insert SRAM cells
            
            for idx, line in enumerate(lines):
                line_stripped = line.strip()
                if mbist_pattern.match(line_stripped):
                    last_mbist_line_index = len(modified_lines)  # Record position
                    # Extract filename from the path
                    filename = Path(line_stripped.split('//')[0].strip()).name
                    
                    if filename in copied_filename_to_newpath:
                        # File was successfully copied, replace with new path
                        new_path = copied_filename_to_newpath[filename]
                        modified_lines.append(new_path + '\n')
                        print(f"Replaced: {line_stripped[:60]}... -> {new_path}")
                        replaced_count += 1
                    else:
                        # File was not found/copied, keep original path
                        modified_lines.append(line)
                        print(f"Kept (not found): {line_stripped}")
                        kept_count += 1
                else:
                    # Non-mbist line, keep as is
                    modified_lines.append(line)
            
            # Insert SRAM cell files after the last mbist line
            if sram_cell_files and last_mbist_line_index >= 0:
                print(f"\nAdding {len(sram_cell_files)} SRAM cell files after last mbist line...")
                insert_position = last_mbist_line_index + 1
                for sram_file in sram_cell_files:
                    modified_lines.insert(insert_position, sram_file + '\n')
                    print(f"Added SRAM cell: {sram_file}")
                    insert_position += 1
                    
            # Write modified file
            with open(input_file, 'w', encoding='utf-8') as f:
                f.writelines(modified_lines)
                
            print(f"\nUpdated: {input_file}")
            print(f"  Replaced paths: {replaced_count} files")
            print(f"  Kept original paths: {kept_count} files")
            print(f"  Added SRAM cells: {len(sram_cell_files)} files")
        
    def extract_sram_cellnames(self):
        """Extract SRAM cellnames from *_block.v files in mbist_files/"""
        if not self.output_dir.exists():
            print("ERROR: mbist_files directory does not exist")
            return []
            
        # Find all *_block.v files
        block_files = list(self.output_dir.glob("*_block.v"))
        cellnames = []
        
        print(f"Found {len(block_files)} block.v files:")
        for block_file in block_files:
            filename = block_file.name
            print(f"  {filename}")
            
            # Extract cellname from xxx_cellname_block.v
            if filename.endswith('_block.v'):
                # Remove _block.v suffix
                name_part = filename[:-8]  # Remove '_block.v'
                
                # Find the last underscore to get cellname
                parts = name_part.split('_')
                if len(parts) >= 2:
                    cellname = parts[-1]  # Last part is cellname
                    cellnames.append(cellname)
                    print(f"    -> Extracted cellname: {cellname}")
                else:
                    print(f"    -> Warning: Could not extract cellname from {filename}")
                    
        # Remove duplicates and sort
        unique_cellnames = sorted(list(set(cellnames)))
        print(f"\nUnique SRAM cellnames found: {len(unique_cellnames)}")
        for cellname in unique_cellnames:
            print(f"  {cellname}")
            
        return unique_cellnames
        
    def get_sram_cell_path(self):
        """Interactively get user-specified path for SRAM cell files"""
        print("="*60)
        print("Need to specify path for SRAM cell files")
        print("="*60)
        
        while True:
            cell_path = input("Please enter the SRAM cell source path: ").strip()
            
            if not cell_path:
                print("ERROR: Path cannot be empty, please try again")
                continue
                
            path_obj = Path(cell_path)
            if not path_obj.exists():
                print(f"WARNING: Path does not exist: {cell_path}")
                retry = input("Do you want to continue with this path? (y/n): ").strip().lower()
                if retry == 'y':
                    return path_obj
                else:
                    continue
            else:
                return path_obj
                
    def find_sram_cell_file(self, cellname, cell_source_path):
        """Find SRAM cell file by searching in subdirectories"""
        cell_filename = f"{cellname}.v"
        
        # First try direct path
        direct_path = cell_source_path / cell_filename
        if direct_path.exists():
            return direct_path
            
        # If not found, search in subdirectories
        for subdir in cell_source_path.iterdir():
            if subdir.is_dir():
                subdir_file = subdir / cell_filename
                if subdir_file.exists():
                    return subdir_file
                    
        # If still not found, return None
        return None
    
    def copy_sram_cells(self, cellnames, cell_source_path):
        """Copy SRAM cell files to mbist_files/"""
        if not cellnames:
            print("No SRAM cellnames found")
            return
            
        copied_cells = []
        missing_cells = []
        
        print(f"Searching for SRAM cell files in: {cell_source_path}")
        
        for cellname in cellnames:
            cell_filename = f"{cellname}.v"
            source_cell_file = self.find_sram_cell_file(cellname, cell_source_path)
            
            if source_cell_file:
                dest_cell_file = self.output_dir / cell_filename
                shutil.copy2(source_cell_file, dest_cell_file)
                copied_cells.append(dest_cell_file)
                print(f"Copied: {source_cell_file} -> {dest_cell_file}")
            else:
                missing_cells.append(cell_filename)
                print(f"WARNING: Cell file not found: {cell_filename}")
                
        print(f"\nSRAM cell copy summary:")
        print(f"  Successfully copied: {len(copied_cells)} files")
        print(f"  Missing files: {len(missing_cells)} files")
        
        if missing_cells:
            print("  Missing cell files:")
            for missing in missing_cells:
                print(f"    {missing}")
                
        return copied_cells
        
    def process_sram_cells(self, predefined_cell_path=None, output_filelist="mbist_filelist.f"):
        """Process SRAM cell extraction and copying"""
        print("="*60)
        print("Processing SRAM cell files...")
        print("="*60)
        
        # 1. Extract cellnames from block.v files
        cellnames = self.extract_sram_cellnames()
        
        if not cellnames:
            print("No SRAM cellnames found, skipping SRAM cell processing")
            return
            
        print()
        
        # 2. Get SRAM cell source path
        if predefined_cell_path:
            cell_source_path = Path(predefined_cell_path)
            print(f"Using predefined SRAM cell path: {cell_source_path}")
        else:
            cell_source_path = self.get_sram_cell_path()
        print(f"SUCCESS: Will use SRAM cell path: {cell_source_path}")
        print()
        
        # 3. Copy SRAM cell files
        copied_cells = self.copy_sram_cells(cellnames, cell_source_path)
        
        # 4. Regenerate filelist to include new cell files
        if copied_cells:
            print("\nRegenerating filelist to include SRAM cell files...")
            # Update copied_files list to include new cell files
            self.copied_files.extend(copied_cells)
            self.generate_filelist(output_filelist)
            
        print("="*60)
        print("SRAM cell processing completed!")
        print("="*60)
        
    def process(self, output_filelist="mbist_filelist.f", auto_update_original=False, auto_copy_cells=False, cell_path=None):
        """Execute complete processing workflow"""
        print("="*60)
        print("Starting mbist file processing...")
        print("="*60)
        
        # 0. Get user-specified path
        self.get_source_path()
        
        # 1. Extract mbist paths
        self.extract_mbist_paths()
        print()
        
        # 2. Copy files
        print("Starting file copying...")
        self.copy_files()
        print()
        
        # 3. Generate filelist
        print("Generating filelist...")
        self.generate_filelist(output_filelist)
        print()
        
        # 4. Process SRAM cells if requested
        if auto_copy_cells:
            self.process_sram_cells(cell_path, output_filelist)
        else:
            process_cells = input("Do you want to extract and copy SRAM cell files? (y/n): ").strip().lower()
            if process_cells == 'y':
                self.process_sram_cells(cell_path, output_filelist)
        
        # 5. Update original file if requested
        if auto_update_original:
            print("Updating original filelist...")
            self.update_original_filelist()
        else:
            update_original = input("Do you want to update the original .f file to use local mbist_files/ paths? (y/n): ").strip().lower()
            if update_original == 'y':
                print("Updating original filelist...")
                self.update_original_filelist()
        
        print("="*60)
        print("Processing completed!")
        print("="*60)

def main():
    parser = argparse.ArgumentParser(
        description='Process .f file(s), extract mbist paths and copy files',
        epilog='You can specify multiple input files to process them together.'
    )
    parser.add_argument('input_files', nargs='+', help='One or more .f file paths')
    parser.add_argument('source_path', nargs='?', help='Custom path to replace $PROJECT_HOME (optional, will prompt if not provided)')
    parser.add_argument('-o', '--output-dir', default='mbist_files', 
                       help='Output subdirectory name (default: mbist_files)')
    parser.add_argument('-f', '--filelist', default='mbist_filelist.f',
                       help='Output filelist filename (default: mbist_filelist.f)')
    parser.add_argument('-u', '--update-original', action='store_true',
                       help='Automatically update original .f file(s) to use local paths')
    parser.add_argument('-c', '--copy-cells', action='store_true',
                       help='Automatically extract and copy SRAM cell files')
    parser.add_argument('--cell-path', type=str,
                       help='SRAM cell source path (optional, will prompt if not provided when -c is used)')
    
    args = parser.parse_args()
    
    # Determine if last argument is source_path or part of input_files
    input_files = args.input_files
    source_path = args.source_path
    
    # If source_path is provided but looks like a .f file, treat it as input file
    if source_path and source_path.endswith('.f'):
        input_files.append(source_path)
        source_path = None
    
    try:
        processor = MbistFilelistProcessor(
            input_files=input_files,
            source_path=source_path,
            output_dir=args.output_dir
        )
        
        processor.process(args.filelist, args.update_original, args.copy_cells, args.cell_path)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    return 0

if __name__ == "__main__":
    # Show usage if no arguments provided
    if len(os.sys.argv) == 1:
        print("USAGE:")
        print("python dcmc_sync_filelist.py <input1.f> [input2.f ...] [source_path] [options]")
        print("\nEXAMPLES:")
        print("# Single file (original behavior)")
        print("python dcmc_sync_filelist.py input.f /path/to/project")
        print("\n# Multiple files")
        print("python dcmc_sync_filelist.py file1.f file2.f file3.f /path/to/project")
        print("python dcmc_sync_filelist.py *.f /path/to/project")
        print("\n# Multiple files with options")
        print("python dcmc_sync_filelist.py file1.f file2.f -u -c --cell-path /path/to/cells")
        print("\nFor detailed help, use: python dcmc_sync_filelist.py -h")
    else:
        exit(main())
