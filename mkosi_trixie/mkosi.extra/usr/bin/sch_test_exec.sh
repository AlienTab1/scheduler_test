#!/bin/bash

# Script for execution of process scheduler tests

# Detect number of threads
threads=$(grep -c ^processor /proc/cpuinfo)

# Get kernel version for file prefix
kernel_version=$(uname -r)

# Find next available run directory under /media/output/
output_base="/media/output"
run_index=1
while [ -d "${output_base}/run_${run_index}" ]; do
    run_index=$((run_index + 1))
done

run_dir="${output_base}/run_${run_index}"
mkdir -p "$run_dir"

echo "Output will be saved in: $run_dir"
echo "Kernel version prefix: $kernel_version"
echo "Threads detected: $threads"

# Start environment info collection
echo "Getting environment info..."
sch_test_env_info.sh > "${run_dir}/sch_env_info_output_${kernel_version}_${threads}.txt" 2>&1 &
PID=$!
wait $PID
echo "Environment info collection complete."

# Run the latency test
echo "Running latency test..."
sch_test_latency.sh > "${run_dir}/sch_latency_output_${kernel_version}_${threads}.txt" 2>&1 &
PID=$!
wait $PID
echo "Latency test complete."

# Run throughput test
echo "Running throughput test..."
sch_test_throughtput.sh > "${run_dir}/sch_throughput_output_${kernel_version}_${threads}.txt" 2>&1 &
PID=$!
wait $PID
echo "Throughput test complete."

