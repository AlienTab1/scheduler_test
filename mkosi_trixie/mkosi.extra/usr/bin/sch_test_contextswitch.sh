#!/bin/bash

# ==============================================
# Scheduler Context Switching Test using pidstat
# ----------------------------------------------
# This script uses `pidstat` to measure voluntary and non-voluntary
# context switches per thread while the system is under load using `stress-ng`.
# ==============================================

# Determine the number of CPU threads available on the system
threads=$(grep -c ^processor /proc/cpuinfo)

# Define how long the test should run (in seconds)
duration=30

# Display test parameters
echo "Current CPU threads: $threads"
echo "Test duration: $duration seconds"
echo "=== Scheduler Context Switching Test ==="

# Function to run the pidstat test
run_pidstat_test() {
    echo
    echo ">>> Measuring per-thread context switches with pidstat -w -t"

    # Launch stress-ng in the background to generate CPU load
    # We add +3 seconds to make sure stress-ng runs slightly longer
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
