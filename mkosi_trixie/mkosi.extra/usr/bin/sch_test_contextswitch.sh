#!/bin/bash

# Scheduler Context Switching Test using vmstat and pidstat (thread-aware)

threads=$(grep -c ^processor /proc/cpuinfo)
duration=30

echo "Current CPU threads: $threads"
echo "Test duration: $duration seconds"
echo "=== Scheduler Context Switching Test ==="

run_vmstat_test() {
    echo
    echo ">>> [1/2] Measuring system-wide context switches with vmstat"
    echo "Starting CPU load using stress-ng with $threads threads..."
    stress-ng --cpu "$threads" --timeout "$duration" --quiet &
    stress_pid=$!
    sleep 2
    echo
    echo "--- vmstat output (context switch column = 'cs') ---"
    vmstat 1 "$duration"
    wait $stress_pid
}

run_pidstat_test() {
    echo
    echo ">>> [2/2] Measuring per-thread context switches with pidstat -w -t"
    echo "Starting stress-ng again for detailed tracking..."
    stress-ng --cpu "$threads" --timeout "$(($duration+3))" --quiet &
    stress_pid=$!
    sleep 2
    echo
    echo "--- pidstat -w -t output ---"
    pidstat -w -t -I 1 "$duration"
    wait $stress_pid
}

# === Run both parts ===
#run_vmstat_test
echo
echo "Sleeping for 5 seconds before running pidstat..."
sleep 5
run_pidstat_test

echo
echo "=== Context Switching Test Complete ==="
