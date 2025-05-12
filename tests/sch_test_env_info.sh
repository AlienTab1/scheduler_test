#!/bin/bash

# ===============================================================
# System Information Summary Script for Benchmarking Context
# ---------------------------------------------------------------
# This script collects detailed system information relevant to
# performance benchmarking, tuning, or diagnostics.
#
# It prints:
# - CPU details and cache hierarchy
# - Memory availability
# - CPU core and NUMA topology
# - Kernel version
# - Scheduler tuning parameters from /proc/sys/kernel
#
# This information is essential when documenting system state
# during performance experiments (e.g. latency, throughput tests).
#
# Usage:
#   ./system_info_report.sh > system_info.txt
# ===============================================================

# === CPU Information ===
echo "=== CPU Information ==="
lscpu                             # Basic CPU architecture summary
lscpu --all                       # Detailed per-core/thread info
lscpu --cache                     # L1/L2/L3 cache size and mapping
lscpu --all --extended            # Extended fields including topology and thread IDs

# === RAM Information ===
echo "=== RAM Information ==="
free -h                           # Human-readable memory usage snapshot (RAM + swap)

# === CPU Topology ===
echo "=== CPU Topology ==="
lstopo-no-graphics                # NUMA and CPU layout without graphical output

# === Kernel Version ===
echo "=== Kernel Version ==="
uname -r                          # Display the running Linux kernel version

# === Scheduler Settings (/proc/sys/kernel/sched*) ===
echo "=== Scheduler Settings (/proc/sys/kernel/sched*) ==="
for param in /proc/sys/kernel/sched*; do
    if [ -f "$param" ]; then
        # Print each kernel scheduler parameter with its current value
        echo "$(basename "$param"): $(cat "$param")"
    fi
done


koko