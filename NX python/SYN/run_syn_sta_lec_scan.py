#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Synthesis, STA, LEC, and Scan Flow Controller - Simplified Version with Process Monitoring

This script manages the synthesis flow with simplified shell-based execution and process monitoring.
Each step: Delete files -> Execute command -> Monitor process and wait for completion files
All terminal state issues are handled by shell scripts.

Author: Generated for synthesis flow automation
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('syn_flow.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class SynthesisFlowController:
    def __init__(self, work_dir='.'):
        """Initialize the synthesis flow controller
        
        Args:
            work_dir (str): Working directory path
        """
        self.work_dir = Path(work_dir)
        self.logger = logging.getLogger(__name__)
        
        # ==========================================
        # CONFIGURATION - Modify these parameters
        # ==========================================
        
        # Step execution control (1 = execute, 0 = skip)
        self.config_need_step0 = 0  # VCSG LINT
        self.config_need_step1 = 1  # SYNTHESIS
        self.config_need_step2 = 1  # STATIC TIMING ANALYSIS  
        self.config_need_step3 = 1  # LOGIC EQUIVALENCE CHECK
        self.config_need_step4 = 1  # SCAN INSERTION
        self.config_need_step5 = 0  # PRE POWER ANALYSIS
        
        # Delay between steps (in seconds)
        self.inter_step_delay = 30  # Default 30 seconds between steps
        
        # Simplified step configurations
        self.step_configs = {
            'step0': {
                'name': 'VCSG LINT',
                'work_folder': None,
                'command': 'run_vcsg_lint',
                'file_patterns': ['./vcspyglass/vcspyglass_lint/vcsg_lint.err_warn.rpt'],
            },
            'step1': {
                'name': 'SYNTHESIS',
                'work_folder': None,
                'command': 'qqrsh64 run_syn',
                'file_patterns': ['./syn_rpt/*congestion.rpt'],
            },
            'step2': {
                'name': 'STATIC TIMING ANALYSIS',
                'work_folder': None,
                'command': 'qqrsh64 run_pre_sta',
                'file_patterns': ['./sta_rpt/*derate.rpt'],
            },
            'step3': {
                'name': 'LOGIC EQUIVALENCE CHECK',
                'work_folder': None,
                'command': 'qqrsh64 run_lec_rtl2pre',
                'file_patterns': ['./lec/lec.bbox.rpt'],
            },
            'step4': {
                'name': 'SCAN INSERTION',
                'work_folder': './scan_atpg_automation',
                'command': './run_scan',
                'file_patterns': ['scan_summary.rpt'],
            },
            'step5': {
                'name': 'PRE POWER ANALYSIS',
                'work_folder': None,
                'command': 'qqrsh64 run_pre_pwr',
                'file_patterns': ['./pwr_rpt/*power.rpt'],
            }
        }
        
        # ==========================================
        
        # Add delay info to logging
        self.logger.info("Flow Controller initialized with process monitoring:")
        self.logger.info("Step execution control:")
        self.logger.info(f"  config_need_step0 (VCSG LINT): {self.config_need_step0}")
        self.logger.info(f"  config_need_step1 (SYNTHESIS): {self.config_need_step1}")
        self.logger.info(f"  config_need_step2 (STATIC TIMING ANALYSIS): {self.config_need_step2}")
        self.logger.info(f"  config_need_step3 (LOGIC EQUIVALENCE CHECK): {self.config_need_step3}")
        self.logger.info(f"  config_need_step4 (SCAN INSERTION): {self.config_need_step4}")
        self.logger.info(f"  config_need_step5 (PRE POWER ANALYSIS): {self.config_need_step5}")
        self.logger.info(f"  Inter-step delay: {self.inter_step_delay} seconds")
        self.logger.info("")
        self.logger.info("Step configurations:")
        for step_id, config in self.step_configs.items():
            self.logger.info(f"  {step_id} ({config['name']}):")
            self.logger.info(f"    Work folder: {config['work_folder'] or 'Current directory'}")
            self.logger.info(f"    Command: {config['command']}")
            self.logger.info(f"    File patterns: {config['file_patterns']}")
    
    def run_step_simplified(self, step_id):
        """Simplified step execution with process monitoring - infinite wait until completion
        
        Args:
            step_id (str): Step identifier (step0, step1, step2, step3, step4, step5)
            
        Returns:
            bool: True if step completed successfully
        """
        if step_id not in self.step_configs:
            self.logger.error(f"Unknown step: {step_id}")
            return False
        
        config = self.step_configs[step_id]
        step_name = config['name']
        
        self.logger.info("=" * 80)
        self.logger.info(f"STARTING {step_id.upper()}: {step_name}")
        self.logger.info(f"Will monitor process and wait indefinitely for completion (Ctrl+C to interrupt)")
        self.logger.info("=" * 80)
        
        # Determine working directory
        if config['work_folder']:
            work_dir = self.work_dir / config['work_folder']
            self.logger.info(f"Working directory: {work_dir.absolute()}")
        else:
            work_dir = self.work_dir
            self.logger.info(f"Working directory: {work_dir.absolute()}")
        
        # Prepare file patterns for shell script
        wait_files_str = ' '.join(f'"{f}"' for f in config['file_patterns'])
        
        # Max time to wait for files after process dies (seconds)
        # If the process exits/is killed and files don't appear within this time, treat as failure
        process_dead_timeout = 120

        # Enhanced shell script with process monitoring
        shell_script = f'''
        set -e
        cd "{work_dir.absolute()}"

        echo "Step: Delete old files"
        for pattern in {wait_files_str}; do
            rm -f $pattern 2>/dev/null || true
        done

        echo "Step: Execute command - {config['command']}"
        {config['command']} &
        command_pid=$!

        # Verify PID is valid
        if [ -z "$command_pid" ]; then
            echo "ERROR: Failed to get process PID"
            exit 1
        fi

        echo "Command started with PID: $command_pid"

        # Verify process is actually running
        if kill -0 $command_pid 2>/dev/null; then
            echo "Verified: Process $command_pid is running"
        else
            echo "WARNING: Process $command_pid not found immediately after start"
        fi

        echo "Step: Monitor process and wait for completion"
        start_time=$(date +%s)
        files_found_time=0
        process_finished_time=0
        process_exit_code=-1

        # Signal handling for Ctrl+C - kill child process group and exit immediately
        trap 'echo "Interrupted by user"; kill $command_pid 2>/dev/null || true; exit 130' INT TERM

        while true; do
            current_time=$(date +%s)

            # Check if process is still running using kill -0
            if kill -0 $command_pid 2>/dev/null; then
                process_running=true
                process_status="RUNNING"
            else
                process_running=false
                process_status="FINISHED"

                # Record when process finished and capture exit code
                if [ $process_finished_time -eq 0 ]; then
                    process_finished_time=$current_time
                    wait $command_pid 2>/dev/null
                    process_exit_code=$?
                    echo "Process PID $command_pid has finished with exit code: $process_exit_code"
                fi
            fi

            # Check if files exist
            all_found=true
            missing_files=""
            for pattern in {wait_files_str}; do
                if ! ls $pattern >/dev/null 2>&1; then
                    all_found=false
                    missing_files="$missing_files $pattern"
                fi
            done

            # Record when files are first found
            if [ "$all_found" = "true" ] && [ $files_found_time -eq 0 ]; then
                files_found_time=$current_time
                echo "All required files found!"

                # List the found files with details
                echo "Found files:"
                for pattern in {wait_files_str}; do
                    ls -la $pattern 2>/dev/null || true
                done
            fi

            # Exit conditions: Process finished AND files exist AND stability delay
            if [ "$all_found" = "true" ] && [ "$process_running" = "false" ]; then
                if [ $files_found_time -gt 0 ] && [ $process_finished_time -gt 0 ]; then
                    # Calculate time since both conditions were met
                    time_since_files=$((current_time - files_found_time))
                    time_since_process=$((current_time - process_finished_time))

                    # Wait for stability (30 seconds after both conditions)
                    stability_delay=30
                    if [ $time_since_files -ge $stability_delay ] && [ $time_since_process -ge $stability_delay ]; then
                        echo "SUCCESS: Process completed and files stable for $stability_delay seconds!"
                        break
                    else
                        echo "Waiting for stability... Files stable: $time_since_files sec, Process finished: $time_since_process sec (need $stability_delay sec)"
                    fi
                fi
            fi

            # CRITICAL FIX: If process died but files never appeared, abort after timeout
            if [ "$process_running" = "false" ] && [ "$all_found" = "false" ] && [ $process_finished_time -gt 0 ]; then
                time_since_death=$((current_time - process_finished_time))
                if [ $time_since_death -ge {process_dead_timeout} ]; then
                    echo "ERROR: Process exited (code: $process_exit_code) {process_dead_timeout} seconds ago but required files never appeared."
                    echo "  The process was likely killed or crashed. Aborting step."
                    echo "  Missing files:$missing_files"
                    exit 1
                else
                    remaining_wait=$(({process_dead_timeout} - time_since_death))
                    echo "WARNING: Process exited (code: $process_exit_code), waiting up to $remaining_wait more seconds for files..."
                fi
            fi

            # Show progress
            elapsed=$((current_time - start_time))
            hours=$((elapsed/3600))
            minutes=$(((elapsed%3600)/60))

            if [ $hours -gt 0 ]; then
                time_str="$hours hours $minutes minutes"
            else
                time_str="$minutes minutes"
            fi

            # Status message based on current state
            if [ "$process_running" = "true" ]; then
                if [ "$all_found" = "true" ]; then
                    echo "Status: Process PID $command_pid running, files found - {step_name} running... ($time_str elapsed)"
                else
                    echo "Status: Process PID $command_pid running, waiting for files - {step_name} running... ($time_str elapsed)"
                    echo "  Missing files:$missing_files"
                fi
            else
                if [ "$all_found" = "true" ]; then
                    echo "Status: Process PID $command_pid finished, files found, ensuring stability - {step_name} finalizing... ($time_str elapsed)"
                fi
            fi

            sleep 10
        done

        # Final verification and summary
        echo "Final verification:"
        echo "  Process PID $command_pid: $(kill -0 $command_pid 2>/dev/null && echo "still running" || echo "finished")"
        echo "  Required files:"
        for pattern in {wait_files_str}; do
            if ls $pattern >/dev/null 2>&1; then
                echo "    Found: $pattern"
                ls -la $pattern
            else
                echo "    Missing: $pattern"
            fi
        done

        # Ensure terminal state is normal
        stty sane 2>/dev/null || true
        echo "{step_name} COMPLETED!"
        '''

        try:
            # Use Popen for better control over child process lifecycle
            proc = subprocess.Popen(
                ['bash', '-c', shell_script],
                # Start in a new process group so we can kill the entire tree
                preexec_fn=os.setsid if hasattr(os, 'setsid') else None,
            )

            try:
                result_code = proc.wait()
            except KeyboardInterrupt:
                self.logger.warning(f"{step_name} interrupted by user (Ctrl+C), killing process tree...")
                # Kill the entire process group (bash + all children)
                import signal
                try:
                    if hasattr(os, 'killpg'):
                        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                    else:
                        proc.terminate()
                except ProcessLookupError:
                    pass
                # Give it a moment to terminate gracefully, then force kill
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    try:
                        if hasattr(os, 'killpg'):
                            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                        else:
                            proc.kill()
                    except ProcessLookupError:
                        pass
                    proc.wait()
                return False

            if result_code == 0:
                self.logger.info(f"{step_name} completed successfully")
                self.logger.info("=" * 80)
                return True
            elif result_code == 130:  # Ctrl+C interrupt
                self.logger.warning(f"{step_name} interrupted by user")
                return False
            else:
                self.logger.error(f"{step_name} failed with return code {result_code}")
                return False

        except Exception as e:
            self.logger.error(f"{step_name} failed: {e}")
            return False
    
    def apply_inter_step_delay(self, current_step, next_step=None):
        """Apply delay between steps
        
        Args:
            current_step (str): Current step that just completed
            next_step (str): Next step to be executed (None if last step)
        """
        if next_step is None:
            # Last step, no delay needed
            return
            
        if self.inter_step_delay <= 0:
            # No delay configured
            return
        
        self.logger.info("=" * 50)
        self.logger.info(f"INTER-STEP DELAY")
        self.logger.info(f"Completed: {current_step}")
        self.logger.info(f"Next step: {next_step}")
        self.logger.info(f"Waiting {self.inter_step_delay} seconds before next step...")
        self.logger.info("=" * 50)
        
        # Countdown display
        import time
        for remaining in range(self.inter_step_delay, 0, -1):
            if remaining % 10 == 0 or remaining <= 10:
                self.logger.info(f"Starting {next_step} in {remaining} seconds...")
            time.sleep(1)
        
        self.logger.info(f"Delay complete. Starting {next_step}")
    
    def step0_vcsg_lint(self, step_number=None, total_steps=None):
        """Step 0: VCSG Lint - With process monitoring"""
        return self.run_step_simplified('step0')
    
    def step1_synthesis(self, step_number=None, total_steps=None):
        """Step 1: Synthesis - With process monitoring"""
        return self.run_step_simplified('step1')
    
    def step2_sta(self, step_number=None, total_steps=None):
        """Step 2: Static Timing Analysis - With process monitoring"""
        return self.run_step_simplified('step2')
    
    def step3_lec(self, step_number=None, total_steps=None):
        """Step 3: Logic Equivalence Check - With process monitoring"""
        return self.run_step_simplified('step3')
    
    def step4_scan(self, step_number=None, total_steps=None):
        """Step 4: Scan Insertion - With process monitoring"""
        return self.run_step_simplified('step4')
    
    def step5_pre_pwr(self, step_number=None, total_steps=None):
        """Step 5: Pre Power Analysis - With process monitoring"""
        return self.run_step_simplified('step5')
    
    def run_flow(self, steps=['step1']):
        """Run the complete or partial synthesis flow with inter-step delays
        
        Args:
            steps (list): List of steps to run (default: ['step1'])
        """
        self.logger.info("Starting Synthesis Flow Controller - Process Monitoring Version")
        self.logger.info(f"Working directory: {self.work_dir.absolute()}")
        self.logger.info(f"Steps to execute: {steps}")
        self.logger.info(f"Inter-step delay: {self.inter_step_delay} seconds")
        
        step_functions = {
            'step0': self.step0_vcsg_lint,
            'step1': self.step1_synthesis,
            'step2': self.step2_sta, 
            'step3': self.step3_lec,
            'step4': self.step4_scan,
            'step5': self.step5_pre_pwr
        }
        
        total_steps = len(steps)
        success = True
        
        try:
            for step_index, step in enumerate(steps, 1):
                if step in step_functions:
                    self.logger.info(f"\nPreparing to execute {step} ({step_index}/{total_steps})")
                    
                    # Execute the step
                    if not step_functions[step](step_index, total_steps):
                        success = False
                        self.logger.error(f"{step} execution failed, flow terminated")
                        break
                    else:
                        self.logger.info(f"{step} executed successfully")
                        
                        # Apply delay before next step (if not the last step)
                        if step_index < total_steps:
                            next_step = steps[step_index]  # next step in the list
                            self.apply_inter_step_delay(step, next_step)
                        
                else:
                    self.logger.error(f"Unknown step: {step}")
                    success = False
                    break
            
            if success:
                self.logger.info("=" * 80)
                self.logger.info("ENTIRE FLOW EXECUTION COMPLETED SUCCESSFULLY!")
                self.logger.info("=" * 80)
            else:
                self.logger.error("=" * 80)
                self.logger.error("FLOW EXECUTION FAILED!")
                self.logger.error("=" * 80)
        
        except KeyboardInterrupt:
            self.logger.warning("Flow interrupted by user (Ctrl+C)")
            success = False
        
        finally:
            # Always ensure terminal state is restored
            try:
                subprocess.run(['stty', 'sane'], check=False, timeout=5)
                self.logger.info("Terminal state restored")
            except Exception:
                pass  # Ignore errors in terminal reset
        
        return success

def main():
    """Main function"""
    # Create and run flow controller with default settings
    controller = SynthesisFlowController('.')
    
    # Build steps_to_run list based on configuration
    steps_to_run = []
    step_configs = {
        'step0': controller.config_need_step0,
        'step1': controller.config_need_step1,
        'step2': controller.config_need_step2, 
        'step3': controller.config_need_step3,
        'step4': controller.config_need_step4,
        'step5': controller.config_need_step5
    }
    
    for step_id, enabled in step_configs.items():
        if enabled == 1:
            steps_to_run.append(step_id)
    
    if not steps_to_run:
        controller.logger.warning("No steps are enabled! Please set at least one config_need_stepX to 1")
        sys.exit(1)
    
    controller.logger.info(f"Steps to execute based on configuration: {steps_to_run}")
    success = controller.run_flow(steps_to_run)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
