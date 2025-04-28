#!/bin/bash

# Script for execution of process scheduler tests

# Call env init script to mount opuput partition
sch_test_env_init.sh

sleep 2
# Detect environment info
threads=$(grep -c ^processor /proc/cpuinfo)

echo "Getting environment info..."
sch_test_env_info.sh > "/media/output/${threads}_env_info_output.txt" 2>&1 &
PID=$!
wait $PID
echo "Environment info collection complete."

# Run the latency test
echo "Running latency test..."
sch_test_latency.sh > "/media/output/${threads}_latency_output.txt" 2>&1 &
PID=$!
wait $PID
echo "Latency test complete."
