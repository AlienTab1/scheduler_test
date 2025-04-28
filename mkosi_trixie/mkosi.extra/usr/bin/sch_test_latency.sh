#!/bin/bash

echo "Scehdulre Latency test"

threads=$(grep processor /proc/cpuinfo | wc -l)
echo "Current CPU threads: " $threads 


echo "Starting hackbench.."
hackbench_out=$(hackbench -g 20 -l 10000 -s 512 -f 25 -T)&

sleep 1

echo "cyclictest latency measurement:"
sudo cyclictest --mlockall --nsecs  --priority=80 --interval=200 --distance=0 --loop=100000 --mainaffinity=0 --threads=$(($threads-1)) --affinity=1-$(($threads-1)) 
