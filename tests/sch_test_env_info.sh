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

