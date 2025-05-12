#!/bin/bash

# ==============================================================================
# Scheduler Throughput Test Script (Sysbench + Stress-ng)
# ------------------------------------------------------------------------------
# This script runs multiple `sysbench` CPU throughput tests under different
# load scenarios to evaluate how the Linux scheduler handles contention.
#
# It simulates "real-world" conditions by combining:
# - Controlled CPU stress (via `stress-ng`)
# - Multi-threaded CPU benchmarks (via `sysbench`)
#
# Test Scenarios:
#   1. 30s Sysbench, no background load
#   2. 30s Sysbench, background load from stress-ng
#   3. 100s Sysbench, no background load
#   4. 100s Sysbench, background load from stress-ng
#
# Requirements:
# - sysbench
# - stress-ng
#
# Usage:
#   ./sch_test_throughput.sh > throughput_results.txt
# ==============================================================================

# === Detect number of logical CPU threads ===
threads=$(grep -c ^processor /proc/cpuinfo)
echo "Current CPU threads: $threads"

# === Scenario 1: 30 seconds, no background load ===
echo
echo "=== Scenario 1: Sysbench ($threads threads, 30s, no background load) ==="
sysbench cpu --threads="$threads" --time=30 run
sleep 5

# === Scenario 2: 30 seconds, with stress-ng background CPU load ===
echo
echo "=== Scenario 2: Sysbench ($threads threads, 30s, with stress-ng background load) ==="
stress-ng --cpu "$threads" --timeout=$((30 + 3)) --quiet &  # start background load
stress_pid=$!
sleep 2  # let stress-ng ramp up
sysbench cpu --threads="$threads" --time=30 run
wait $stress_pid  # ensure stress-ng finishes
sleep 5

# === Scenario 3: 100 seconds, no background load ===
echo
echo "=== Scenario 3: Sysbench ($threads threads, 100s, no background load) ==="
sysbench cpu --threads="$threads" --time=100 run
sleep 5

# === Scenario 4: 100 seconds, with stress-ng background CPU load ===
echo
echo "=== Scenario 4: Sysbench ($threads threads, 100s, with stress-ng background load) ==="
stress-ng --cpu "$threads" --timeout=$((100 + 3)) --quiet &
stress_pid=$!
sleep 2
sysbench cpu --threads="$threads" --time=100 run
wait $stress_pid

# === Done ===
echo
echo "=== Throughput tests completed ==="
