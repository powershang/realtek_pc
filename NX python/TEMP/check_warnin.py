#!/usr/bin/env python3
"""
Script to extract all warning messages (*W) and error messages (*E) from ncverilog log files
and save them to a separate file.
"""

import os
import re
import sys
from datetime import datetime

# Ignore list - warnings containing these keywords will be skipped
IGNORE_WARNING_KEYWORDS = [
    "rtk_rtl_lib",
    "DSEM2009",
    "RNOUIE",
    "SPDUSD",
    "DSEMEL",
    # Add more keywords here as needed
    # "another_keyword",
    # "yet_another_keyword",
]

def find_log_files(directory="."):
    """
    Find ncverilog.log file in the specified directory
    """
    log_file_path = os.path.join(directory, "ncverilog.log")
    
    if os.path.exists(log_file_path):
        return [log_file_path]
    else:
        return []

def should_ignore_warning(warning_content, ignore_keywords):
    """
    Check if warning should be ignored based on ignore keywords
    """
    for keyword in ignore_keywords:
        if keyword.lower() in warning_content.lower():
            return True
    return False

def extract_warnings_and_errors(log_file):
    """
    Extract all warning (*W) and error (*E) lines from a log file
    """
    warnings = []
    ignored_warnings = []
    errors = []
    
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                # Look for error patterns first
                if re.search(r'\*E', line):
                    error_data = {
                        'file': log_file,
                        'line_num': line_num,
                        'content': line.strip()
                    }
                    errors.append(error_data)
                
                # Look for warning patterns
                elif re.search(r'\*W', line):
                    warning_data = {
                        'file': log_file,
                        'line_num': line_num,
                        'content': line.strip()
                    }
                    
                    # Check if this warning should be ignored
                    if should_ignore_warning(line, IGNORE_WARNING_KEYWORDS):
                        ignored_warnings.append(warning_data)
                    else:
                        warnings.append(warning_data)
                        
    except Exception as e:
        print(f"Error reading file {log_file}: {e}")
    
    return warnings, ignored_warnings, errors

def save_results_to_file(all_warnings, ignored_warnings, all_errors, output_file="extracted_warnings.txt"):
    """
    Save all extracted warnings and errors to a file
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write("="*80 + "\n")
            f.write("NCVERILOG WARNING & ERROR EXTRACTION REPORT\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            
            # Write ignore list
            f.write("IGNORED WARNING KEYWORDS:\n")
            f.write("-" * 30 + "\n")
            if IGNORE_WARNING_KEYWORDS:
                for keyword in IGNORE_WARNING_KEYWORDS:
                    f.write(f"  - {keyword}\n")
            else:
                f.write("  (None)\n")
            f.write("\n")
            
            # Write errors first (highest priority)
            f.write("ERRORS (*E) - COMPILE FAILURES:\n")
            f.write("="*50 + "\n")
            if all_errors:
                for error in all_errors:
                    f.write(f"Line {error['line_num']}: {error['content']}\n")
            else:
                f.write("No errors found.\n")
            
            f.write("\n" + "="*50 + "\n\n")
            
            # Write active warnings (not ignored)
            f.write("ACTIVE WARNINGS (*W) - NEED ATTENTION:\n")
            f.write("="*50 + "\n")
            if all_warnings:
                for warning in all_warnings:
                    f.write(f"Line {warning['line_num']}: {warning['content']}\n")
            else:
                f.write("No active warnings found.\n")
            
            f.write("\n" + "="*50 + "\n\n")
            
            # Write ignored warnings
            f.write("IGNORED WARNINGS (*W):\n")
            f.write("="*50 + "\n")
            if ignored_warnings:
                for warning in ignored_warnings:
                    f.write(f"Line {warning['line_num']}: {warning['content']}\n")
            else:
                f.write("No ignored warnings found.\n")
            
            f.write("\n" + "="*50 + "\n\n")
            
            # Write summary
            f.write("SUMMARY\n")
            f.write("-" * 20 + "\n")
            f.write(f"Errors (*E): {len(all_errors)}\n")
            f.write(f"Active warnings (*W): {len(all_warnings)}\n")
            f.write(f"Ignored warnings (*W): {len(ignored_warnings)}\n")
            f.write(f"Total issues found: {len(all_errors) + len(all_warnings) + len(ignored_warnings)}\n")
                
    except Exception as e:
        print(f"Error writing to output file {output_file}: {e}")

def main():
    """
    Main function to orchestrate the warning and error extraction process
    """
    print("NCVERILOG Warning & Error Extractor")
    print("=" * 35)
    
    # Display ignore list
    print("Ignore keywords:")
    if IGNORE_WARNING_KEYWORDS:
        for keyword in IGNORE_WARNING_KEYWORDS:
            print(f"  - {keyword}")
    else:
        print("  (None)")
    print()
    
    # Find log files
    log_files = find_log_files()
    
    if not log_files:
        print("ncverilog.log file not found in the current directory.")
        print("Please ensure ncverilog.log file is present.")
        return
    
    print(f"Found ncverilog.log file")
    
    # Extract warnings and errors from all files
    all_warnings = []
    all_ignored_warnings = []
    all_errors = []
    
    for log_file in log_files:
        print(f"\nProcessing: {log_file}")
        warnings, ignored_warnings, errors = extract_warnings_and_errors(log_file)
        all_warnings.extend(warnings)
        all_ignored_warnings.extend(ignored_warnings)
        all_errors.extend(errors)
        print(f"  Found {len(errors)} error(s)")
        print(f"  Found {len(warnings)} active warning(s)")
        print(f"  Found {len(ignored_warnings)} ignored warning(s)")
    
    # Save results
    output_file = "extracted_warnings.txt"
    save_results_to_file(all_warnings, all_ignored_warnings, all_errors, output_file)
    
    print(f"\nExtraction complete!")
    print(f"Errors: {len(all_errors)}")
    print(f"Active warnings: {len(all_warnings)}")
    print(f"Ignored warnings: {len(all_ignored_warnings)}")
    print(f"Total issues: {len(all_errors) + len(all_warnings) + len(all_ignored_warnings)}")
    print(f"Results saved to: {output_file}")
    
    # ANSI color codes
    RED = '\033[91m'
    GREEN = '\033[92m'
    RESET = '\033[0m'
    
    # Final result display
    print("\n" + "="*50)
    
    # Check for errors first (highest priority)
    if len(all_errors) > 0:
        print(f"{RED}COMPILE FAIL!! Fix *E errors first{RESET}")
        print(f"Found {len(all_errors)} error(s) that must be fixed.")
        if len(all_warnings) > 0:
            print(f"Also found {len(all_warnings)} warning(s) to clean.")
    
    # Check for warnings if no errors
    elif len(all_warnings) > 0:
        print(f"{RED}FAIL!! please clean *W{RESET}")
        print(f"Found {len(all_warnings)} active warning(s) that need to be fixed.")
    
    # All clear
    else:
        print(f"{GREEN}PASS{RESET}")
        print("No errors or active warnings found in ncverilog.log")
        if len(all_ignored_warnings) > 0:
            print(f"(Note: {len(all_ignored_warnings)} warning(s) were ignored)")
    
    print("="*50)

if __name__ == "__main__":
    main()
