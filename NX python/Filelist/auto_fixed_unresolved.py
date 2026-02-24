#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-

"""
Auto Fix Unresolved Design Units in FileList
=============================================

This tool automatically fixes unresolved design unit errors by:
1. Parsing compilation error log to find unresolved modules (*E format)
2. Searching for module files in a reference log containing all file paths
3. Adding missing file paths back to the original FileList

USAGE:
    python auto_fixed_unresolved.py <error_log> <reference_log> <filelist>

ARGUMENTS:
    error_log       Compilation error log file containing *E unresolved errors
    reference_log   Log file containing all available file paths
    filelist        Original .f filelist to be updated

OPTIONS:
    -o, --output    Output filelist name (default: fixed_filelist.f)
    -b, --backup    Create backup of original filelist (default: True)
    --insert-after  Insert missing files after this pattern/line (optional)
    
EXAMPLES:
    # Basic usage
    python auto_fixed_unresolved.py compile.log all_files.log dc_mc_top.f
    
    # With custom output
    python auto_fixed_unresolved.py compile.log all_files.log dc_mc_top.f -o new_list.f
    
    # Insert missing files after specific pattern
    python auto_fixed_unresolved.py compile.log all_files.log dc_mc_top.f --insert-after "mbist"
"""

import re
import argparse
from pathlib import Path
from typing import List, Set, Dict
import shutil


class UnresolvedFixer:
    def __init__(self, error_log: str, reference_log: str, filelist: str):
        """
        Initialize the fixer
        
        Args:
            error_log: Path to compilation error log
            reference_log: Path to reference log with all file paths
            filelist: Path to original .f filelist
        """
        self.error_log = Path(error_log)
        self.reference_log = Path(reference_log)
        self.filelist = Path(filelist)
        
        self.unresolved_modules: Set[str] = set()
        self.all_file_paths: Dict[str, str] = {}  # module_name -> file_path
        self.missing_paths: List[str] = []
        
    def parse_error_log(self) -> Set[str]:
        """
        Parse error log to find unresolved design units
        
        Looks for pattern: *E...design unit 'module_name' is unresolved
        
        Returns:
            Set of unresolved module names
        """
        print("=" * 60)
        print("Parsing error log to find unresolved design units...")
        print("=" * 60)
        
        if not self.error_log.exists():
            raise FileNotFoundError(f"Error log not found: {self.error_log}")
            
        with open(self.error_log, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Pattern for unresolved design unit errors
        # Matches: *E...design unit 'module_name' is unresolved
        pattern = r"\*E[,:].*?design unit\s+'([^']+)'\s+is unresolved"
        matches = re.findall(pattern, content, re.IGNORECASE)
        
        for module_name in matches:
            self.unresolved_modules.add(module_name)
            print(f"Found unresolved module: {module_name}")
            
        print(f"\nTotal unresolved modules found: {len(self.unresolved_modules)}")
        return self.unresolved_modules
        
    def parse_reference_log(self) -> Dict[str, str]:
        """
        Parse reference log to build mapping of module names to file paths
        
        Assumes module name = filename (without .v/.sv extension)
        Supports both .v (Verilog) and .sv (SystemVerilog) files
        
        Returns:
            Dictionary mapping module_name to file_path
        """
        print("\n" + "=" * 60)
        print("Parsing reference log to build file path mapping...")
        print("=" * 60)
        
        if not self.reference_log.exists():
            raise FileNotFoundError(f"Reference log not found: {self.reference_log}")
            
        with open(self.reference_log, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
        # Pattern to match file paths ending with .v or .sv
        path_pattern = re.compile(r'.*\.(v|sv)\s*$', re.IGNORECASE)
        
        file_count = 0
        v_count = 0
        sv_count = 0
        
        for line in lines:
            line = line.strip()
            if path_pattern.match(line):
                # Remove possible comments
                if '//' in line:
                    line = line.split('//')[0].strip()
                    
                if line:
                    # Extract filename and module name (filename without .v/.sv)
                    filename = Path(line).name
                    module_name = None
                    
                    if filename.endswith('.v'):
                        module_name = filename[:-2]  # Remove .v extension
                        v_count += 1
                    elif filename.endswith('.sv'):
                        module_name = filename[:-3]  # Remove .sv extension
                        sv_count += 1
                    
                    if module_name:
                        self.all_file_paths[module_name] = line
                        file_count += 1
                        
                        # Debug: show first few and last few entries
                        if file_count <= 3:
                            print(f"  Sample {file_count}: {module_name} -> {line}")
                        
        if file_count > 3:
            # Show last entry
            print(f"  ...")
            print(f"  Sample {file_count}: {module_name} -> {line}")
                        
        print(f"Total file paths found: {len(self.all_file_paths)}")
        print(f"  .v files: {v_count}")
        print(f"  .sv files: {sv_count}")
        return self.all_file_paths
        
    def find_missing_paths(self) -> List[str]:
        """
        Find file paths for unresolved modules
        
        Returns:
            List of file paths to be added to filelist
        """
        print("\n" + "=" * 60)
        print("Finding file paths for unresolved modules...")
        print("=" * 60)
        
        found_count = 0
        not_found_count = 0
        
        for module_name in self.unresolved_modules:
            if module_name in self.all_file_paths:
                file_path = self.all_file_paths[module_name]
                self.missing_paths.append(file_path)
                print(f"[OK] Found: {module_name} -> {file_path}")
                found_count += 1
            else:
                print(f"[WARN] NOT FOUND: {module_name}")
                
                # Try fuzzy search for similar module names
                print(f"  Searching for similar names...")
                similar = []
                for key in self.all_file_paths.keys():
                    if module_name.lower() in key.lower() or key.lower() in module_name.lower():
                        similar.append(key)
                
                if similar:
                    print(f"  Found {len(similar)} similar module names:")
                    for sim in similar[:5]:  # Show up to 5 similar names
                        print(f"    - {sim}")
                    if len(similar) > 5:
                        print(f"    ... and {len(similar) - 5} more")
                else:
                    print(f"  No similar module names found")
                    
                not_found_count += 1
                
        print(f"\nSummary:")
        print(f"  Files found: {found_count}")
        print(f"  Files NOT found: {not_found_count}")
        
        return self.missing_paths
        
    def update_filelist(self, output_file: str = None, backup: bool = True, 
                       insert_after: str = None) -> None:
        """
        Update filelist by adding missing file paths
        
        Args:
            output_file: Output filelist name (default: use same name)
            backup: Whether to create backup of original filelist
            insert_after: Insert missing files after lines containing this pattern
        """
        print("\n" + "=" * 60)
        print("Updating filelist...")
        print("=" * 60)
        
        if not self.filelist.exists():
            raise FileNotFoundError(f"Filelist not found: {self.filelist}")
            
        # Create backup if requested
        if backup:
            backup_path = self.filelist.with_suffix('.f.backup')
            shutil.copy2(self.filelist, backup_path)
            print(f"Created backup: {backup_path}")
            
        # Read original filelist
        with open(self.filelist, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
        # Determine output file
        if output_file:
            output_path = Path(output_file)
        else:
            output_path = self.filelist
            
        # Build new filelist
        new_lines = []
        inserted = False
        
        if insert_after:
            # Insert after specific pattern
            for line in lines:
                new_lines.append(line)
                if not inserted and insert_after.lower() in line.lower():
                    # Found insertion point
                    new_lines.append(f"\n// Auto-added missing files ({len(self.missing_paths)} files)\n")
                    for missing_path in self.missing_paths:
                        new_lines.append(f"{missing_path}\n")
                    inserted = True
                    print(f"Inserted {len(self.missing_paths)} files after line: {line.strip()}")
        else:
            # Append at the end
            new_lines = lines
            new_lines.append(f"\n// Auto-added missing files ({len(self.missing_paths)} files)\n")
            for missing_path in self.missing_paths:
                new_lines.append(f"{missing_path}\n")
            inserted = True
            print(f"Appended {len(self.missing_paths)} files at the end")
            
        # Write updated filelist
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
            
        print(f"\nUpdated filelist saved: {output_path}")
        print(f"Total files added: {len(self.missing_paths)}")
        
    def process(self, output_file: str = None, backup: bool = True, 
                insert_after: str = None) -> None:
        """
        Execute complete fixing workflow
        
        Args:
            output_file: Output filelist name
            backup: Whether to create backup
            insert_after: Insert missing files after this pattern
        """
        print("=" * 60)
        print("Starting Auto Fix Unresolved...")
        print("=" * 60)
        print(f"Error log: {self.error_log}")
        print(f"Reference log: {self.reference_log}")
        print(f"FileList: {self.filelist}")
        print()
        
        # 1. Parse error log
        self.parse_error_log()
        
        # 2. Parse reference log
        self.parse_reference_log()
        
        # 3. Find missing paths
        self.find_missing_paths()
        
        if not self.missing_paths:
            print("\n" + "=" * 60)
            print("No missing files found or all modules are already resolved!")
            print("=" * 60)
            return
            
        # 4. Update filelist
        self.update_filelist(output_file, backup, insert_after)
        
        print("\n" + "=" * 60)
        print("Auto Fix Completed Successfully!")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='Automatically fix unresolved design units in FileList',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Basic usage
  python auto_fixed_unresolved.py compile.log all_files.log dc_mc_top.f
  
  # With custom output
  python auto_fixed_unresolved.py compile.log all_files.log dc_mc_top.f -o fixed.f
  
  # Insert after specific pattern
  python auto_fixed_unresolved.py compile.log all_files.log dc_mc_top.f --insert-after "mbist"
        '''
    )
    
    parser.add_argument('error_log', help='Compilation error log file')
    parser.add_argument('reference_log', help='Reference log with all file paths')
    parser.add_argument('filelist', help='Original .f filelist to update')
    parser.add_argument('-o', '--output', help='Output filelist name (default: update in-place)')
    parser.add_argument('-b', '--backup', action='store_true', default=True,
                       help='Create backup of original filelist (default: True)')
    parser.add_argument('--no-backup', action='store_false', dest='backup',
                       help='Do not create backup')
    parser.add_argument('--insert-after', help='Insert missing files after lines containing this pattern')
    
    args = parser.parse_args()
    
    try:
        fixer = UnresolvedFixer(
            error_log=args.error_log,
            reference_log=args.reference_log,
            filelist=args.filelist
        )
        
        fixer.process(
            output_file=args.output,
            backup=args.backup,
            insert_after=args.insert_after
        )
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    return 0


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        print(__doc__)
        sys.exit(1)
    else:
        sys.exit(main())