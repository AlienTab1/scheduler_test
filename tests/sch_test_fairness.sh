#!/bin/bash

echo "Scheduler Fairness Test (tracking only hackbench scheduling events)"

# Setup output directory
outputs_dir="/tmp/outputs"
mkdir -p "$outputs_dir"
rm -f "$outputs_dir"/*

# Detect CPU count
threads=$(grep -c ^processor /proc/cpuinfo)
echo "Using $threads logical CPUs"

perf_data_file="$outputs_dir/perf_sched.data"

# Start perf recording only for hackbench
echo "Starting perf record for hackbench (sched events only)..."
perf record -e sched:* -g -o "$perf_data_file"&
perf_pid=$!

# Start hackbench
echo "Starting hackbench..."
hackbench -s 512 -l 1500 -g 12 -f 25 -P &
hackbench_pid=$!
echo "Hackbench PID: $hackbench_pid"

# Give hackbench time to spawn threads
#sleep .5

# Save LWP IDs
thread_lwps=$(ps -L -o pid,tid,comm | grep hackbench | awk '{print $2}')
echo "$thread_lwps" > "$outputs_dir/thread_lwps.txt"
echo "Captured LWP count: $(echo "$thread_lwps" | wc -w)"

# Wait for hackbench to finish
wait "$hackbench_pid"
echo "Hackbench completed."

# Stop perf cleanly
kill "$perf_pid" 2>/dev/null
wait "$perf_pid" 2>/dev/null

# Convert perf.data to readable trace
perf script -i "$perf_data_file" > "$outputs_dir/perf_trace.txt"

echo "Done. Output files:"
echo " - Thread LWPs: $outputs_dir/thread_lwps.txt"
echo " - Perf data:   $perf_data_file"
echo " - Trace:       $outputs_dir/perf_trace.txt"
