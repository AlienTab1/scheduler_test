# scheduler_test
This repository contains, scripts and configurations for the testing of linux process scheduler from debian distribution based images created by mkosi tool.

## Content of the repository

- **mkosi_bookworm/**<br>
mkosi project directory based on bookworm release with kernel 6.1 and CFS

- **mkosi_trixie/** <br>
mkosi project directory based on trixie release with kernel 6.12 and EEVDF

- **original/** <br>
Original attempt of creating one image with multiple kernels.

- **outputs/** <br>
Contains python script for test results data analysis, plots and data tables generatos.
And measurements data results. 

- **tests/** <br>
Directory containing process scheduler tests targetin scheduling criteria. 

## Useful commands
### dd created image to USB disk
>*sudo dd if=image.raw.raw of=/dev/XXX conv=fsync oflag=direct status=progress bs=4M*

### Initial command for instalation MKOSI to system
>*pipx install git+https://github.com/systemd/mkosi.git*
- systemd-repart necessary for partitioning bootable image<br>
>*sudo apt install systemd-repart*

### Create new image and run it in Quemu VM
>*mkosi --qemu-smp 2 qemu --force*
- without Quemu<br> 
>*mkosi --force*

