#!/bin/sh

echo "Simple sysbench CPU test"

threads=$(grep processor /proc/cpuinfo | wc -l)

echo "Current CPU threads: " $threads 

sysbench cpu run --threads=$threads

