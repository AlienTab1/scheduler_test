#!/bin/bash

# Scheduler Context Switching Test using pidstat (thread-aware)

threads=$(grep -c ^processor /proc/cpuinfo)
duration=30

echo "Current CPU threads: $threads"
echo "Test duration: $duration seconds"
echo "=== Scheduler Context Switching Test ==="

run_pidstat_test() {
    echo
    echo ">>> Measuring per-thread context switches with pidstat -w -t"
    echo "Starting stress-ng again for detailed tracking..."
    stress-ng --cpu "$threads" --timeout "$(($duration+3))" --quiet &
    stress_pid=$!
    sleep 2
    echo
    echo "--- pidstat -w -t output ---"
    pidstat -w -t 1 "$duration"
    wait $stress_pid
}

# === Run both parts ===
#run_vmstat_test

run_pidstat_test

echo
echo "=== Context Switching Test Complete ==="
