#!/bin/sh
echo "====== Shell Environment Info ======"
echo "Shell (SHELL var):  $SHELL"
echo "Shell (process \$0): $0"
echo "Bash version:       $BASH_VERSION"
echo "Tcsh version:       $tcsh"
echo "Zsh version:        $ZSH_VERSION"
echo ""
echo "====== OS Info ======"
uname -a 2>/dev/null || echo "uname not available"
echo ""
echo "====== User & Host ======"
echo "User:  $(whoami)"
echo "Host:  $(hostname)"
echo "PWD:   $PWD"
echo ""
echo "====== Python ======"
python3 --version 2>/dev/null || python --version 2>/dev/null || echo "python not found"
echo ""
echo "====== Key Tool Availability ======"
for cmd in run_pre_pwr_anal_busy200 run_waveform_analysis mm2_fsdbextract expect; do
    if command -v "$cmd" >/dev/null 2>&1; then
        echo "  $cmd: FOUND ($(command -v $cmd))"
    else
        echo "  $cmd: NOT FOUND in PATH"
    fi
done
echo ""
echo "====== PATH ======"
echo "$PATH" | tr ':' '\n'
echo "===================================="
