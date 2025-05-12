#!/bin/bash

# ==============================================================================
# Scheduler Latency Test: cyclictest under stress
# ------------------------------------------------------------------------------
# This script evaluates real-time scheduling latency using `cyclictest`
# while running a concurrent background CPU load (`hackbench`) to simulate stress.
#
# Procedure:
# - Detects system CPU thread count
# - Launches `hackbench` to create a realistic scheduler load
# - Starts `cyclictest` to measure scheduling jitter under stress
# - Gracefully stops `cyclictest` once `hackbench` completes
#
# Requirements:
# - `cyclictest` (from rt-tests)
# - `hackbench` (from stress-ng or util-linux)
#
# Output:
# - latency data printed to stdout (should be redirected to file when running)
#
# Usage:
#   ./sch_test_latency.sh > latency_results.txt
# ==============================================================================

echo "Scheduler Latency Test"

# === Detect the number of logical CPU threads ===
threads=$(grep -c ^processor /proc/cpuinfo)
echo "Current CPU threads: $threads"

# === Launch hackbench to generate CPU load in background ===
# -g 20: number of groups (each group = 2 communicating processes)
# -l 10000: loop count
# -s 512: message size
# -f 25: number of file descriptors (parallel tasks per group)
# -T: use threads instead of processes (less fork overhead)
echo "Starting hackbench..."
hackbench -g 20 -l 10000 -s 512 -f 25 -T &
hb_pid=$!

# Give hackbench some time to initialize before measuring latency
sleep 0.3

# === Launch cyclictest for latency measurement ===
# --mlockall: lock memory to avoid paging
# --nsecs: use nanosecond resolution
# --priority=80: real-time thread priority
# --interval=200: interval between timer events (in µs)
# --distance=0: thread CPU affinity spacing (0 = packed)
# --loop=800000: number of test loops (i.e., wakeups)
# --threads=$threads: one thread per CPU core
# --affinity=0-N: bind threads explicitly to CPUs
echo "Starting cyclictest latency measurement..."
cyclictest --mlockall --nsecs --priority=80 \
  --interval=200 --distance=0 --loop=800000 \
  --threads=$threads --affinity=0-$(($threads - 1)) &
ct_pid=$!

# === Wait for hackbench to finish ===
wait $hb_pid

# === Stop cyclictest gracefully (so it flushes final stats) ===
echo "Hackbench finished. Stopping cyclictest..."
kill -INT $ct_pid 2>/dev/null

# === Wait for cyclictest to exit cleanly ===
wait $ct_pid 2>/dev/null

echo "Latency test complete."
