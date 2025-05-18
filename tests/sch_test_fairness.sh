#!/bin/bash

# ==============================================================================
# Scheduler Fairness Test with PID/TID Logging
# ------------------------------------------------------------------------------
# This script launches four groups of CPU-bound tasks using `hackbench`, each
# with a different `nice` level to simulate varying scheduling priorities.
#
# The script:
# - Starts hackbench processes with different `nice` values (18, 10, 5, -5)
# - Captures all their TIDs (threads) once started
# - Periodically logs runtime statistics from /proc/<pid>/stat
#   including user/system time and scheduling priority
#
# Output: CSV-formatted log stream for later analysis of fairness
#
# Requirements:
# - bash, `hackbench`, `pgrep`, `/proc` access
#
# Usage:
#   ./sch_test_fairness.sh > fairness_log.csv
#
# Format: timestamp, starttime, pid, nice, utime, stime
# ==============================================================================

echo "=== Scheduler Fairness Test with PID Logging ==="

# --- Detect total logical CPUs ---
cpu_threads=$(grep -c ^processor /proc/cpuinfo)
echo "# Logical CPUs: $cpu_threads"

# Get system clock ticks per second (for converting utime/stime if needed)
CLK_TCK=$(getconf CLK_TCK)
echo "# CLK_TCK: $CLK_TCK"

# Set number of hackbench groups equal to logical CPU count
groups_per_hackbench=$((cpu_threads))

# Define workload parameters for hackbench
LOOPS=90000   # Number of message loop iterations
FDS=6         # Number of file descriptors (default hackbench group size)
BYTES=512     # Message size in bytes

# --- Launch Group A with low priority (nice 18) ---
echo -e "\n# Starting Group A (nice 18)"
nice -n 18 hackbench -s $BYTES -l $LOOPS -g $groups_per_hackbench -f $FDS -P &
pid_a=$!

sleep 0.1

# --- Launch Group B with medium-low priority (nice 10) ---
echo -e "\n# Starting Group B (nice 10)"
nice -n 10 hackbench -s $BYTES -l $LOOPS -g $groups_per_hackbench -f $FDS -P &
pid_b=$!

# --- Launch Group C with default priority (nice 5) ---
echo -e "\n# Starting Group C (nice 5)"
nice -n 5 hackbench -s $BYTES -l $LOOPS -g $groups_per_hackbench -f $FDS -P &
pid_c=$!

# --- Launch Group D with high priority (nice -5) ---
echo -e "\n# Starting Group D (nice -5)"
nice -n -5 hackbench -s $BYTES -l $LOOPS -g $groups_per_hackbench -f $FDS -P &
pid_d=$!

# Allow some time for all hackbench groups to spawn their threads
sleep 0.01

# --- Collect TIDs (thread IDs) for each group ---
group_a_pids=$(pgrep -P "$pid_a")
group_b_pids=$(pgrep -P "$pid_b")
group_c_pids=$(pgrep -P "$pid_c")
group_d_pids=$(pgrep -P "$pid_d")

# Merge all TIDs into one list
all_pids+="$$group_c_pids $group_d_pids"

echo "Group A: $(echo "$group_a_pids"| wc -w)"
echo "Group B: $(echo "$group_b_pids"| wc -w)"
echo "Group C: $(echo "$group_c_pids"| wc -w)"
echo "Group D: $(echo "$group_d_pids"| wc -w)"

echo "# Total PIDs being logged: $(echo "$all_pids" | wc -w)"
echo "timestamp,starttime,pid,nice,utime,stime"
echo "Start logging..."

# === Logging Loop ===
# Continue logging while any of the four hackbench groups is still alive
while kill -0 "$pid_a" 2>/dev/null || kill -0 "$pid_b" 2>/dev/null || kill -0 "$pid_c" 2>/dev/null || kill -0 "$pid_d" 2>/dev/null; do
    #timestamp=$(date +%s.%N)  # Nanosecond-resolution timestamp

    # Collect runtime statistics from each thread still alive
    for pid in $all_pids; do
        if [[ -r /proc/$pid/stat ]]; then
            stat_line=$(< /proc/$pid/stat)
            fields=($stat_line)
            #echo "$timestamp,${fields[21]},$pid,${fields[18]},${fields[13]},${fields[14]}"
        fi
    done

    # Separate each sampling block
    echo "end sample"
    sleep 0.1
done

echo "# Fairness test complete"
