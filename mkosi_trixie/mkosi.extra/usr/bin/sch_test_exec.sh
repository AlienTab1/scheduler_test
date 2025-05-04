#!/bin/bash

# Script for execution of process scheduler tests

# === Help Message ===
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    echo "Usage: $0 [--loops=N] [--tests=lat thr fai sca res ctx star]"
    echo "Run selected scheduler tests. If no tests are specified, all tests will run once."
    echo
    echo "  --loops=N  = Repeat the entire test loop N times (default: 1)"
    echo "  --tests=[lat ... star]  = List of executed tests (if not set all test will be executed)"
    echo "          lat          = latency"
    echo "          thr          = throughput"
    echo "          fai          = fairness"
    echo "          sca          = scalability"
    echo "          res          = responsiveness"
    echo "          ctx          = context switching"
    echo "          star         = starvation detection"
    exit 0
fi

# === Configuration ===
threads=$(grep -c ^processor /proc/cpuinfo)
kernel_version=$(uname -r)
output_base="/media/output"
loops=1
tests=()
run_all=false
parse_tests=false

# === Parse Parameters ===
for arg in "$@"; do
    if [[ "$arg" == --loops=* ]]; then
        loops="${arg#*=}"
    elif [[ "$arg" == --tests ]]; then
        parse_tests=true
    elif $parse_tests; then
        # As long as next args aren't starting with '--', treat them as test keys
        if [[ "$arg" == --* ]]; then
            parse_tests=false
        else
            tests+=("$arg")
        fi
    fi
done

if [ ${#tests[@]} -eq 0 ]; then
    run_all=true
fi

# === Test Execution Function ===
run_test() {
    local label=$1
    local script=$2
    local out_file="$1"

    echo "Running $label test..."
    "$script" > "$out_file" 2>&1
    echo "$label test complete."
}

# === Test Script Mapping ===
declare -A test_map=(
    ["lat"]="sch_test_latency.sh"
    ["thr"]="sch_test_throughput.sh"
    ["fai"]="sch_test_fairness.sh"
    ["sca"]="sch_test_scalability.sh"
    ["res"]="sch_test_responsiveness.sh"
    ["ctx"]="sch_test_contextswitch.sh"
    ["star"]="sch_test_starvation.sh"
)

# === Main Loop (Repeat Entire Run) ===
for ((i = 1; i <= loops; i++)); do
    echo "=== Starting test cycle $i of $loops ==="

    # --- Create next available run directory ---
    run_index=1
    while [ -d "${output_base}/run_${run_index}" ]; do
        run_index=$((run_index + 1))
    done

    run_dir="${output_base}/run_${run_index}"
    mkdir -p "$run_dir"

    echo "Output will be saved in: $run_dir"
    echo "Kernel version prefix: $kernel_version"
    echo "Threads detected: $threads"

    # --- Environment Info ---
    echo "Getting environment info..."
    sch_test_env_info.sh > "${run_dir}/sch_env_info_output_${kernel_version}_${threads}.txt" 2>&1 &
    wait $!
    echo "Environment info collection complete."

    # --- Run selected or all tests ---
    for key in "${!test_map[@]}"; do
        if $run_all || [[ " ${tests[*]} " =~ " ${key} " ]]; then
            output_file="${run_dir}/sch_${key}_output_${kernel_version}_${threads}.txt"
            run_test "$key" "${test_map[$key]}" "$output_file"
            sleep 3
        fi
    done

    echo "=== Finished test cycle $i ==="
    echo
done
