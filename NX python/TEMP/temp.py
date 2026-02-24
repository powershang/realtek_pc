#!/usr/bin/env python3
import os
import re
import argparse
import shutil
from pathlib import Path

def load_replacements_from_file(config_file):
    """
    Load replacement rules from a config file
    
    Expected format:
    old_keyword1    new_keyword1
    old_keyword2     new_keyword2
    (supports multiple spaces between keywords)
    """
    replacements = {}
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Split by whitespace (any amount of spaces/tabs)
                parts = line.split()
                
                if len(parts) == 2:
                    old_key = parts[0]
                    new_key = parts[1]
                    replacements[old_key] = new_key
                elif len(parts) > 2:
                    print(f"Warning: Too many parts at line {line_num}: {line}")
                    print(f"  Only using first two: {parts[0]} to {parts[1]}")
                    replacements[parts[0]] = parts[1]
                else:
                    print(f"Warning: Invalid format at line {line_num}: {line}")
                    
    except FileNotFoundError:
        print(f"Error: Config file {config_file} not found")
        return None
    except Exception as e:
        print(f"Error reading config file: {e}")
        return None
    
    return replacements

def replace_keywords_in_file(filepath, replacements, backup=True):
    """
    Replace keywords in a file
    
    Args:
        filepath: Path to the file
        replacements: Dictionary of old_keyword to new_keyword
        backup: Whether to backup the original file
    """
    try:
        # Read the file
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Backup original file
        if backup:
            backup_path = f"{filepath}.bak"
            shutil.copy2(filepath, backup_path)
            print(f"Backed up: {backup_path}")
        
        # Store original content
        original_content = content
        
        # Perform replacements
        for old_keyword, new_keyword in replacements.items():
            # Use word boundaries for precise matching
            pattern = r'\b' + re.escape(old_keyword) + r'\b'
            content = re.sub(pattern, new_keyword, content)
        
        # Check if there were changes
        if content != original_content:
            # Write back to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Processed: {filepath}")
            return True
        else:
            print(f"No changes: {filepath}")
            return False
            
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Batch replace keywords in files')
    parser.add_argument('config_file', help='Configuration file with replacement rules')
    parser.add_argument('files', nargs='+', help='Files to process')
    parser.add_argument('--no-backup', action='store_true', help='Do not backup original files')
    
    args = parser.parse_args()
    
    # Load replacement rules from config file
    replacements = load_replacements_from_file(args.config_file)
    if replacements is None:
        return
    
    if not replacements:
        print("No replacement rules found in config file")
        return
    
    print("Keyword Replacement Tool")
    print("=" * 60)
    print(f"Config file: {args.config_file}")
    print(f"Replacement rules ({len(replacements)}):")
    for old, new in replacements.items():
        print(f"  {old} to {new}")
    print("=" * 60)
    
    # Process files
    processed_count = 0
    changed_count = 0
    
    for file_pattern in args.files:
        if '*' in file_pattern:
            # Handle wildcards
            files = Path('.').glob(file_pattern)
        else:
            # Handle single file
            files = [Path(file_pattern)]
        
        for filepath in files:
            if filepath.is_file():
                result = replace_keywords_in_file(
                    str(filepath), 
                    replacements, 
                    backup=not args.no_backup
                )
                processed_count += 1
                if result:
                    changed_count += 1
    
    print("=" * 60)
    print(f"Processing complete: {processed_count} files, {changed_count} changed")

if __name__ == "__main__":
    main()