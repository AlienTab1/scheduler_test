#!/bin/bash

# ===============================================================
# Scheduler Tuning & Output Partition Mount Script
# ---------------------------------------------------------------
# This script does two main things:
# 1. Applies a unified set of Linux scheduler kernel parameters
#    to tune task scheduling behavior.
# 2. Mounts a pre-defined output partition (labelled OUTPUT) to
#    /media/output to store benchmark or test results.
#
# The output partition is assumed to be created via mkosi.repart
# or a similar tool and should be labeled OUTPUT (vfat recommended).
#
# Run as root or with sufficient privileges to change /proc/sys/*
# and mount partitions.
#
# Usage:
#   sudo ./setup_scheduler_and_mount.sh
# ===============================================================

# === Apply scheduler tuning parameters ===
echo "Applying unified scheduler settings..."

# Enable task group scheduling (autogrouping)
echo 1 > /proc/sys/kernel/sched_autogroup_enabled

# Set slice duration for CFS (Completely Fair Scheduler)
echo 5000 > /proc/sys/kernel/sched_cfs_bandwidth_slice_us

# Child process does not run before parent (0 = disabled)
echo 0 > /proc/sys/kernel/sched_child_runs_first

# Max/min deadline periods in microseconds (used for deadline policy)
echo 4194304 > /proc/sys/kernel/sched_deadline_period_max_us
echo 100 > /proc/sys/kernel/sched_deadline_period_min_us

# Disable energy-aware scheduling (mostly for heterogeneous cores)
echo 0 > /proc/sys/kernel/sched_energy_aware

# Enable Intel Turbo Mode-aware scheduling (ITMT)
echo 1 > /proc/sys/kernel/sched_itmt_enabled

# Round-robin scheduler timeslice in ms
echo 100 > /proc/sys/kernel/sched_rr_timeslice_ms

# Realtime scheduling: max period and allowed runtime per period
echo 1000000 > /proc/sys/kernel/sched_rt_period_us
echo 950000 > /proc/sys/kernel/sched_rt_runtime_us

# Disable internal scheduler stats collection (overhead reduction)
echo 0 > /proc/sys/kernel/sched_schedstats

echo "All scheduler settings applied."

# === Mount output partition for storing results ===

# Define mount sequence logic with fallback
mount_sequence() {
    if create_output_dir; then
        mount_output
    else
        mount_output
    fi
}

# Create target directory (if not already present)
create_output_dir() {
    mkdir -p /media/output
}

# Mount the partition with label OUTPUT to the target directory
mount_output() {
    mount --label OUTPUT /media/output/
}

echo "Mounting OUTPUT partition to /media/output"

# Try initial mount attempt
mount_sequence

# Check if it succeeded
if [ $? -eq 0 ]; then
    exit 0
else
    # Retry once after short delay in case the device was slow to initialize
    sleep 5
    mount_sequence
fi
