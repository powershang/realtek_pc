#!/usr/bin/env python3

import os
import glob

def rename_v_files():
    """
    Find all .v files in the current directory and subdirectories and
    replace 'hd21' with 'hd22' and 'hdmi21' with 'hdmi22' in their filenames
    """
    # Get current working directory
    current_dir = os.getcwd()
    print(f"Searching in directory: {current_dir}")
    
    # Find all .v files recursively in current directory and subdirectories
    v_files = glob.glob("**/*.v", recursive=True)
    
    if not v_files:
        print("No .v files found")
        return
    
    print(f"Found {len(v_files)} .v file(s):")
    for file in v_files:
        print(f"  - {file}")
    
    print("\n" + "="*50)
    
    # Separate files into two categories
    files_need_rename = []
    files_no_rename = []
    
    for filepath in v_files:
        filename = os.path.basename(filepath)
        if "hd21" in filename or "hdmi21" in filename:
            files_need_rename.append(filepath)
        else:
            files_no_rename.append(filepath)
    
    # Display files that do NOT need renaming
    print(f"Files WITHOUT hd21 or hdmi21 in filename ({len(files_no_rename)} files):")
    if files_no_rename:
        for file in files_no_rename:
            print(f"  - {file}")
    else:
        print("  No files found without hd21 or hdmi21")
    
    print("\n" + "-"*30)
    
    # Display files that need renaming
    print(f"Files WITH hd21 or hdmi21 in filename ({len(files_need_rename)} files):")
    if files_need_rename:
        for file in files_need_rename:
            print(f"  - {file}")
    else:
        print("  No files found with hd21 or hdmi21")
    
    print("\n" + "="*50)
    print("Starting rename process...")
    
    # Rename files
    renamed_count = 0
    for old_filepath in files_need_rename:
        # Get directory and filename
        directory = os.path.dirname(old_filepath)
        old_filename = os.path.basename(old_filepath)
        
        # Replace both hd21 and hdmi21
        new_filename = old_filename.replace("hd21", "hd22").replace("hdmi21", "hdmi22")
        new_filepath = os.path.join(directory, new_filename)
        
        # Check if new filepath already exists
        if os.path.exists(new_filepath):
            print(f"Warning: {new_filepath} already exists, skipping rename of {old_filepath}")
            continue
        
        try:
            os.rename(old_filepath, new_filepath)
            print(f"SUCCESS Renamed: {old_filepath} -> {new_filepath}")
            renamed_count += 1
        except OSError as e:
            print(f"FAILED to rename {old_filepath}: {e}")
    
    print(f"\nCompleted! Renamed {renamed_count} file(s)")
    print(f"Skipped {len(files_no_rename)} file(s) without hd21 or hdmi21 in filename")

if __name__ == "__main__":
    rename_v_files()