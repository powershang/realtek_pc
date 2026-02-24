#!/usr/bin/env python3
"""
Auto waveform extraction flow (busy200 or idle2busy200).

Usage:
  python3 auto_busy200.py            # busy200 (default)
  python3 auto_busy200.py idle2busy  # idle2busy200
"""

import subprocess
import sys
import re

DEFAULT_STRIP_PATH = "top/u_midas/main_top_apr_inst/main_top_inst/dc_mc_top_inst"
QQRSH = "qqrsh64"

# helpers

def run_step(label, cmd):
    """Run command, stream output live. Exit on failure."""
    print(f"\nSTEP : {label}")
    print(f"CMD  : {cmd}")
    ret = subprocess.run(cmd, shell=True)
    if ret.returncode != 0:
        print(f"\nERROR: exited with code {ret.returncode}")
        sys.exit(1)
    print(f"DONE: {label}")


def run_capture(label, cmd):
    """Run command, stream output live, also collect it. Exit on failure."""
    print(f"\nSTEP : {label}")
    print(f"CMD  : {cmd}")

    proc = subprocess.Popen(
        cmd, shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1
    )
    lines = []
    for line in proc.stdout:
        print(line, end="")
        lines.append(line)
    proc.wait()

    if proc.returncode != 0:
        print(f"\nERROR: exited with code {proc.returncode}")
        sys.exit(1)

    print(f"DONE: {label}")
    return "".join(lines)


def parse_begin_time(text):
    """
    Parse begin time from run_waveform_analysis output.

    Targets the line:
      idle2busy 200ns start from 439272ns to 439472ns roughly ...
      busy 200ns start from 569616ns to 569816ns roughly ...
    """
    m = re.search(r'start from\s+(\d+)ns', text, re.IGNORECASE)
    if m:
        return m.group(1)
    return None


def derive_ip(strip_path):
    """
    Strip trailing _inst or _apr_inst from the last path component.
    Example: dc_mc_top_inst becomes dc_mc_top
    """
    name = strip_path.rstrip("/").split("/")[-1]
    for suffix in ("_apr_inst", "_inst"):
        if name.endswith(suffix):
            name = name[: -len(suffix)]
            break
    return name


def run_extract(strip_path, begin_time, ip_name, wtype):
    """Run mm2_fsdbextract and auto-answer Y to copy prompt."""
    cmd = (
        f"mm2_fsdbextract"
        f" -s={strip_path}"
        f" -bt={begin_time}"
        f" -ip={ip_name}"
        f" -type={wtype}"
    )
    print(f"\nSTEP : mm2_fsdbextract ({wtype})")
    print(f"CMD  : {cmd}")

    proc = subprocess.Popen(
        cmd, shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True, bufsize=1
    )
    for line in proc.stdout:
        print(line, end="")
        if re.search(r'\(Y/N\)', line, re.IGNORECASE):
            print("AUTO: answering Y")
            proc.stdin.write("Y\n")
            proc.stdin.flush()

    proc.wait()
    if proc.returncode != 0:
        print(f"\nERROR: mm2_fsdbextract exited with code {proc.returncode}")
        sys.exit(1)
    print(f"DONE: mm2_fsdbextract ({wtype})")

# main

def main():
    # Determine flow type from argument
    mode = sys.argv[1] if len(sys.argv) > 1 else "busy"
    if "idle" in mode.lower():
        anal_cmd = f"{QQRSH} run_pre_pwr_anal_idle2busy200"
        wtype    = "idle2busy200"
    else:
        anal_cmd = f"{QQRSH} run_pre_pwr_anal_busy200"
        wtype    = "busy200"

    print(f"Auto waveform extraction: {wtype}")

    # Step 1
    run_step(anal_cmd, anal_cmd)

    # Step 2
    waveform_cmd = f"{QQRSH} run_waveform_analysis"
    output = run_capture(waveform_cmd, waveform_cmd)

    # Step 3: parse begin time
    print("\nSTEP : Parse begin time (-bt)")
    begin_time = parse_begin_time(output)
    if begin_time:
        print(f"AUTO: detected begin time {begin_time} ns")
    else:
        print("WARN: could not auto-detect begin time, check output above")
        begin_time = input("Enter begin time (-bt) manually: ").strip()

    # Step 4: confirm strip path
    print(f"\nSTEP : Confirm strip path (-s)")
    print(f"Default: {DEFAULT_STRIP_PATH}")
    user_s = input("Press Enter to use default, or type new path: ").strip()
    strip_path = user_s if user_s else DEFAULT_STRIP_PATH
    ip_name    = derive_ip(strip_path)

    print(f"  strip path : {strip_path}")
    print(f"  ip name    : {ip_name}")
    print(f"  begin time : {begin_time}")
    print(f"  type       : {wtype}")

    confirm = input("Proceed? (Y/n): ").strip().lower()
    if confirm == "n":
        print("Aborted.")
        sys.exit(0)

    # Step 5: extract
    run_extract(strip_path, begin_time, ip_name, wtype)

    print(f"All done. {wtype} extraction complete.")


if __name__ == "__main__":
    main()
