#!/bin/bash

# ================================================================
# CPU Temperature + Frequency Logger with Interval Control
# ------------------------------------------------
# This script continuously logs CPU temperature readings and per-core
# frequencies using Linux-native sysfs interfaces.
#
# - Output includes: sample count, timestamp, temperature (°C), and
#   frequencies (kHz) for all logical CPUs.
# - Interval between samples is set by the first CLI argument.
# - Data is printed to stdout (can be redirected for logging).
#
# Usage:
#   ./cpu_temp_logger.sh [interval_seconds]
#
# Example:
#   ./cpu_temp_logger.sh 2    # logs every 2 seconds
# ================================================================

interval=${1:-1}  # Default interval is 1 second if not provided

# Function to find the appropriate CPU temperature input file
get_cpu_temp_file() {
    for hwmon in /sys/class/hwmon/hwmon*; do
        chip_name=$(cat "$hwmon/name")

        if [[ "$chip_name" == "k10temp" ]]; then
            for temp_input in "$hwmon"/temp*_input; do
                label_file=${temp_input/_input/_label}
                if [[ -f "$label_file" ]]; then
                    label=$(cat "$label_file")
                    if [[ "$label" == "Tctl" ]]; then
                        echo "$temp_input"
                        return
                    fi
                fi
            done

        elif [[ "$chip_name" == "coretemp" ]]; then
            for temp_input in "$hwmon"/temp*_input; do
                label_file=${temp_input/_input/_label}
                if [[ -f "$label_file" ]]; then
                    label=$(cat "$label_file")
                    if [[ "$label" == "Package id 0" ]]; then
                        echo "$temp_input"
                        return
                    fi
                fi
            done
        fi
    done
    echo ""
}

# Function to read CPU frequencies for all logical CPUs
get_cpu_frequencies() {
    for cpu in /sys/devices/system/cpu/cpu[0-9]*; do
        freq_file="$cpu/cpufreq/scaling_cur_freq"
        if [[ -f "$freq_file" ]]; then
            cpu_id=$(basename "$cpu")
            freq=$(cat "$freq_file")
            echo -n "$cpu_id: ${freq}kHz, "
        fi
    done
}

# Get the CPU temperature input file path
cpu_temp_file=$(get_cpu_temp_file)

# Main logging loop
if [[ -n "$cpu_temp_file" ]]; then
    count=1
    while true; do
        timestamp=$(date '+%s')
        temp=$(($(cat "$cpu_temp_file") / 1000))

        echo -n "Sample #$count, Timestamp: $timestamp, CPU_Temperature: ${temp}°C, "
        get_cpu_frequencies
        echo  # newline

        count=$((count + 1))
        sleep "$interval"
    done
else
    echo "CPU temperature sensor not found."
    exit 1
fi
