#!/bin/bash

# Script for execution of process scheduler tests

# === Help Message ===
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    echo "Usage: $0 [lat thr fai sca res ctx star]"
    echo "Run selected scheduler tests. If no parameters are provided, all tests will run."
    echo
    echo "  lat   = latency"
    echo "  thr   = throughput"
    echo "  fai   = fairness"
    echo "  sca   = scalability"
    echo "  res   = responsiveness"
    echo "  ctx   = context switching"
    echo "  star  = starvation detection"
    exit 0
fi

# === Configuration ===
threads=$(grep -c ^processor /proc/cpuinfo)
kernel_version=$(uname -r)
output_base="/media/output"

# === Create next available run directory ===
run_index=1
while [ -d "${output_base}/run_${run_index}" ]; do
    run_index=$((run_index + 1))
done

run_dir="${output_base}/run_${run_index}"
mkdir -p "$run_dir"

echo "Output will be saved in: $run_dir"
echo "Kernel version prefix: $kernel_version"
echo "Threads detected: $threads"

# === Parse Parameters ===
run_all=false
tests=()

if [ $# -eq 0 ]; then
    run_all=true
else
    tests=("$@")
fi

# === Test Execution Functions ===
run_test() {
    local label=$1
    local script=$2
    echo "Running $label test..."
    "$script" > "${run_dir}/sch_${label}_output_${kernel_version}_${threads}.txt" 2>&1 &
    wait $!
    echo "$label test complete."
}

# === Environment Info ===
echo "Getting environment info..."
sch_test_env_info.sh > "${run_dir}/sch_env_info_output_${kernel_version}_${threads}.txt" 2>&1 &
wait $!
echo "Environment info collection complete."

# === Test Definitions ===
declare -A test_map=(
    ["lat"]="sch_test_latency.sh"
    ["thr"]="sch_test_throughput.sh"
    ["fai"]="sch_test_fairness.sh"
    ["sca"]="sch_test_scalability.sh"
    ["res"]="sch_test_responsiveness.sh"
    ["ctx"]="sch_test_context_switching.sh"
    ["star"]="sch_test_starvation.sh"
)

# === Execute Requested or All Tests ===
for key in "${!test_map[@]}"; do
    if $run_all || [[ " ${tests[*]} " =~ " ${key} " ]]; then
        run_test "$key" "${test_map[$key]}"
    fi
done
