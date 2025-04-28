#!/bin/bash

# set scheduler settings
echo "Appliing unified scheduler settings.."

echo 1 > /proc/sys/kernel/sched_autogroup_enabled
echo 5000 > /proc/sys/kernel/sched_cfs_bandwidth_slice_us
echo 0 > /proc/sys/kernel/sched_child_runs_first
echo 4194304 > /proc/sys/kernel/sched_deadline_period_max_us
echo 100 > /proc/sys/kernel/sched_deadline_period_min_us
echo 0 > /proc/sys/kernel/sched_energy_aware
echo 1 > /proc/sys/kernel/sched_itmt_enabled
echo 100 > /proc/sys/kernel/sched_rr_timeslice_ms
echo 1000000 > /proc/sys/kernel/sched_rt_period_us
echo 950000 > /proc/sys/kernel/sched_rt_runtime_us
echo 0 > /proc/sys/kernel/sched_schedstats

echo "All scheduler settings applied."


# mount output partition
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
#------------------------------------------------------























