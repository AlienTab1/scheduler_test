#!/bin/bash

#param="$1"
#name="${param%%=*}"
#value="${param#*=}"

#echo "value " $value
#echo "name " $name

echo "Simple fairness test"

threads=$(grep processor /proc/cpuinfo | wc -l)
echo "Current CPU threads: " $threads 

outputs=()

#sysbench cpu run --threads=1 --time=10 --verbosity=1

for ((i=0; i<$threads; i++)); do
  echo "Starting sysbench on cpu: $i"
  {
    time taskset -c $1 hackbench -g 20 -l 100 -s 512 -f 25 --threads
  } > >(
    # Tady čteme celý výstup najednou
    out=""
    while IFS= read -r row; do
      out+="$row"$'\n'
      done
    outputs+=("$vystup")
  ) &
 
done

#wait
sleep 7

echo "Results:"
for ((i=0; i<${#outputs[@]}; i++)); do
  echo "CPU $i: ${outputs[$i]}"
done

