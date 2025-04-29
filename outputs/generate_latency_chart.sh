#!/bin/bash

# Base directory
BASE_DIR="32_ryzen9/CFS"

# Loop over all run directories
for dir in "$BASE_DIR"/run_*/; do
    RUN_ID=$(basename "$dir")
    
    # Try both possible input files
    FILE_16="${dir}6.1.0-34-amd64_32_latency_output.txt"
    FILE_12="${dir}6.1.0-34-amd64_12_latency_output.txt"

    if [[ -f "$FILE_16" ]]; then
        echo "Processing $RUN_ID (16)..."
        python3 latency_plot.py "$FILE_16" "$dir"
    elif [[ -f "$FILE_12" ]]; then
        echo "Processing $RUN_ID (12)..."
        python3 latency_plot.py "$FILE_12" "$dir"
    else
        echo "Skipping $RUN_ID — no matching input file found."
    fi
done


# Base directory
BASE_DIR="32_ryzen9/EEVDF"

# Loop over all run directories
for dir in "$BASE_DIR"/run_*/; do
    RUN_ID=$(basename "$dir")
    
    # Try both possible input files
    FILE_16="${dir}6.12.22-amd64_32_latency_output.txt"
    FILE_12="${dir}6.12.22-amd64_12_latency_output.txt"

    if [[ -f "$FILE_16" ]]; then
        echo "Processing $RUN_ID (16)..."
        python3 latency_plot.py "$FILE_16" "$dir"
    elif [[ -f "$FILE_12" ]]; then
        echo "Processing $RUN_ID (12)..."
        python3 latency_plot.py "$FILE_12" "$dir"
    else
        echo "Skipping $RUN_ID — no matching input file found."
    fi
done

