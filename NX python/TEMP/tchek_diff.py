#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import re
import os

def read_file_safely(filename):
    """Read file and safely handle different encodings"""
    # Try different encodings
    encodings = ['utf-8', 'latin1', 'cp1252', 'ascii']
    
    for encoding in encodings:
        try:
            with open(filename, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    
    # If all encodings fail, read in binary mode and force conversion
    with open(filename, 'rb') as f:
        content = f.read()
        # Force replace unidentifiable bytes with replacement characters
        return content.decode('utf-8', errors='replace')

def extract_patterns(filename):
    patterns = []
    try:
        content = read_file_safely(filename)
        lines = content.splitlines()
        
        for line in lines:
            if 'PATH' in line and '-tcheck' in line:
                # Extract the string between PATH and -tcheck
                match = re.search(r'PATH\s+(.+?)\s+-tcheck', line)
                if match:
                    patterns.append(match.group(1))
    except Exception as e:
        print(f"Error processing file {filename}: {e}")
    
    return patterns

def compare_files(file1, file2):
    patterns1 = extract_patterns(file1)
    patterns2 = extract_patterns(file2)
    
    # Find patterns only in file1
    only_in_file1 = set(patterns1) - set(patterns2)
    # Find patterns only in file2
    only_in_file2 = set(patterns2) - set(patterns1)
    
    print("Patterns only in the first file:")
    for pattern in only_in_file1:
        print(f"PATH {pattern} -tcheck")
    
    print("\nPatterns only in the second file:")
    for pattern in only_in_file2:
        print(f"PATH {pattern} -tcheck")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python tchek_diff.py file1 file2")
        sys.exit(1)
    
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    compare_files(file1, file2)
