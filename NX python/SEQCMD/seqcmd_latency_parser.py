"""
VODMA Command Latency Analyzer
=============================

This script analyzes VODMA command latencies from ncverilog log files.

Features:
---------
- Tracks VODMA commands and their corresponding responses
- Calculates latency between command issue and completion
- Two analysis modes:
  * Separate mode: Analyze each VODMA type independently
  * Combined mode: Treat multiple VODMA types as a single client
- Provides detailed analysis including:
  * Command-by-command latency breakdown
  * Average latency across all commands
  * Maximum latency with detailed information
  * Total number of commands analyzed
  * Optional latency distribution plots (-p flag) saved to 'plots' directory
- Time filtering: Analyze commands after specified timestamp (-t flag)

Usage:
------
python seqcmd_parser.py <logfile> [-c] [-p] [-t START_TIME] <vodma_type1> [vodma_type2 ...]
Options:
  -c : Combined mode - treat all VODMA types as single client
  -p : Generate and save latency distribution plots to 'plots' directory
  -t START_TIME : Only analyze commands after this timestamp

Examples:
- Single type:     python seqcmd_parser.py ncverilog.log vodma1yrr
- Separate types:  python seqcmd_parser.py ncverilog.log vodma1yrr vodma1crr
- Combined types:  python seqcmd_parser.py ncverilog.log -c vodma1yrr vodma1crr
- With plots:      python seqcmd_parser.py ncverilog.log -p vodma1yrr
- Combined plots:  python seqcmd_parser.py ncverilog.log -c -p vodma1yrr vodma1crr
- Time filter:     python seqcmd_parser.py ncverilog.log -t 3000000 vodma1yrr
"""

import re
from typing import Dict, List, Tuple
import sys
from collections import defaultdict
import os
try:
    import matplotlib.pyplot as plt
    import numpy as np
    PLOT_AVAILABLE = True
except ImportError:
    PLOT_AVAILABLE = False

class VodmaLatencyAnalyzer:
    def __init__(self, vodma_types: List[str], combined_mode: bool = False, plot_enabled: bool = False, start_time: int = 0):
        self.vodma_commands: Dict[str, Tuple[int, str]] = {}  # tag -> (timestamp, vodma_type)
        self.latencies: List[Tuple[str, str, int, int, int]] = []  # (tag, vodma_type, start_time, end_time, latency)
        self.vodma_types = vodma_types
        self.type_counts = defaultdict(int)  # Count of commands per type
        self.combined_mode = combined_mode
        self.plot_enabled = plot_enabled and PLOT_AVAILABLE
        self.start_time = start_time
        
        # Create plots directory if plotting is enabled
        if self.plot_enabled:
            os.makedirs('plots', exist_ok=True)

    def save_plot(self, fig, filename):
        """Save plot to the plots directory"""
        filepath = os.path.join('plots', filename)
        fig.savefig(filepath)
        plt.close(fig)
        print(f"Plot saved to: {filepath}")

    def parse_line(self, line: str):
        # Extract timestamp at the start of the line
        timestamp_match = re.match(r'^(\d+)', line)
        if not timestamp_match:
            return
        
        timestamp = int(timestamp_match.group(1))
        
        # Skip if before start time
        if timestamp < self.start_time:
            return
        
        # Look for vodma commands
        for vodma_type in self.vodma_types:
            vodma_cmd_match = re.search(r'\[seqcmd\].*\[' + re.escape(vodma_type) + r'\s*\].*tag\[(\d+)\]', line)
            if vodma_cmd_match:
                tag = vodma_cmd_match.group(1)
                self.vodma_commands[tag] = (timestamp, vodma_type)
                return

        # Look for last data responses
        last_data_match = re.search(r'\[data\].*tag\[(\d+)\].*last', line)
        if last_data_match:
            tag = last_data_match.group(1)
            if tag in self.vodma_commands:
                start_time, vodma_type = self.vodma_commands[tag]
                latency = timestamp - start_time
                self.latencies.append((tag, vodma_type, start_time, timestamp, latency))
                self.type_counts[vodma_type] += 1
                del self.vodma_commands[tag]

    def plot_latency_distribution(self):
        if not self.plot_enabled:
            return

        # For combined mode
        if self.combined_mode:
            fig = plt.figure(figsize=(12, 6))
            latencies = [lat[4] for lat in self.latencies]
            
            # Histogram
            plt.subplot(121)
            plt.hist(latencies, bins=30, edgecolor='black')
            plt.title('Latency Distribution (All Types Combined)')
            plt.xlabel('Latency (time units)')
            plt.ylabel('Frequency')
            
            # Add mean and median lines
            mean_latency = np.mean(latencies)
            median_latency = np.median(latencies)
            plt.axvline(mean_latency, color='r', linestyle='dashed', linewidth=1, label=f'Mean: {mean_latency:.2f}')
            plt.axvline(median_latency, color='g', linestyle='dashed', linewidth=1, label=f'Median: {median_latency:.2f}')
            plt.legend()
            
            # Box plot
            plt.subplot(122)
            plt.boxplot(latencies, labels=['Combined'])
            plt.title('Latency Box Plot')
            plt.ylabel('Latency (time units)')
            
            plt.tight_layout()
            self.save_plot(fig, 'combined_latency_distribution.png')
        
        # For separate mode
        else:
            # Plot for each type
            for vtype in self.vodma_types:
                type_latencies = [lat[4] for lat in self.latencies if lat[1] == vtype]
                if not type_latencies:
                    continue
                
                fig = plt.figure(figsize=(12, 6))
                
                # Histogram
                plt.subplot(121)
                plt.hist(type_latencies, bins=30, edgecolor='black')
                plt.title(f'Latency Distribution - {vtype}')
                plt.xlabel('Latency (time units)')
                plt.ylabel('Frequency')
                
                # Add mean and median lines
                mean_latency = np.mean(type_latencies)
                median_latency = np.median(type_latencies)
                plt.axvline(mean_latency, color='r', linestyle='dashed', linewidth=1, label=f'Mean: {mean_latency:.2f}')
                plt.axvline(median_latency, color='g', linestyle='dashed', linewidth=1, label=f'Median: {median_latency:.2f}')
                plt.legend()
                
                # Box plot
                plt.subplot(122)
                plt.boxplot(type_latencies, labels=[vtype])
                plt.title('Latency Box Plot')
                plt.ylabel('Latency (time units)')
                
                plt.tight_layout()
                self.save_plot(fig, f'{vtype}_latency_distribution.png')
            
            # Comparison plot for all types
            if len(self.vodma_types) > 1:
                fig = plt.figure(figsize=(12, 6))
                data = []
                labels = []
                for vtype in self.vodma_types:
                    type_latencies = [lat[4] for lat in self.latencies if lat[1] == vtype]
                    if type_latencies:
                        data.append(type_latencies)
                        labels.append(vtype)
                
                plt.boxplot(data, labels=labels)
                plt.title('Latency Comparison Across Types')
                plt.ylabel('Latency (time units)')
                plt.xticks(rotation=45)
                plt.tight_layout()
                self.save_plot(fig, 'type_comparison.png')

    def analyze_file(self, filename: str):
        try:
            with open(filename, 'r') as f:
                for line in f:
                    self.parse_line(line.strip())
            
            if self.combined_mode:
                self._print_combined_analysis()
            else:
                self._print_separate_analysis()
            
            self.plot_latency_distribution()

        except FileNotFoundError:
            print(f"Error: File {filename} not found.")
        except Exception as e:
            print(f"Error processing file: {str(e)}")

    def _print_combined_analysis(self):
        if not self.latencies:
            print(f"\nNo matching commands found with responses after timestamp {self.start_time}.")
            return

        print(f"\nVodma Command Latency Analysis (Combined mode for: {', '.join(self.vodma_types)})")
        print(f"Analysis starting from timestamp: {self.start_time}")
        print("=" * 60)
        print(f"{'Tag':<10} {'Start Time':<12} {'End Time':<12} {'Latency':<8}")
        print("-" * 60)
        
        for tag, _, start, end, latency in sorted(self.latencies, key=lambda x: x[2]):
            print(f"{tag:<10} {start:<12} {end:<12} {latency:<8}")
        
        avg_latency = sum(lat[4] for lat in self.latencies) / len(self.latencies)
        max_latency = max(lat[4] for lat in self.latencies)
        max_lat_cmd = next(lat for lat in self.latencies if lat[4] == max_latency)
        
        print("\nSummary:")
        print("-" * 40)
        print(f"Total commands analyzed: {len(self.latencies)}")
        print(f"Average latency: {avg_latency:.2f} time units")
        print(f"Maximum latency: {max_latency} time units")
        
        print("\nMax latency command details:")
        print(f"  Tag: {max_lat_cmd[0]}")
        print(f"  Start time: {max_lat_cmd[2]}")
        print(f"  End time: {max_lat_cmd[3]}")

    def _print_separate_analysis(self):
        if not self.latencies:
            print(f"\nNo matching commands found with responses after timestamp {self.start_time}.")
            return

        print(f"\nVodma Command Latency Analysis for types: {', '.join(self.vodma_types)}")
        print(f"Analysis starting from timestamp: {self.start_time}")
        print("=" * 80)
        print(f"{'Tag':<10} {'Type':<12} {'Start Time':<12} {'End Time':<12} {'Latency':<8}")
        print("-" * 80)
        
        for tag, vtype, start, end, latency in sorted(self.latencies, key=lambda x: x[2]):
            print(f"{tag:<10} {vtype:<12} {start:<12} {end:<12} {latency:<8}")
        
        avg_latency = sum(lat[4] for lat in self.latencies) / len(self.latencies)
        max_latency = max(lat[4] for lat in self.latencies)
        max_lat_cmd = next(lat for lat in self.latencies if lat[4] == max_latency)
        
        print("\nSummary:")
        print("-" * 40)
        print(f"Total commands analyzed: {len(self.latencies)}")
        print(f"Average latency: {avg_latency:.2f} time units")
        print(f"Maximum latency: {max_latency} time units")
        
        print("\nBreakdown by type:")
        for vtype, count in self.type_counts.items():
            type_latencies = [lat[4] for lat in self.latencies if lat[1] == vtype]
            type_avg = sum(type_latencies) / len(type_latencies)
            print(f"  {vtype}: {count} commands, avg latency: {type_avg:.2f}")
        
        print("\nMax latency command details:")
        print(f"  Tag: {max_lat_cmd[0]}")
        print(f"  Type: {max_lat_cmd[1]}")
        print(f"  Start time: {max_lat_cmd[2]}")
        print(f"  End time: {max_lat_cmd[3]}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python seqcmd_parser.py <logfile> [-c] [-p] [-t START_TIME] <vodma_type1> [vodma_type2 ...]")
        print("Options:")
        print("  -c : Combined mode - treat all VODMA types as single client")
        print("  -p : Generate and save latency distribution plots to 'plots' directory")
        print("  -t START_TIME : Only analyze commands after this timestamp")
        print("\nExamples:")
        print("  Single type:     python seqcmd_parser.py ncverilog.log vodma1yrr")
        print("  Separate types:  python seqcmd_parser.py ncverilog.log vodma1yrr vodma1crr")
        print("  Combined types:  python seqcmd_parser.py ncverilog.log -c vodma1yrr vodma1crr")
        print("  With plots:      python seqcmd_parser.py ncverilog.log -p vodma1yrr")
        print("  Combined plots:  python seqcmd_parser.py ncverilog.log -c -p vodma1yrr vodma1crr")
        print("  Time filter:     python seqcmd_parser.py ncverilog.log -t 3000000 vodma1yrr")
        print("  Order flexible:  python seqcmd_parser.py ncverilog.log vodma1yrr -t 3000000 -p")
        sys.exit(1)
    
    log_file = sys.argv[1]
    args = sys.argv[2:]
    
    # Initialize parameters
    combined_mode = False
    plot_enabled = False
    start_time = 0
    vodma_types = []
    
    # Process arguments
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == '-c':
            combined_mode = True
            i += 1
        elif arg == '-p':
            plot_enabled = True
            i += 1
        elif arg == '-t':
            if i + 1 >= len(args):
                print("Error: -t option requires a timestamp value")
                sys.exit(1)
            try:
                start_time = int(args[i + 1])
            except ValueError:
                print(f"Error: Invalid timestamp value '{args[i + 1]}'. Must be an integer.")
                sys.exit(1)
            i += 2  # Skip both -t and its value
        elif arg.startswith('-'):
            print(f"Error: Unknown option '{arg}'")
            sys.exit(1)
        else:
            # This must be a vodma type
            vodma_types.append(arg)
            i += 1
    
    if not vodma_types:
        print("Error: No VODMA types specified")
        sys.exit(1)
    
    if plot_enabled and not PLOT_AVAILABLE:
        print("Warning: Plotting requires matplotlib and numpy. Please install them first.")
        print("You can install them using: pip install matplotlib numpy")
        plot_enabled = False
    
    # Print parsed arguments for verification
    print("\nParsed arguments:")
    print(f"Log file: {log_file}")
    print(f"Start time: {start_time}")
    print(f"VODMA types: {', '.join(vodma_types)}")
    print(f"Combined mode: {combined_mode}")
    print(f"Plot enabled: {plot_enabled}\n")
    
    analyzer = VodmaLatencyAnalyzer(vodma_types, combined_mode, plot_enabled, start_time)
    analyzer.analyze_file(log_file)

if __name__ == "__main__":
    main()
