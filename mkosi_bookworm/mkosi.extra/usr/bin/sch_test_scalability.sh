#!/bin/bash

# Scheduler Scalability Test using sysbench

threads=$(grep processor /proc/cpuinfo | wc -l)
echo "Current CPU threads: $threads"

duration=30

echo "=== Scheduler Scalability Test ==="
echo "Test duration per run: ${duration}s"
echo

# Define list of powers of 2 up to max threads
thread_levels=(1 2 4 8 16 32 64 128)

for t in "${thread_levels[@]}"; do
  if [ "$t" -le "$threads" ]; then
    echo ">> Running sysbench with $t threads"
    sysbench cpu --threads="$t" --time="$duration" run
    echo
    sleep 5
  fi
done

# Run with full CPU count if not already included
if ! [[ "${thread_levels[*]}" =~ (^|[[:space:]])$threads($|[[:space:]]) ]]; then
  echo ">> Running sysbench with $threads threads (max detected)"
  sleep 1
  sysbench cpu --threads="$threads" --time="$duration" run
  echo
  sleep 5
fi

echo "=== Scalability test complete ==="
