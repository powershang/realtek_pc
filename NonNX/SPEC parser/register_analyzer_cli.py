#!/usr/bin/env python3
"""
Register Signal Analyzer - CLI Version
Command-line interface for analyzing register signals
No GUI dependencies, pure command-line tool

Features:
  - Parse Verilog regfile and RTD files
  - Calculate signal values from register addresses
  - Multi-channel address mapping (0x180c2, 0x180c3, 0x180c4, 0x180c5)
  - Support 0x18 and 0xb8 address prefix equivalence
  - Compare two RTD files to find differences
  - Export RTD output files
  - Filter results by signal name or address

Usage:
  # Analyze register signals
  python register_analyzer_cli.py regfile.v rtdfile.tbl
  
  # Save analysis results to file
  python register_analyzer_cli.py regfile.v rtdfile.tbl -o results.txt
  
  # Filter signals
  python register_analyzer_cli.py regfile.v rtdfile.tbl -f "signal_name"
  
  # Compare two RTD files (register-level only)
  python register_analyzer_cli.py --compare file1.tbl file2.tbl
  
  # Compare two RTD files with signal analysis (recommended)
  python register_analyzer_cli.py regfile.v file1.tbl --compare file2.tbl
  
  # Compare and save results
  python register_analyzer_cli.py regfile.v file1.tbl --compare file2.tbl -o comparison.txt
  
  # Export RTD output
  python register_analyzer_cli.py regfile.v rtdfile.tbl --export-rtd output.tbl
  
  # Custom address mapping
  python register_analyzer_cli.py regfile.v rtdfile.tbl --base-prefix 180c6 --prefixes "180c2,180c3,180c4,180c5,180c6"
  
  # Verbose mode
  python register_analyzer_cli.py regfile.v rtdfile.tbl -v

Author: Enhanced CLI tool for register analysis
Version: 2.0 (with RTD comparison feature)
"""

import argparse
import re
from collections import defaultdict
from typing import Dict, List, NamedTuple, Set
import os
import sys

class SignalMapping(NamedTuple):
    signal_name: str
    register_name: str
    bit_range: str
    start_bit: int
    end_bit: int

class RegisterAnalyzerCLI:
    def __init__(self):
        self.signal_mappings: List[SignalMapping] = []
        self.address_values: Dict[str, int] = {}
        self.results: Dict[str, Dict[str, Dict]] = {}
        
        # Address mapping configuration
        self.address_prefixes = ['180c2', '180c3', '180c4', '180c5']
        self.base_prefix = '180c2'
        self.enable_multi_channel = True
    
    def parse_regfile(self, regfile_path: str) -> int:
        """Parse the Verilog regfile to extract signal-to-register mappings"""
        self.signal_mappings = []
        assign_pattern = r'assign\s+(\w+)\s*=\s*(reg[0-9a-fA-F]+)\[(\d+):?(\d+)?\];'
        
        try:
            with open(regfile_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    match = re.match(assign_pattern, line)
                    if match:
                        signal_name = match.group(1)
                        register_name = match.group(2)
                        
                        if match.group(4):
                            start_bit = int(match.group(3))
                            end_bit = int(match.group(4))
                            bit_range = f"[{start_bit}:{end_bit}]"
                        else:
                            start_bit = end_bit = int(match.group(3))
                            bit_range = f"[{start_bit}]"
                        
                        mapping = SignalMapping(
                            signal_name=signal_name,
                            register_name=register_name,
                            bit_range=bit_range,
                            start_bit=start_bit,
                            end_bit=end_bit
                        )
                        self.signal_mappings.append(mapping)
            
            return len(self.signal_mappings)
        except Exception as e:
            print(f"Error parsing RegIF file: {e}", file=sys.stderr)
            return 0
    
    def parse_rtd_file(self, rtd_path: str) -> int:
        """Parse the RTD file to extract address-to-value mappings"""
        self.address_values = {}
        rtd_pattern = r'rtd_outl\(0x([0-9a-fA-F]+),0x([0-9a-fA-F]+)\);'
        
        try:
            with open(rtd_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    match = re.match(rtd_pattern, line)
                    if match:
                        address = match.group(1).lower()
                        value = int(match.group(2), 16)
                        self.address_values[address] = value
            
            return len(self.address_values)
        except Exception as e:
            print(f"Error parsing RTD file: {e}", file=sys.stderr)
            return 0
    
    def parse_rtd_file_standalone(self, rtd_path: str) -> Dict[str, int]:
        """Parse RTD file and return address-value mappings without modifying internal state"""
        address_values = {}
        rtd_pattern = r'rtd_outl\(0x([0-9a-fA-F]+),0x([0-9a-fA-F]+)\);'
        
        try:
            with open(rtd_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    match = re.match(rtd_pattern, line)
                    if match:
                        address = match.group(1).lower()
                        value = int(match.group(2), 16)
                        address_values[address] = value
            
            return address_values
        except Exception as e:
            print(f"Error parsing RTD file: {e}", file=sys.stderr)
            return {}
    
    def extract_bit_field(self, value: int, start_bit: int, end_bit: int) -> int:
        """Extract bit field from a value"""
        if start_bit == end_bit:
            return (value >> start_bit) & 1
        else:
            mask = (1 << (start_bit - end_bit + 1)) - 1
            return (value >> end_bit) & mask
    
    def convert_address_to_base(self, address: str) -> str:
        """Convert address to base prefix for signal mapping lookup"""
        address_lower = address.lower()
        
        # Treat 0xb8 and 0x18 as equivalent - convert b8 to 18
        if address_lower.startswith('b8'):
            address_lower = '18' + address_lower[2:]
        
        if self.enable_multi_channel:
            for prefix in self.address_prefixes:
                if address_lower.startswith(prefix) and prefix != self.base_prefix:
                    suffix = address_lower[len(prefix):]
                    return self.base_prefix + suffix
        
        return address_lower
    
    def is_supported_address_prefix(self, address: str) -> bool:
        """Check if address uses supported prefix"""
        address_lower = address.lower()
        # Treat 0xb8 and 0x18 as equivalent - convert b8 to 18
        if address_lower.startswith('b8'):
            address_lower = '18' + address_lower[2:]
        return any(address_lower.startswith(prefix) for prefix in self.address_prefixes)
    
    def calculate_signal_values(self):
        """Calculate actual signal values based on mappings and RTD values"""
        results = defaultdict(dict)
        
        for address, register_value in self.address_values.items():
            if self.enable_multi_channel and self.is_supported_address_prefix(address):
                base_address = self.convert_address_to_base(address)
                
                for mapping in self.signal_mappings:
                    mapping_addr = mapping.register_name[3:]
                    
                    if mapping_addr == base_address:
                        signal_value = self.extract_bit_field(
                            register_value,
                            mapping.start_bit,
                            mapping.end_bit
                        )
                        
                        display_register_name = f"reg{address}"
                        
                        results[address][mapping.signal_name] = {
                            'value': signal_value,
                            'register_value': hex(register_value),
                            'bit_range': mapping.bit_range,
                            'register_name': display_register_name,
                            'start_bit': mapping.start_bit,
                            'end_bit': mapping.end_bit
                        }
            else:
                for mapping in self.signal_mappings:
                    reg_addr = mapping.register_name[3:]
                    
                    if reg_addr == address:
                        signal_value = self.extract_bit_field(
                            register_value,
                            mapping.start_bit,
                            mapping.end_bit
                        )
                        
                        results[address][mapping.signal_name] = {
                            'value': signal_value,
                            'register_value': hex(register_value),
                            'bit_range': mapping.bit_range,
                            'register_name': mapping.register_name,
                            'start_bit': mapping.start_bit,
                            'end_bit': mapping.end_bit
                        }
        
        self.results = dict(results)
    
    def display_results(self, filter_text: str = '', output_file=None):
        """Display or save the analysis results"""
        if not self.results:
            print("No results to display.")
            return
        
        output = sys.stdout if output_file is None else output_file
        
        # Header
        print("=" * 100, file=output)
        print("Register Signal Analysis Results", file=output)
        print("=" * 100, file=output)
        print("", file=output)
        
        total_signals = 0
        displayed_addresses = 0
        
        for address in sorted(self.results.keys()):
            signals = self.results[address]
            if not signals:
                continue
            
            # Apply filter if specified
            if filter_text:
                filtered_signals = {}
                for signal_name, signal_info in signals.items():
                    if (filter_text.lower() in signal_name.lower() or
                        filter_text.lower() in address or
                        filter_text.lower() in signal_info['register_name'].lower()):
                        filtered_signals[signal_name] = signal_info
                if not filtered_signals:
                    continue
                signals = filtered_signals
            
            displayed_addresses += 1
            total_signals += len(signals)
            
            # Address header
            register_value = signals[list(signals.keys())[0]]['register_value']
            print(f"=== Address 0x{address.upper()} (Value: {register_value}) ===", file=output)
            
            # Sort signals by bit position (high to low)
            sorted_signals = sorted(signals.items(), key=lambda x: x[1]['start_bit'], reverse=True)
            
            for signal_name, signal_info in sorted_signals:
                line = f"{signal_name:<40} = {signal_info['register_name']}{signal_info['bit_range']:<12} = {signal_info['value']:<6} (0x{signal_info['value']:x})"
                print(line, file=output)
            
            print("", file=output)
        
        # Summary
        print("=" * 100, file=output)
        summary = f"Summary: {total_signals} signals across {displayed_addresses} addresses"
        if filter_text:
            summary += f" (filtered by '{filter_text}')"
        print(summary, file=output)
        print("=" * 100, file=output)
    
    def export_rtd(self, output_file):
        """Export RTD_OUTL statements"""
        if not self.results:
            print("No results to export.")
            return
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("// Generated RTD_OUTL Statements\n")
            f.write("// Register Signal Analyzer - CLI Version\n\n")
            
            for address in sorted(self.address_values.keys()):
                value = self.address_values[address]
                f.write(f"rtd_outl(0x{address.upper()},{value:#010x});\n")
            
            f.write(f"\n// Total: {len(self.address_values)} addresses\n")
    
    def compare_rtd_files(self, file1_path: str, file2_path: str, regfile_path: str = None, output_file=None):
        """Compare two RTD files and display differences with signal-level details if regfile provided"""
        # Parse both files
        values1 = self.parse_rtd_file_standalone(file1_path)
        values2 = self.parse_rtd_file_standalone(file2_path)
        
        if not values1:
            print(f"Error: No values found in {file1_path}", file=sys.stderr)
            return
        if not values2:
            print(f"Error: No values found in {file2_path}", file=sys.stderr)
            return
        
        # Parse regfile if provided for signal-level analysis
        has_signal_mappings = False
        if regfile_path:
            mapping_count = self.parse_regfile(regfile_path)
            has_signal_mappings = mapping_count > 0
            if not has_signal_mappings:
                print(f"Warning: No signal mappings found in {regfile_path}, showing register-level comparison only", file=sys.stderr)
        
        output = sys.stdout if output_file is None else output_file
        
        # Get all unique addresses
        all_addresses = set(values1.keys()) | set(values2.keys())
        
        # Categorize differences
        only_in_file1 = []
        only_in_file2 = []
        different_values = []
        same_values = []
        
        for address in sorted(all_addresses):
            if address in values1 and address not in values2:
                only_in_file1.append((address, values1[address]))
            elif address not in values1 and address in values2:
                only_in_file2.append((address, values2[address]))
            elif values1[address] != values2[address]:
                different_values.append((address, values1[address], values2[address]))
            else:
                same_values.append((address, values1[address]))
        
        # Display header
        print("=" * 120, file=output)
        print("RTD Files Comparison", file=output)
        if has_signal_mappings:
            print("(with Signal-Level Analysis)", file=output)
        print("=" * 120, file=output)
        print(f"File 1: {file1_path}", file=output)
        print(f"File 2: {file2_path}", file=output)
        if regfile_path:
            print(f"RegFile: {regfile_path}", file=output)
        print("=" * 120, file=output)
        print("", file=output)
        
        # Display differences
        if different_values:
            print(f"[Different Values] ({len(different_values)} addresses)", file=output)
            print("=" * 120, file=output)
            
            for address, val1, val2 in different_values:
                diff = val2 - val1
                diff_sign = "+" if diff >= 0 else ""
                
                # Display register-level info
                print(f"\nAddress: 0x{address.upper()}", file=output)
                print(f"  File 1: {val1:#010x} ({val1})", file=output)
                print(f"  File 2: {val2:#010x} ({val2})", file=output)
                print(f"  Diff:   {diff_sign}{diff:#010x} ({diff_sign}{diff})", file=output)
                
                # Display signal-level info if available
                if has_signal_mappings:
                    # Find matching signals for this address
                    base_address = self.convert_address_to_base(address)
                    matched_signals = []
                    
                    for mapping in self.signal_mappings:
                        mapping_addr = mapping.register_name[3:]  # Remove 'reg' prefix
                        
                        if (self.enable_multi_channel and self.is_supported_address_prefix(address) and 
                            mapping_addr == base_address) or (mapping_addr == address):
                            
                            # Extract signal values from both register values
                            signal_val1 = self.extract_bit_field(val1, mapping.start_bit, mapping.end_bit)
                            signal_val2 = self.extract_bit_field(val2, mapping.start_bit, mapping.end_bit)
                            
                            if signal_val1 != signal_val2:
                                matched_signals.append((mapping, signal_val1, signal_val2))
                    
                    if matched_signals:
                        print(f"\n  Changed Signals:", file=output)
                        # Sort by bit position
                        matched_signals.sort(key=lambda x: x[0].start_bit, reverse=True)
                        for mapping, sig_val1, sig_val2 in matched_signals:
                            sig_diff = sig_val2 - sig_val1
                            sig_diff_sign = "+" if sig_diff >= 0 else ""
                            print(f"    {mapping.signal_name:<40} {mapping.bit_range:<12} File1: {sig_val1:<6} (0x{sig_val1:x})  File2: {sig_val2:<6} (0x{sig_val2:x})  Diff: {sig_diff_sign}{sig_diff}", file=output)
                    else:
                        if self.is_supported_address_prefix(address) or any(m.register_name[3:] == address for m in self.signal_mappings):
                            print(f"  No signal changes (bit-level XOR shows change but no mapped signals affected)", file=output)
                
                print("-" * 120, file=output)
            
            print("", file=output)
        
        if only_in_file1:
            print(f"[Only in File 1] ({len(only_in_file1)} addresses)", file=output)
            print("-" * 120, file=output)
            print(f"{'Address':<20} {'Value':<30}", file=output)
            print("-" * 120, file=output)
            for address, value in only_in_file1:
                print(f"0x{address.upper():<18} {value:#010x} ({value})", file=output)
            print("", file=output)
        
        if only_in_file2:
            print(f"[Only in File 2] ({len(only_in_file2)} addresses)", file=output)
            print("-" * 120, file=output)
            print(f"{'Address':<20} {'Value':<30}", file=output)
            print("-" * 120, file=output)
            for address, value in only_in_file2:
                print(f"0x{address.upper():<18} {value:#010x} ({value})", file=output)
            print("", file=output)
        
        # Summary
        print("=" * 120, file=output)
        print("Summary:", file=output)
        print(f"  Total addresses (File 1): {len(values1)}", file=output)
        print(f"  Total addresses (File 2): {len(values2)}", file=output)
        print(f"  Same settings: {len(same_values)}", file=output)
        print(f"  Different settings: {len(different_values)}", file=output)
        print(f"  Only in file 1: {len(only_in_file1)}", file=output)
        print(f"  Only in file 2: {len(only_in_file2)}", file=output)
        print("=" * 120, file=output)

def main():
    parser = argparse.ArgumentParser(
        description='Register Signal Analyzer - CLI Version',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Basic analysis
  %(prog)s regfile.v rtdfile.tbl
  
  # Save results to file
  %(prog)s regfile.v rtdfile.tbl -o results.txt
  
  # Filter signals
  %(prog)s regfile.v rtdfile.tbl -f "signal_name"
  
  # Export RTD output
  %(prog)s regfile.v rtdfile.tbl --export-rtd output.tbl
  
  # Compare two RTD files (register-level only)
  %(prog)s --compare file2.tbl file1.tbl
  
  # Compare two RTD files with signal analysis
  %(prog)s regfile.v --compare file1.tbl file2.tbl
  
  # Compare and save to file
  %(prog)s regfile.v --compare file1.tbl file2.tbl -o comparison.txt
  
  # Configure address mapping
  %(prog)s regfile.v rtdfile.tbl --base-prefix 180c6 --prefixes "180c2,180c3,180c4,180c5,180c6"
        '''
    )
    
    # Optional arguments for mode selection
    parser.add_argument('--compare', metavar='FILE2', help='Compare mode: compare two RTD files (specify second file)')
    
    # Positional arguments (required for normal mode, optional for compare mode)
    parser.add_argument('regfile', nargs='?', help='RegIF Verilog file (.v) or first RTD file for comparison')
    parser.add_argument('rtdfile', nargs='?', help='RTD_OUTL file (.tbl)')
    
    # Optional arguments
    parser.add_argument('-o', '--output', help='Output file for analysis results or comparison')
    parser.add_argument('-f', '--filter', help='Filter signals by name or address')
    parser.add_argument('--export-rtd', help='Export RTD_OUTL statements to file')
    parser.add_argument('--base-prefix', default='180c2', help='Base address prefix (default: 180c2)')
    parser.add_argument('--prefixes', help='Comma-separated address prefixes (default: 180c2,180c3,180c4,180c5)')
    parser.add_argument('--disable-multi-channel', action='store_true', help='Disable multi-channel address mapping')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Create analyzer
    analyzer = RegisterAnalyzerCLI()
    
    # Check if in compare mode
    if args.compare:
        # Compare mode: compare two RTD files
        if not args.regfile:
            print("Error: First RTD file is required for comparison", file=sys.stderr)
            return 1
        
        # Determine if regfile is actually a regfile.v or just the first RTD file
        regfile_for_analysis = None
        if args.regfile.endswith('.v'):
            # User provided regfile.v for signal analysis
            regfile_for_analysis = args.regfile
            if not args.rtdfile:
                print("Error: When providing regfile.v, you need to specify first RTD file as second argument", file=sys.stderr)
                print("Usage: program regfile.v --compare file1.tbl file2.tbl", file=sys.stderr)
                return 1
            file1 = args.rtdfile
            file2 = args.compare
        else:
            # User only provided RTD files, no signal analysis
            file1 = args.regfile
            file2 = args.compare
        
        # Validate files
        if regfile_for_analysis and not os.path.exists(regfile_for_analysis):
            print(f"Error: RegIF file not found: {regfile_for_analysis}", file=sys.stderr)
            return 1
            
        if not os.path.exists(file1):
            print(f"Error: First RTD file not found: {file1}", file=sys.stderr)
            return 1
        
        if not os.path.exists(file2):
            print(f"Error: Second RTD file not found: {file2}", file=sys.stderr)
            return 1
        
        # Configure address mapping
        analyzer.base_prefix = args.base_prefix
        if args.prefixes:
            analyzer.address_prefixes = [p.strip().lower() for p in args.prefixes.split(',')]
        analyzer.enable_multi_channel = not args.disable_multi_channel
        
        if args.verbose:
            print(f"Comparing RTD files:")
            if regfile_for_analysis:
                print(f"  RegFile: {regfile_for_analysis} (signal-level analysis enabled)")
            print(f"  File 1: {file1}")
            print(f"  File 2: {file2}")
            print()
        
        # Perform comparison
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                analyzer.compare_rtd_files(file1, file2, regfile_for_analysis, f)
            print(f"Comparison results saved to: {args.output}")
        else:
            analyzer.compare_rtd_files(file1, file2, regfile_for_analysis)
        
        return 0
    
    # Normal analysis mode
    # Validate input files
    if not args.regfile:
        print("Error: RegIF file is required", file=sys.stderr)
        parser.print_help()
        return 1
    
    if not args.rtdfile:
        print("Error: RTD file is required", file=sys.stderr)
        parser.print_help()
        return 1
    
    if not os.path.exists(args.regfile):
        print(f"Error: RegIF file not found: {args.regfile}", file=sys.stderr)
        return 1
    
    if not os.path.exists(args.rtdfile):
        print(f"Error: RTD file not found: {args.rtdfile}", file=sys.stderr)
        return 1
    
    # Configure address mapping
    analyzer.base_prefix = args.base_prefix
    if args.prefixes:
        analyzer.address_prefixes = [p.strip().lower() for p in args.prefixes.split(',')]
    analyzer.enable_multi_channel = not args.disable_multi_channel
    
    if args.verbose:
        print(f"Configuration:")
        print(f"  Multi-channel mapping: {'Enabled' if analyzer.enable_multi_channel else 'Disabled'}")
        print(f"  Base prefix: {analyzer.base_prefix}")
        print(f"  Address prefixes: {', '.join(analyzer.address_prefixes)}")
        print()
    
    # Parse files
    if args.verbose:
        print(f"Parsing RegIF file: {args.regfile}")
    
    mapping_count = analyzer.parse_regfile(args.regfile)
    if mapping_count == 0:
        print("Warning: No signal mappings found in RegIF file", file=sys.stderr)
        return 1
    
    if args.verbose:
        print(f"  Found {mapping_count} signal mappings")
        print(f"Parsing RTD file: {args.rtdfile}")
    
    address_count = analyzer.parse_rtd_file(args.rtdfile)
    if address_count == 0:
        print("Warning: No addresses found in RTD file", file=sys.stderr)
        return 1
    
    if args.verbose:
        print(f"  Found {address_count} addresses")
        print("Calculating signal values...")
    
    # Calculate signal values
    analyzer.calculate_signal_values()
    
    if args.verbose:
        total_signals = sum(len(signals) for signals in analyzer.results.values())
        print(f"  Calculated {total_signals} signal values")
        print()
    
    # Display results
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            analyzer.display_results(args.filter or '', f)
        print(f"Results saved to: {args.output}")
    else:
        analyzer.display_results(args.filter or '')
    
    # Export RTD if requested
    if args.export_rtd:
        analyzer.export_rtd(args.export_rtd)
        print(f"\nRTD output saved to: {args.export_rtd}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

