# NX Python Tools - Usage Guide

This document provides usage instructions and examples for all Python utilities in this project.

---

## Table of Contents

1. [ECO Flow Tools](#1-eco-flow-tools)
2. [Filelist Tools](#2-filelist-tools)
3. [GENTOP V2 Tools](#3-gentop-v2-tools)
4. [SEQCMD Tools](#4-seqcmd-tools)
5. [SYN Tools](#5-syn-tools)
6. [QOS Tools](#6-qos-tools)
7. [TEMP/Utility Tools](#7-temputility-tools)

---

## 1. ECO Flow Tools

### FileToECO.py
**Purpose:** Backup SVN modified files and generate restore scripts.

**Usage:**
```bash
python FileToECO.py -o <output_directory>
python FileToECO.py -w <working_directory> -o <output_directory> -d
```

**Options:**
- `-w, --work-dir`: SVN working directory (default: current directory)
- `-o, --output-dir`: Output directory for backup files (required)
- `-d, --debug`: Enable debug logging

**Example:**
```bash
# Basic backup
python FileToECO.py -o ./backup

# With debug mode and custom working directory
python FileToECO.py -w /project/rtl -o ./eco_backup -d
```

**Expected Output:**
- Copied files in the output directory
- `restore_files_YYYYMMDD_HHMMSS.tcl` - TCL restore script

---

## 2. Filelist Tools

### FileCMDList.py
**Purpose:** Execute commands in multiple directories from a path list.

**Usage:**
```bash
python FileCMDList.py "<command>" <path_list_file>
```

**Example:**
```bash
# Search for "pass" in test.log in all directories
python FileCMDList.py 'grep "pass" test.log' paths.list

# Find Python files in all directories
python FileCMDList.py "find . -name '*.py'" directories.txt
```

**Expected Output:**
```
Executing in /path/to/dir1: grep "pass" test.log
Output:
PASS: Test case 1

Executing in /path/to/dir2: grep "pass" test.log
Output:
PASS: Test case 2
```

---

### auto_fixed_unresolved.py
**Purpose:** Automatically fix unresolved design unit errors by adding missing files to filelist.

**Usage:**
```bash
python auto_fixed_unresolved.py <error_log> <reference_log> <filelist>
python auto_fixed_unresolved.py <error_log> <reference_log> <filelist> -o <output_file>
python auto_fixed_unresolved.py <error_log> <reference_log> <filelist> --insert-after "pattern"
```

**Options:**
- `-o, --output`: Output filelist name (default: update in-place)
- `-b, --backup`: Create backup (default: True)
- `--insert-after`: Insert missing files after this pattern

**Example:**
```bash
# Basic usage
python auto_fixed_unresolved.py compile.log all_files.log dc_mc_top.f

# With custom output
python auto_fixed_unresolved.py compile.log all_files.log dc_mc_top.f -o fixed.f
```

**Expected Output:**
```
Found unresolved module: mbist_wrapper
[OK] Found: mbist_wrapper -> $PROJECT_HOME/rtl/mbist/mbist_wrapper.v
Updated filelist saved: fixed.f
Total files added: 3
```

---

### dcmc_sync_filelist.py
**Purpose:** Extract mbist files from filelist, copy them locally, and update paths.

**Usage:**
```bash
python dcmc_sync_filelist.py <input.f> [source_path] [options]
python dcmc_sync_filelist.py <file1.f> <file2.f> [source_path] [options]
```

**Options:**
- `-o, --output-dir`: Output subdirectory (default: mbist_files)
- `-f, --filelist`: Output filelist name (default: mbist_filelist.f)
- `-u, --update-original`: Update original .f file to use local paths
- `-c, --copy-cells`: Extract and copy SRAM cell files
- `--cell-path`: SRAM cell source path

**Example:**
```bash
# Single file with auto-update
python dcmc_sync_filelist.py dc_mc_top.f /project/v1.2 -u

# Multiple files with SRAM cells
python dcmc_sync_filelist.py file1.f file2.f /project/v1.2 -u -c --cell-path /cells
```

**Expected Output:**
```
Found mbist path: $PROJECT_HOME/rtl/mbist/mbist_ctrl.v
Copied: /project/v1.2/rtl/mbist/mbist_ctrl.v -> mbist_files/mbist_ctrl.v
Generated filelist: mbist_filelist.f
Updated: dc_mc_top.f
  Replaced paths: 5 files
```

---

## 3. GENTOP V2 Tools

### rtk_conn_by_pattern.py
**Purpose:** Generate Realtek connection scripts by pattern matching ports in Verilog files.

**Usage:**
```bash
python rtk_conn_by_pattern.py <verilog_file> <port_types> <direction> "<pattern>"
```

**Port Types:** input, output, inout, wire (comma-separated)

**Direction:**
- `wire`: Generate connection scripts (receive port)
- `io`: Generate input/output declarations (send port)

**Example:**
```bash
# Generate wire declarations for output ports matching "dfi_*"
python rtk_conn_by_pattern.py design.v output wire "dfi_*"

# Generate I/O declarations for multiple patterns
python rtk_conn_by_pattern.py design.v input,output io "mc_*" "dfi_*"
```

**Expected Output:**
```
=== Output Analysis Results ===
Port: dfi_rddata
Bus Width: [31:0] (32 bits)
Connections:
  - dfi_inst.rddata (output)

=== All Realtek Conn Scripts ===
//==output==
// Module: dfi
// realtek conn dfi.rddata ""
```

---

### rtk_conn_by_comment.py
**Purpose:** Convert Verilog signals with `// realtekshane` comments to realtek format.

**Usage:**
```bash
python rtk_conn_by_comment.py <verilog_file>
```

**Comment Patterns:**
- `// realtekshane wire` - for wire signals
- `// realtekshane port <signal_name>` - for port signals

**Example:**
```bash
python rtk_conn_by_comment.py my_design.v
```

**Input Format:**
```verilog
wire my_signal;      // realtekshane wire
input [3:0] data;    // realtekshane port data
```

**Expected Output:**
```
//===input===
// realtek assign my_signal = 1'b0;
// realtek wire my_signal
// realtek input data.[3:0]

//===output===
// realtek output result.[7:0]
// realtek assign result = 8'd0;
```

---

### module_chk_port_diff.py
**Purpose:** Compare ports between two Verilog files and identify differences.

**Usage:**
```bash
python module_chk_port_diff.py <file1.v> <file2.v>
```

**Example:**
```bash
python module_chk_port_diff.py old_design.v new_design.v
```

**Expected Output:**
```
=== Comparing ports between old_design.v and new_design.v ===

Found module: my_module in old_design.v
Found module: my_module in new_design.v

=== Ports only in old_design.v ===
  input   [7:0]      old_signal                     (8 bits)

=== Ports only in new_design.v ===
  output  [3:0]      new_signal                     (4 bits)

=== Summary ===
Found 2 port differences
```

---

### module_wire_name_prefixer.py
**Purpose:** Add IP_NAME parameter prefixes to wire connections in Verilog modules.

**Usage:**
```bash
python module_wire_name_prefixer.py <input.v> <output.v> [--custom-prefix PREFIX]
```

**Example:**
```bash
python module_wire_name_prefixer.py design.v design_prefixed.v --custom-prefix "MY_IP"
```

**Expected Output:**
```
Processing file: design.v
Found 3 instances
Processing instance: inst_0 of type dcmc_tchk_pbk with IP_NAME: MC0RK0
  Found 10 port connections
  Successfully modified instance inst_0
Successfully processed. Output written to: design_prefixed.v
```

---

### rtk_conn_gen_align_bitwidth.py
**Purpose:** Compare ports and generate realtek annotations for alignment with bitwidth mismatch handling.

**Usage:**
```bash
python rtk_conn_gen_align_bitwidth.py <file1.v> <file2.v>
```

**Example:**
```bash
python rtk_conn_gen_align_bitwidth.py aaa.v bbb.v
```

**Expected Output:**
```
=== Comparing ports between aaa.v and bbb.v ===
Found 5 port differences

=== Alignment Options ===
1. Align to aaa.v (make bbb.v ports match aaa.v)
2. Align to bbb.v (make aaa.v ports match bbb.v)

Enter your choice (1 or 2): 1

=== Generated Realtek Annotations ===
// ===== Ports only in target - need input/output declarations =====
// realtek input new_signal.[7:0]
// realtek output result.[3:0]
```

---

### merge_dpi_pad.py
**Purpose:** Compare DPI pad files and update connection, wire, and assign files.

**Usage:**
```bash
python merge_dpi_pad.py <new_file.v> <old_file.v>
```

**Requires:** `PROJECT_HOME` environment variable

**Example:**
```bash
export PROJECT_HOME=/path/to/project
python merge_dpi_pad.py merlin10.v merlin10_raw.v
```

**Expected Output:**
```
=== Found 3 new inout signals ===
  inout      new_pad    (1 bits)

Generated Verilog Code:
// Module connections:
    .new_pad(new_pad),
// Wire declarations:
wire new_pad;
// Assign statements:
assign new_pad = 1'b1;

Updated File A: removed 2, added 3 connection lines
```

---

## 4. SEQCMD Tools

### seqcmd_latency_parser.py
**Purpose:** Analyze VODMA command latencies from ncverilog log files.

**Usage:**
```bash
python seqcmd_latency_parser.py <logfile> [options] <vodma_type1> [vodma_type2 ...]
```

**Options:**
- `-c`: Combined mode - treat all VODMA types as single client
- `-p`: Generate latency distribution plots
- `-t START_TIME`: Only analyze commands after this timestamp

**Example:**
```bash
# Single type analysis
python seqcmd_latency_parser.py ncverilog.log vodma1yrr

# Multiple types with plots
python seqcmd_latency_parser.py ncverilog.log -c -p vodma1yrr vodma1crr

# With time filter
python seqcmd_latency_parser.py ncverilog.log -t 3000000 vodma1yrr
```

**Expected Output:**
```
Vodma Command Latency Analysis for types: vodma1yrr, vodma1crr
================================================================
Tag        Type         Start Time   End Time     Latency
----------------------------------------------------------------
001        vodma1yrr    100000       100500       500
002        vodma1crr    100200       100800       600

Summary:
----------------------------------------
Total commands analyzed: 2
Average latency: 550.00 time units
Maximum latency: 600 time units
```

---

### tcheck_diff.py
**Purpose:** Compare tcheck patterns between two files.

**Usage:**
```bash
python tcheck_diff.py <file1> <file2>
```

**Example:**
```bash
python tcheck_diff.py old_tcheck.log new_tcheck.log
```

**Expected Output:**
```
Patterns only in the first file:
PATH module1/signal1 -tcheck

Patterns only in the second file:
PATH module2/signal2 -tcheck
```

---

## 5. SYN Tools

### run_syn_sta_lec_scan.py
**Purpose:** Automated synthesis flow controller with process monitoring.

**Usage:**
```bash
python run_syn_sta_lec_scan.py
```

**Configuration (in script):**
```python
self.config_need_step0 = 0  # VCSG LINT
self.config_need_step1 = 1  # SYNTHESIS
self.config_need_step2 = 1  # STATIC TIMING ANALYSIS
self.config_need_step3 = 1  # LOGIC EQUIVALENCE CHECK
self.config_need_step4 = 1  # SCAN INSERTION
self.config_need_step5 = 0  # PRE POWER ANALYSIS
```

**Expected Output:**
```
Starting Synthesis Flow Controller
Steps to execute: [step1, step2, step3, step4]
================================================================
STARTING STEP1: SYNTHESIS
Waiting for completion...
Status: Process PID 12345 running - SYNTHESIS running... (5 minutes elapsed)
...
SYNTHESIS COMPLETED!
================================================================
ENTIRE FLOW EXECUTION COMPLETED SUCCESSFULLY!
```

---

### dcmc_mbist_parsing.py
**Purpose:** Parse MBIST area data from synthesis reports.

**Usage:**
```bash
python dcmc_mbist_parsing.py                                  # Run demo
python dcmc_mbist_parsing.py <input_file>                     # Interactive mode
python dcmc_mbist_parsing.py <input_file> <pattern1> [pattern2] ...
python dcmc_mbist_parsing.py <input_file> <patterns> --debug
```

**Example:**
```bash
# Analyze multiple FIFO instances
python dcmc_mbist_parsing.py area_report.txt mc_fifo_top_inst_*

# Multiple patterns with debug
python dcmc_mbist_parsing.py area_report.txt mc_fifo_top_inst_* mc_ctl_top_inst_* --debug
```

**Expected Output:**
```
================================================================================
AREA BREAKDOWN ANALYSIS FOR: mc_fifo_top_inst_0
================================================================================

SUMMARY:
Total Area:           431843.8577
MBIST Area:            36151.1988 (8.4%)
Digital Area:         395692.6589 (91.6%)

DETAILED MBIST BREAKDOWN:
MBIST Instance Name                                    | Parent Path          | Area
------------------------------------------------------------------------------------------
mbist_mc_fifo_rdata_top_1024x132_inst                  | mc_fifo_exp2_inst    | 32044.8727 (7.4%)
mbist_mc_fifo_rdata_top_128x132_inst                   | mc_fifo_sys_inst     |  4106.3261 (1.0%)
```

---

## 6. QOS Tools

### qos_tbl_checker.py
**Purpose:** Analyze register signals from Verilog regfile and RTD files.

**Usage:**
```bash
# Basic analysis
python qos_tbl_checker.py regfile.v rtdfile.tbl

# Save results
python qos_tbl_checker.py regfile.v rtdfile.tbl -o results.txt

# Compare two RTD files
python qos_tbl_checker.py regfile.v file1.tbl --compare file2.tbl

# Filter signals
python qos_tbl_checker.py regfile.v rtdfile.tbl -f "signal_name"
```

**Example:**
```bash
python qos_tbl_checker.py mc_regif.v dic_Qos.tbl -o analysis.txt
```

**Expected Output:**
```
====================================================================================================
Register Signal Analysis Results
====================================================================================================

=== Address 0x180C2028 (Value: 0x00000100) ===
mcx2_mode                                = reg180c2028[9:8]    = 1      (0x1)
mcx2_en                                  = reg180c2028[0]      = 0      (0x0)

====================================================================================================
Summary: 150 signals across 45 addresses
====================================================================================================
```

---

## 7. TEMP/Utility Tools

### check_dic_qos.py
**Purpose:** Analyze and compare dic_Qos.tbl file versions across directories.

**Usage:**
```bash
python check_dic_qos.py [target_filename] [regif_file]
```

**Example:**
```bash
# Default search for dic_Qos.tbl
python check_dic_qos.py

# Custom filename and regif
python check_dic_qos.py dic_Qos.tbl ./hardware/rtl/mc_regif.v
```

**Expected Output:**
```
Found 2 different version(s)

[Version 1]
MD5: abc123def456...
Found in folders:
  - D:\project\folder1

[Version 2]
MD5: def789ghi012...
Found in folders:
  - D:\project\folder2

rtd_outl DIFFERENCES ANALYSIS:
  Address: 0xb80c2028
    [Version 1 - Golden]: 0x00000100
    [Version 2]:          0x00000300
    >>> Bit Field Differences:
        mcx2_mode     [9:8]     Golden: 0x1 (1)  vs  Version2: 0x3 (3)
```

---

### check_warnin.py
**Purpose:** Extract warnings and errors from ncverilog.log files.

**Usage:**
```bash
python check_warnin.py
```

**Expected Output:**
```
NCVERILOG Warning & Error Extractor
===================================
Processing: ncverilog.log
  Found 0 error(s)
  Found 5 active warning(s)
  Found 10 ignored warning(s)

==================================================
PASS
No errors or active warnings found in ncverilog.log
==================================================
```

---

### all_filename_prefix.py
**Purpose:** Rename .v files by replacing 'hd21' with 'hd22' and 'hdmi21' with 'hdmi22'.

**Usage:**
```bash
cd /path/to/verilog/files
python all_filename_prefix.py
```

**Expected Output:**
```
Found 10 .v file(s)
Files WITH hd21 or hdmi21 in filename (5 files):
  - hd21_module.v
  - hdmi21_top.v

SUCCESS Renamed: hd21_module.v -> hd22_module.v
SUCCESS Renamed: hdmi21_top.v -> hdmi22_top.v
Completed! Renamed 5 file(s)
```

---

### all_module_prefix.py
**Purpose:** Check and fix filename/module name consistency in Verilog files.

**Usage:**
```bash
python all_module_prefix.py
```

**Interactive Modes:**
1. Check only (default)
2. Check and fix mismatches

**Expected Output:**
```
Found 10 .v files
============================================================
OK: module1.v
   Filename and module name match: module1

MISMATCH: module2.v
   Filename: module2
   Module name: old_module2
   FIXED: Module name changed to module2
```

---

### temp.py (Batch Keyword Replace)
**Purpose:** Batch replace keywords in files using a config file.

**Usage:**
```bash
python temp.py <config_file> <files...> [--no-backup]
```

**Config File Format:**
```
old_keyword1    new_keyword1
old_keyword2    new_keyword2
```

**Example:**
```bash
python temp.py replacements.txt *.v --no-backup
```

**Expected Output:**
```
Keyword Replacement Tool
============================================================
Replacement rules (3):
  hd21 to hd22
  hdmi21 to hdmi22

Processed: design.v
No changes: other.v
============================================================
Processing complete: 5 files, 3 changed
```

---

### replace_inst_name.py
**Purpose:** Parse unresolved instance errors and apply name replacements.

**Usage:**
```bash
python replace_inst_name.py parse <error_file> [output_file]
python replace_inst_name.py rename <error_file>
python replace_inst_name.py test
```

**Example:**
```bash
# Parse unresolved instances
python replace_inst_name.py parse ncverilog.log

# Apply hd21->hd22 renames
python replace_inst_name.py rename ncverilog.log
```

**Expected Output:**
```
Found 5 unresolved instances:
File                    Line    Inst_Name               Design_Unit_Name
--------------------------------------------------------------------------------
video_retiming.v        751     rline_cnt_g2b           hd21_gray2bin_13b

Applying rename rules: [('hd21', 'hd22')]
  Replaced design unit: hd21_gray2bin_13b -> hd22_gray2bin_13b
  SUCCESS: File modified
```

---

### rdc.py
**Purpose:** Add display statements for debugging Verilog testbenches.

**Usage:**
```bash
python rdc.py <verilog_file>
```

**Example:**
```bash
python rdc.py testbench.v
```

**Expected Output:**
```
Modified file saved as testbench.v.modified
Added 10 delay displays, 5 wait task calls, 3 check task calls
```

---

### tbl_formate_chg_for_parser.py
**Purpose:** Convert rtd_inl format to rtd_outl format (GUI tool).

**Usage:**
```bash
python tbl_formate_chg_for_parser.py
```

**Conversion:**
```
Before: rtd_inl(0xb80c1040); //0x00000000
After:  rtd_outl(0xb80c1040,0x00000000);
```

---

### record_voice.py
**Purpose:** System audio recording tool (GUI application).

**Usage:**
```bash
python record_voice.py
```

**Features:**
- Record system audio (stereo mix)
- Configurable recording duration
- Save as WAV format

---

### proj_data.py
**Purpose:** Get SVN last changed dates for a list of project codes.

**Usage:**
```bash
python proj_data.py <list_filename.txt>
```

**Example:**
```bash
python proj_data.py project_codes.txt
```

**Expected Output:**
```
Done! Results have been written to svn_dates.txt

# svn_dates.txt content:
PROJECT001: 2024-01-15 10:30:00 +0800
PROJECT002: 2024-01-14 15:45:00 +0800
```

---

## Quick Reference Card

| Tool | Main Purpose | Quick Example |
|------|--------------|---------------|
| `FileToECO.py` | SVN backup | `python FileToECO.py -o ./backup` |
| `FileCMDList.py` | Batch commands | `python FileCMDList.py "cmd" paths.list` |
| `auto_fixed_unresolved.py` | Fix filelist | `python auto_fixed_unresolved.py err.log ref.log file.f` |
| `dcmc_sync_filelist.py` | Sync mbist files | `python dcmc_sync_filelist.py input.f /path -u` |
| `rtk_conn_by_pattern.py` | Port pattern match | `python rtk_conn_by_pattern.py design.v output wire "dfi_*"` |
| `rtk_conn_by_comment.py` | Comment conversion | `python rtk_conn_by_comment.py design.v` |
| `module_chk_port_diff.py` | Port comparison | `python module_chk_port_diff.py a.v b.v` |
| `seqcmd_latency_parser.py` | Latency analysis | `python seqcmd_latency_parser.py log vodma1yrr` |
| `dcmc_mbist_parsing.py` | MBIST area parsing | `python dcmc_mbist_parsing.py report.txt inst_*` |
| `qos_tbl_checker.py` | Register analysis | `python qos_tbl_checker.py regif.v rtd.tbl` |
| `check_dic_qos.py` | Version comparison | `python check_dic_qos.py` |
| `check_warnin.py` | Extract warnings | `python check_warnin.py` |
| `run_syn_sta_lec_scan.py` | Synthesis flow | `python run_syn_sta_lec_scan.py` |

---

*Generated for NX Python Tools Collection*
