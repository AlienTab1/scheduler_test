#!/bin/bash

param="$1"
name="${param%%=*}"
value="${param#*=}"

#echo "value " $value
#echo "name " $name

echo "Latency test"

threads=$(grep processor /proc/cpuinfo | wc -l)
echo "Current CPU threads: " $threads 

if [[ "$name" == "test" ]]; then
  case "$value" in
    sys)
      echo "Starting sysbench.."
      sysbench_out=$(sysbench cpu run --threads=$threads)&
      ;;
    hack)
      echo "Starting hackbench.."
      hackbench_out=$(hackbench -g 20 -l 10000 -s 512 -f 25 --threads)&
      ;;
    *)
      echo "Unknown value for param test: $value"
      echo "Starting hackbench.."
      hackbench_out=$(hackbench -g 20 -l 10000 -s 512 -f 25 --threads)&
      ;;
  esac
  else
    echo "Starting hackbench.."
    hackbench_out=$(hackbench -g 20 -l 10000 -s 512 -f 25 --threads)&
fi  


sleep 1

echo "cyclictest latency measurement:"
sudo cyclictest --mlockall --nsecs  --priority=80 --interval=200 --distance=0 --loop=100000 --mainaffinity=0 --threads=$(($threads-1)) --affinity=1-$(($threads-1)) 
