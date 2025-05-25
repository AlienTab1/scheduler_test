#!/bin/bash

# ==============================================================================
# Scheduler Context Switching Test with pidstat and stress-ng
# ------------------------------------------------------------------------------
# This script evaluates per-thread context switch behavior on a loaded system
# by combining `stress-ng` for CPU stress and `pidstat` for scheduling stats.
#
# The script:
# - Detects the number of available logical CPUs
# - Launches `stress-ng` with matching load to saturate the CPU
# - Uses `pidstat -w -t` to monitor voluntary and involuntary context switches
#   for each thread during the test interval
#
# Output: Context switch metrics (stdout) for runtime analysis
#
# Requirements:
# - bash, `stress-ng`, `pidstat` (part of sysstat package)
#
# Usage:
#   ./sch_test_context_switch.sh > context_switch_log.txt
#
# ==============================================================================

# Determine the number of logical CPUs available on the system
threads=$(grep -c ^processor /proc/cpuinfo)

# Define how long the test should run (in seconds)
duration=30

# Display test parameters
echo "Current logical CPUs: $threads"
echo "Test duration: $duration seconds"
echo "=== Scheduler Context Switching Test ==="

# Function to run the pidstat test
run_pidstat_test() {
    echo
    echo ">>> Measuring per-thread context switches with pidstat -w -t"

    # Launch stress-ng in the background to generate CPU load
    # Add +3 seconds to make sure stress-ng runs slightly longer
    # than pidstat to guarantee full coverage of the sampling window.
    echo "Starting stress-ng again for detailed tracking..."
    stress-ng --cpu "$threads" --timeout "$(($duration+3))" --quiet &
    stress_pid=$!

    # Give stress-ng some time to initialize before starting pidstat
    sleep 2

    echo
    echo "--- pidstat -w -t output ---"

    # Run pidstat to monitor per-thread context switches:
    # -w  : display task switching activity (voluntary/involuntary)
    # -t  : show per-thread stats (not just per-process)
    # 1   : sample interval in seconds
    # $duration : how long to run the sampling
    pidstat -w -t 1 "$duration"

    # Wait for stress-ng to complete before exiting
    wait $stress_pid
}

# === Run the actual test ===
run_pidstat_test

# Final message to indicate the test has ended
echo
echo "=== Context Switching Test Complete ==="
