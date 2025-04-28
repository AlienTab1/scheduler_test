#!/bin/bash

mount_sequence() {
    if create_output_dir; then
        mount_output
    else
        mount_output
    fi
}

create_output_dir() {
    mkdir /media/output
}

mount_output() {
    mount --label OUTPUT /media/output/   
}


#-- Mounting output partiton to store the test result --
#- Output vfat partition is created by mkosi.repart with label=OUTPUT

#lsblk -o name,mountpoint,label,size,uuid
echo "Mounting OUTPUT partition to /media/output"

mount_sequence

if [ $? -eq 0 ]; then
    exit 0
else
    sleep 5
    mount_sequence
fi


# Set scheduler settings

# List of parameters to set
declare -A params=(
    [sched_autogroup_enabled]=0
    [sched_cfs_bandwidth_slice_us]=5000
    [sched_child_runs_first]=0
    [sched_deadline_period_max_us]=4194304
    [sched_deadline_period_min_us]=100
    [sched_energy_aware]=1
    [sched_itmt_enabled]=1
    [sched_rr_timeslice_ms]=100
    [sched_rt_period_us]=1000000
    [sched_rt_runtime_us]=950000
    [sched_schedstats]=0
)

echo "Applying scheduler settings..."

for param in "${!params[@]}"; do
    path="/proc/sys/kernel/$param"
    if [ -e "$path" ]; then
        echo "${params[$param]}" | sudo tee "$path" > /dev/null
        echo "Set $param to ${params[$param]}"
    else
        echo "Warning: $path does not exist (skipped)"
    fi
done

echo "All settings applied."

#------------------------------------------------------























