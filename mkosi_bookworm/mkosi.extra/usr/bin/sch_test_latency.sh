#!/bin/bash

echo "Scehdulre Latency test"

threads=$(grep processor /proc/cpuinfo | wc -l)
echo "Current CPU threads: " $threads 


echo "Starting hackbench.."
hackbench_out=$(hackbench -g 20 -l 10000 -s 512 -f 25 -T)&

sleep 1

echo "cyclictest latency measurement:"
cyclictest --mlockall --nsecs  --priority=80 --interval=200 --distance=0 --loop=100000 --threads=$threads --affinity=0-$(($threads-1)) 
