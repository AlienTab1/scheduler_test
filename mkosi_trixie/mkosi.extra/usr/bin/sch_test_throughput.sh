#!/bin/bash

# Scheduler Throughput Test Script (Sysbench + Stress-ng)

threads=$(nproc)
echo "Current CPU threads: $threads"

# Scenario 1: 30s, no load
echo
echo "=== Scenario 1: Sysbench ($threads threads, 30s, no background load) ==="
sysbench cpu --threads="$threads" --time=30 run
sleep 5

# Scenario 2: 30s, with background stress-ng
echo
echo "=== Scenario 2: Sysbench ($threads threads, 30s, with stress-ng background load) ==="
stress-ng --cpu "$threads" --timeout=$((30+3)) --quiet &
stress_pid=$!
sleep 2
sysbench cpu --threads="$threads" --time=30 run
wait $stress_pid
sleep 5

# Scenario 3: 100s, no load
echo
echo "=== Scenario 3: Sysbench ($threads threads, 100s, no background load) ==="
sysbench cpu --threads="$threads" --time=100 run
sleep 5

# Scenario 4: 100s, with background stress-ng
echo
echo "=== Scenario 4: Sysbench ($threads threads, 100s, with stress-ng background load) ==="
stress-ng --cpu "$threads" --timeout=$((100+3)) --quiet &
stress_pid=$!
sleep 2
sysbench cpu --threads="$threads" --time=100 run
wait $stress_pid

echo
echo "=== Throughput tests completed ==="
