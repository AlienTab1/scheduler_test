#!/bin/bash

# Script for printing CPU temperature at adjustable intervals

interval=${1:-1}  # Default interval is 1 second if no parameter is provided

# Function to find the appropriate CPU temperature input file
get_cpu_temp_file() {
    # Iterate through all hwmon sensor directories
    for hwmon in /sys/class/hwmon/hwmon*; do
        # Read the chip name from the current sensor
        chip_name=$(cat "$hwmon/name")

        # Check if the sensor corresponds to AMD CPU (k10temp)
        if [[ "$chip_name" == "k10temp" ]]; then
            # Look through temperature input files in AMD sensor
            for temp_input in "$hwmon"/temp*_input; do
                # Construct corresponding label file name
                label_file=${temp_input/_input/_label}
                # Check if the label file exists
                if [[ -f "$label_file" ]]; then
                    label=$(cat "$label_file")
                    # Return the file if it matches Tctl (AMD main control temperature)
                    if [[ "$label" == "Tctl" ]]; then
                        echo "$temp_input"
                        return
                    fi
                fi
            done

        # Check if the sensor corresponds to Intel CPU (coretemp)
        elif [[ "$chip_name" == "coretemp" ]]; then
            # Look through temperature input files in Intel sensor
            for temp_input in "$hwmon"/temp*_input; do
                # Construct corresponding label file name
                label_file=${temp_input/_input/_label}
                # Check if the label file exists
                if [[ -f "$label_file" ]]; then
                    label=$(cat "$label_file")
                    # Return the file if it matches Package id 0 (Intel main temperatures)
                    if [[ "$label" == "Package id 0" ]]; then
                        echo "$temp_input"
                        return
                    fi
                fi
            done
        fi
    done

    # Return empty string if no sensor file was found
    echo ""
}

# Get the CPU temperature input file path
cpu_temp_file=$(get_cpu_temp_file)

# Check if a valid temperature file was found
if [[ -n "$cpu_temp_file" ]]; then
    count=1
    # Continuously print CPU temperature at the given interval with index counter
    while true; do
        # Generate a timestamp
        timestamp=$(date '+%s')
        # Read and calculate temperature in Celsius
        temp=$(($(cat "$cpu_temp_file") / 1000))
        # Output timestamp and temperature
        echo "CPU_Temperature: $temp °C, $count, $timestamp"
        # count++
        count=$((count + 1))
        # Sleep for the specified interval
        sleep "$interval"
    done
else
    # Output error message if no sensor is found
    echo "CPU temperature sensor not found."
    exit 1
fi
