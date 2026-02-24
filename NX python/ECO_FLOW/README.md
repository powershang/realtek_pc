# SVN File Backup Tool

A Python utility for backing up modified files in SVN working directories and generating restore scripts.

## Features

- Automatically detects modified files in SVN working directory
- Creates timestamped backups of modified files
- Generates TCL restore scripts for easy file restoration
- Detailed logging with debug mode option
- Command-line interface for flexible usage

## Requirements

- Python 3.x
- SVN (Subversion) installed and accessible from command line
- Required Python packages:
  - argparse
  - logging
  - subprocess
  - shutil
  - os
  - datetime

## Installation

1. Clone or download this repository
2. Ensure you have Python 3.x installed
3. Make sure SVN is installed and accessible from command line

## Usage

Basic usage:
```bash
python FileToECO.py -o <output_directory>
```

Advanced usage with all options:
```bash
python FileToECO.py -w <working_directory> -o <output_directory> -d
```

### Command Line Arguments

- `-w, --work-dir`: SVN working directory (default: current directory)
- `-o, --output-dir`: Output directory path for backup files (required)
- `-d, --debug`: Enable debug mode for detailed logging

## How It Works

1. The script checks for modified files in the specified SVN working directory
2. Creates a timestamped backup directory
3. Copies all modified files to the backup directory
4. Generates a TCL restore script that can be used to restore files if needed
5. Provides detailed logging of all operations

## Output Structure

```
output_directory/
|-- modified_files_YYYYMMDD_HHMMSS/
|   |-- file1
|   |-- file2
|   +-- ...
+-- restore_files_YYYYMMDD_HHMMSS.tcl
```

## Logging

- Default logging includes basic operation information
- Debug mode (-d) provides detailed logging of all operations
- Logs include timestamps and operation details

## Error Handling

- Comprehensive error handling for file operations
- Detailed error messages in debug mode
- Continues operation even if individual file operations fail

## Notes

- Maintains original file permissions during backup
- Preserves file timestamps
- Generates executable TCL restore scripts
- Safe to run multiple times (creates new backup sets each time)

## Author

[Your Name]

## License

[Specify License] 