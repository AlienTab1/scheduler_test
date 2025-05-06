#!/bin/bash

echo "Scheduler Latency Test"

# Detect number of CPU threads
threads=$(grep -c ^processor /proc/cpuinfo)
echo "Current CPU threads: $threads"

echo "Starting hackbench..."
hackbench -g 20 -l 10000 -s 512 -f 25 -T &
hb_pid=$!

# Give hackbench a small head start
sleep 0.5

echo "Starting cyclictest latency measurement..."
# Run cyclictest in the background, output to stdout
cyclictest --mlockall --nsecs --priority=80 \
  --interval=200 --distance=0 --loop=100000 \
  --threads=$threads --affinity=0-$(($threads - 1)) &
ct_pid=$!

# Wait for hackbench to finish
wait $hb_pid

# Kill cyclictest once hackbench completes
echo "Hackbench finished. Stopping cyclictest..."
kill -INT $ct_pid 2>/dev/null

# Wait for cyclictest to flush output
wait $ct_pid 2>/dev/null

echo "Latency test complete."
