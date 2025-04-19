#!/bin/bash

echo "Scheduler Fairness Test (hackbench with full perf logging)"

outputs_dir="/tmp/outputs"
mkdir -p "$outputs_dir"
rm -f "$outputs_dir"/*

# Get number of available thread
threads=$(grep processor /proc/cpuinfo | wc -l)
echo "Current CPU threads: " $threads 

# Starting hackbench
echo "Starting hackbench with 4 times more tasks as are available threads.."
hackbench -g $(($threads/2)) -l 1000000 -s 512 -f 4 --threads &
hackbench_parent_pid=$!
echo "Parent PID hackbench: $hackbench_parent_pid"

sleep 1

# Getting LWP IDs of hackbench threads
thread_lwps=$(ps -L aux | grep "hackbench" | grep -v "grep" | awk '{print $3}')
echo "Child LWP ID threads: $thread_lwps"

# Saving LWP IDs of threads to a file
echo "$thread_lwps" > "$outputs_dir/thread_lwps.txt"

# Starting perf sched record for all processes
echo "Starting perf sched record for all processes..."
perf sched record -a -g -o "$outputs_dir/perf_sched.data" -- bash -c "wait $hackbench_parent_pid" &> "$outputs_dir/hackbench_output.log"
perf_sched_pid=$!

# Waiting for hackbench to complete
wait "$hackbench_parent_pid"

echo "Hackbench completed."

# Finishing perf sched record
echo "Finishing perf sched record..."
kill "$perf_sched_pid" 2>/dev/null

# Generating perf sched latency analysis (for basic metrics)
perf sched latency -i "$outputs_dir/perf_sched.data" > "$outputs_dir/perf_sched_latency.txt"

echo "Scheduler fairness test completed."