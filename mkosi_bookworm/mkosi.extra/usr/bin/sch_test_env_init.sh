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

#------------------------------------------------------























