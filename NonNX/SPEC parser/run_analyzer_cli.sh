#!/bin/bash
# Example script for running Register Signal Analyzer CLI
# Make executable: chmod +x run_analyzer_cli.sh

# Example 1: Basic analysis (display to screen)
echo "Example 1: Basic analysis"
python register_analyzer_cli.py dc_mc1_regfile.v QoS_384_4K120_v1.tbl

# Example 2: Save results to file
echo ""
echo "Example 2: Save results to file"
python register_analyzer_cli.py dc_mc1_regfile.v QoS_384_4K120_v1.tbl -o results.txt

# Example 3: Filter specific signals
echo ""
echo "Example 3: Filter signals containing 'qos'"
python register_analyzer_cli.py dc_mc1_regfile.v QoS_384_4K120_v1.tbl -f "qos"

# Example 4: Export RTD output
echo ""
echo "Example 4: Export RTD statements"
python register_analyzer_cli.py dc_mc1_regfile.v QoS_384_4K120_v1.tbl --export-rtd output.tbl

# Example 5: Verbose mode with custom configuration
echo ""
echo "Example 5: Verbose with custom address mapping"
python register_analyzer_cli.py dc_mc1_regfile.v QoS_384_4K120_v1.tbl \
  --base-prefix 180c6 \
  --prefixes "180c2,180c3,180c4,180c5,180c6" \
  -v -o results_custom.txt

