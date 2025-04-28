echo "=== CPU Information ==="
lscpu
lscpu --all
lscpu --cache
lscpu --all --extended

echo "=== RAM Information ==="
free -h

echo "=== CPU Topology ==="
lstopo-no-graphics

echo "=== Kernel Version ==="
uname -r

echo "=== Scheduler Settings (/proc/sys/kernel/sched*) ==="
for param in /proc/sys/kernel/sched*; do
    if [ -f "$param" ]; then
        echo "$(basename "$param"): $(cat "$param")"
    fi
done