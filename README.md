# scheduler_test



## Useful commands
### dd created image to USB disk
*sudo dd if=image.raw.raw of=/dev/XXX conv=fsync oflag=direct status=progress bs=4M*

### Initial command for instalation MKOSI to system
*pipx install git+https://github.com/systemd/mkosi.git*
- systemd-repart necessary for partitioning bootable image
*sudo apt install systemd-repart*

### Create new image and run it in Quemu VM
*mkosi --output image.raw --qemu-smp 2 qemu --force*
- without Quemu 
*mkosi --output image.raw --force*

