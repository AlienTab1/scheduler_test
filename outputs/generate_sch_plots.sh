#!/bin/bash

# === Usage ===
if [[ "$1" == "-h" || "$1" == "--help" || $# -ne 1 ]]; then
    echo "Usage: $0 <root_directory_with_run_folders>"
    exit 1
fi

ROOT_DIR="$1"

if [[ ! -d "$ROOT_DIR" ]]; then
    echo "Error: '$ROOT_DIR' is not a valid directory."
    exit 1
fi

# === Map file prefixes to corresponding Python parser scripts ===
declare -A parser_map=(
    ["lat"]="latency_plot.py"
    ["thr"]="throughput_plot.py"
    ["fai"]="fairness_plot.py"
    ["sca"]="scalability_plot.py"
    #["res"]="responsiveness_plot.py"
    ["ctx"]="contextswitch_plot.py"
    #["star"]="starvation_plot.py"
)

# === Process each run directory ===
for run_dir in "$ROOT_DIR"/run_*/; do
    echo "==> Processing: $run_dir"

    result_dir="${run_dir}/result"
    mkdir -p "$result_dir"

    for label in "${!parser_map[@]}"; do
        parser="${parser_map[$label]}"
        pattern="sch_${label}_output_"  # filename prefix

        # Find matching file(s)
        for file in "$run_dir"/${pattern}*.txt; do
            if [[ -f "$file" ]]; then
                echo "   → Running $parser on $(basename "$file")"
                python3 "$parser" "$file" "$result_dir"
            fi
        done
    done
done
