#!/bin/bash

# ==============================================================================
# Scheduler Scalability Test using sysbench
# ------------------------------------------------------------------------------
# This script evaluates how the Linux process scheduler scales with increasing
# numbers of threads during a CPU-bound workload (via `sysbench`).
#
# It runs the sysbench CPU test at increasing thread counts, typically in
# powers of two (1, 2, 4, 8, 16...), and finally tests with the maximum number
# of logical CPUs available, if not already included.
#
# Requirements:
# - sysbench installed (`apt install sysbench` on Debian-based systems)
#
# Usage:
#   ./sch_test_scalability.sh > scalability_results.txt
# ==============================================================================

# === Detect total number of logical CPUs ===
threads=$(grep -c ^processor /proc/cpuinfo)
echo "Current logical CPUs: $threads"

# === Test duration per thread level ===
duration=30
echo "=== Scheduler Scalability Test ==="
echo "Test duration per run: ${duration}s"
echo

# === Define which thread levels to test (powers of 2 up to max) ===
thread_levels=(1 2 4 8 16 32 64 128)

# === Run sysbench at each defined thread level ===
for t in "${thread_levels[@]}"; do
  if [ "$t" -le "$threads" ]; then
    echo ">> Running sysbench with $t threads"
    sysbench cpu --threads="$t" --time="$duration" run
    echo
    sleep 5  # cooldown between tests
  fi
done

# === Ensure max thread count is tested if not already included ===
if ! [[ "${thread_levels[*]}" =~ (^|[[:space:]])$threads($|[[:space:]]) ]]; then
  echo ">> Running sysbench with $threads threads (max detected)"
  sleep 1
  sysbench cpu --threads="$threads" --time="$duration" run
  echo
  sleep 5
fi

echo "=== Scalability test complete ==="
