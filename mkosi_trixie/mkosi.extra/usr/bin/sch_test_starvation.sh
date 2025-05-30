#!/bin/bash

# ==============================================================================
# Scheduler Starvation Detection Test with PID Logging
# ------------------------------------------------------------------------------
# This script evaluates whether low-priority tasks are starved by high-priority
# CPU-bound workloads under Linux schedulers.
#
# The script:
# - Launches a high-priority `hackbench` group (nice -10) to saturate the CPU
# - Starts a small low-priority group (nice 19) to simulate starvation victims
# - Periodically logs runtime stats from /proc/<pid>/stat for all tasks
#
# Output: CSV-formatted log showing timestamped user/system CPU time and nice
#         levels for each process.
#
# Requirements:
# - bash, `hackbench`, `pgrep`, `/proc` access
#
# Usage:
#   ./sch_test_starvation.sh > starvation_log.txt
#
# Format: timestamp, starttime, pid, nice, utime, stime
# ==============================================================================

echo "=== Scheduler Starvation Test ==="

# --- Detect total logical CPUs ---
cpu_threads=$(grep -c ^processor /proc/cpuinfo)
echo "# Logical CPUs: $cpu_threads"

# Get system clock ticks per second
CLK_TCK=$(getconf CLK_TCK)
echo "# CLK_TCK: $CLK_TCK"

# Set number of processes
high_group_count=$((cpu_threads * 2))
low_group_count=2  # Few victims at low priority

LOOPS=120000
FDS=4
BYTES=512

# --- Launch High-Priority Group (nice -10) ---
echo -e "\n# Starting high-priority load (nice -10)"
nice -n -10 hackbench -s $BYTES -l $LOOPS -g $high_group_count -f $FDS -P &
pid_high=$!

# --- Launch Low-Priority Victim Group (nice 19) ---
echo -e "\n# Starting victim group (nice 19)"
nice -n 19 hackbench -s $BYTES -l $LOOPS -g $low_group_count -f $FDS -P &
pid_low=$!

# Wait for child processes to spawn
sleep 0.05

# --- Capture all child PIDs ---
pids_high=$(pgrep -P "$pid_high")
pids_low=$(pgrep -P "$pid_low")
all_pids="$pids_high $pids_low"

echo "# High-priority PIDs: $(echo "$pids_high" | wc -w)"
echo "# Victim PIDs: $(echo "$pids_low" | wc -w)"
echo "# Total PIDs being logged: $(echo "$all_pids" | wc -w)"
echo "timestamp,starttime,pid,nice,utime,stime"
echo "Start logging..."

# === Logging Loop ===
while kill -0 "$pid_high" 2>/dev/null || kill -0 "$pid_low" 2>/dev/null; do
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

echo "# Starvation test complete"
