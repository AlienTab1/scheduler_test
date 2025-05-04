#!/bin/bash

echo "=== Scheduler Fairness Test with PID/TID Logging ==="

# Detect CPU threads
cpu_threads=$(grep -c ^processor /proc/cpuinfo)
echo "# Logical CPUs: $cpu_threads"

CLK_TCK=$(getconf CLK_TCK)
echo "# CLK_TCK: $CLK_TCK"

# Determine group count (2x CPUs)
groups_per_hackbench=$((cpu_threads))

# Hackbench params
LOOPS=80000
FDS=6
BYTES=512

# Launch Group A: nice 0
echo -e "\n# Starting Group A (nice 0)"
nice -n 0 hackbench -s $BYTES -l $LOOPS -g $groups_per_hackbench -f $FDS -P &
pid_a=$!

# Launch Group B: nice 10
echo -e "\n# Starting Group B (nice 10)"
nice -n 10 hackbench -s $BYTES -l $LOOPS -g $groups_per_hackbench -f $FDS -P &
pid_b=$!

# Wait for children to spawn
sleep 0.1

# Capture all child PIDs of hackbench groups
group_a_pids=$(pgrep -P "$pid_a" )
group_b_pids=$(pgrep -P "$pid_b" )

# Merge all PIDs from both groups
all_pids="$group_a_pids $group_b_pids"

echo "# Total TIDs being logged: $(echo "$all_pids" | wc -w)"
echo "timestamp,starttime,pid,nice,utime,stime"
echo "Start logging"
# Main logging loop
while kill -0 "$pid_a" 2>/dev/null || kill -0 "$pid_b" 2>/dev/null; do
    timestamp=$(date +%s.%N)

    for pid in $all_pids; do
        if [[ -r /proc/$pid/stat ]]; then
            stat_line=$(< /proc/$pid/stat)
            fields=($stat_line)
            echo "$timestamp,${fields[21]},$pid,${fields[18]},${fields[13]},${fields[14]}"
        fi
    done
    echo "end sample"
    sleep 0.1
done


echo "# Fairness test complete"