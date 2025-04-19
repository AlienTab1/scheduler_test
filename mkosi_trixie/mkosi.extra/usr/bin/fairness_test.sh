#!/bin/bash

#param="$1"
#name="${param%%=*}"
#value="${param#*=}"

#echo "value " $value
#echo "name " $name

echo "Simple fairness test"

threads=$(grep processor /proc/cpuinfo | wc -l)
echo "Current CPU threads: " $threads 




outputs_dir="/tmp/outputs"
mkdir -p "$outputs_dir"
rm -f "$outputs_dir"/*

pids=()

for ((i=0; i<$threads; i++)); do
  echo "Starting test on CPU: $i"
  
  (
  (time taskset -c "$i" hackbench -g 20 -l 100 -s 512 -f 25 --threads) > "$outputs_dir/output_$i.txt" 2>&1
  ) &
  
  pids+=($!)
done

# Čekáme na všechny procesy
for pid in "${pids[@]}"; do
  wait "$pid"
done













#sysbench cpu run --threads=1 --time=10 --verbosity=1

#for ((i=0; i<$threads; i++)); do
#  echo "Starting test on cpu: $i"
#  {
#    time taskset -c "$i" hackbench -g 20 -l 100 -s 512 -f 25 --threads
#  } 2>&1 > >(
#    # Tady čteme celý výstup najednou
#    out=""
#    while IFS= read -r row; do
#      out+="$row"$'\n'
#      done
#    outputs+=("$vystup")
#  ) &
# 
#done

wait
#sleep 7

echo "Results:"
for ((i=0; i<$threads; i++)); do
  echo "CPU $i:"
  #printf "%s\n" "${outputs[$i]}"
  cat "$outputs_dir/output_$i.txt"
  echo
done


rm -f "$outputs_dir"/*
