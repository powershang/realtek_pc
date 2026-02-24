# Register Signal Analyzer - CLI Version

Command-line interface for analyzing register signals without GUI dependencies.

## Features

- Parse RegIF Verilog files (.v) for signal mappings
- Parse RTD_OUTL files (.tbl) for address-value pairs
- Calculate signal values based on bit field extraction
- Support multi-channel address mapping
- Filter results by signal name or address
- Export results to text files
- Export RTD_OUTL statements
- No GUI dependencies - runs in pure command-line environment

## Installation

No additional packages required! Uses only Python standard library.

```bash
# Make sure you're using Python 3
python --version

# No pip install needed!
```

## Basic Usage

### 1. Simple Analysis

```bash
python register_analyzer_cli.py regfile.v rtdfile.tbl
```

### 2. Save Results to File

```bash
python register_analyzer_cli.py regfile.v rtdfile.tbl -o results.txt
```

### 3. Filter Signals

```bash
# Filter by signal name
python register_analyzer_cli.py regfile.v rtdfile.tbl -f "signal_name"

# Filter by address
python register_analyzer_cli.py regfile.v rtdfile.tbl -f "180c2"
```

### 4. Export RTD Output

```bash
python register_analyzer_cli.py regfile.v rtdfile.tbl --export-rtd output.tbl
```

### 5. Verbose Mode

```bash
python register_analyzer_cli.py regfile.v rtdfile.tbl -v
```

## Advanced Usage

### Multi-Channel Address Mapping

Configure address prefix mapping for multiple channels:

```bash
python register_analyzer_cli.py regfile.v rtdfile.tbl \
  --base-prefix 180c6 \
  --prefixes "180c2,180c3,180c4,180c5,180c6"
```

### Disable Multi-Channel Mapping

```bash
python register_analyzer_cli.py regfile.v rtdfile.tbl --disable-multi-channel
```

### Combine Options

```bash
python register_analyzer_cli.py regfile.v rtdfile.tbl \
  -o results.txt \
  -f "qos" \
  --export-rtd output.tbl \
  -v
```

## Command-Line Options

```
positional arguments:
  regfile               RegIF Verilog file (.v)
  rtdfile               RTD_OUTL file (.tbl)

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output file for analysis results
  -f FILTER, --filter FILTER
                        Filter signals by name or address
  --export-rtd EXPORT_RTD
                        Export RTD_OUTL statements to file
  --base-prefix BASE_PREFIX
                        Base address prefix (default: 180c2)
  --prefixes PREFIXES   Comma-separated address prefixes
                        (default: 180c2,180c3,180c4,180c5)
  --disable-multi-channel
                        Disable multi-channel address mapping
  -v, --verbose         Verbose output
```

## Examples with Your Files

### Example 1: Basic Analysis

```bash
python register_analyzer_cli.py dc_mc1_regfile.v QoS_384_4K120_v1.tbl
```

### Example 2: Save and Filter

```bash
python register_analyzer_cli.py dc_mc1_regfile.v QoS_384_4K120_v1.tbl \
  -o qos_analysis.txt \
  -f "qos"
```

### Example 3: Export Modified RTD

```bash
python register_analyzer_cli.py dc_mc1_regfile.v QoS_384_4K120_v1.tbl \
  --export-rtd QoS_384_4K120_modified.tbl
```

### Example 4: Compare Different RTD Files

```bash
# Analyze first file
python register_analyzer_cli.py dc_mc1_regfile.v QoS_384_4K120_v1.tbl -o v1_results.txt

# Analyze second file
python register_analyzer_cli.py dc_mc1_regfile.v QoS_384_4K120_0829_v1.tbl -o 0829_results.txt

# Compare with diff
diff v1_results.txt 0829_results.txt
```

## Running on Linux Workstation

```bash
# Activate virtual environment (if needed)
source myvenv/bin/activate.csh

# Run analyzer
python register_analyzer_cli.py dc_mc1_regfile.v QoS_384_4K120_v1.tbl -v
```

## Running with GRID (qrsh/qsub)

Create a shell script `run_analysis.sh`:

```bash
#!/bin/bash
module load python
source /your/path/to/myvenv/bin/activate.csh
python register_analyzer_cli.py dc_mc1_regfile.v QoS_384_4K120_v1.tbl -o results.txt
```

Submit to GRID:

```bash
qrsh -cwd -v run_analysis.sh
```

## Output Format

The CLI tool generates formatted output showing:
- Address with register value
- Signal name
- Register and bit range
- Signal value in decimal and hexadecimal

Example output:
```
================================================================================
Register Signal Analysis Results
================================================================================

=== Address 0x180C2800 (Value: 0x12345678) ===
signal_name_example                      = reg180c2800[31:28] = 1      (0x1)
another_signal                           = reg180c2800[27:24] = 2      (0x2)

================================================================================
Summary: 150 signals across 25 addresses
================================================================================
```

## Troubleshooting

### No Results Found

Check that:
- RegIF file contains `assign signal = regXXXX[bit:bit];` statements
- RTD file contains `rtd_outl(0xADDRESS,0xVALUE);` statements
- Address prefixes in RTD match those in RegIF (or configure mapping)

### Permission Denied

Make script executable:
```bash
chmod +x register_analyzer_cli.py
chmod +x run_analyzer_cli.sh
```

## Comparison with GUI Version

| Feature | GUI Version | CLI Version |
|---------|-------------|-------------|
| File parsing | ✓ | ✓ |
| Signal analysis | ✓ | ✓ |
| Multi-channel mapping | ✓ | ✓ |
| Filter signals | ✓ | ✓ |
| Export results | ✓ | ✓ |
| Edit signal values | ✓ | ✗ (planned) |
| Interactive UI | ✓ | ✗ |
| Batch processing | ✗ | ✓ |
| Remote SSH usage | ✗ | ✓ |
| Dependencies | tkinter | None |

## Future Enhancements

Planned features:
- Signal value editing via JSON configuration file
- Batch processing multiple RTD files
- Difference comparison between two analyses
- JSON/CSV output formats
- Configuration file support

## Support

For issues or questions, contact the tool maintainer.


