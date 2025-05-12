import re
import sys
import os
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

def print_help():
    """Print usage help and exit."""
    print("Usage: python latency_plot.py <latency_input_file> <temperature_input_file> <output_directory>")
    sys.exit(1)

# ---- Step 1: Parse arguments ----
if len(sys.argv) != 4:
    print("Error: Missing arguments.\n")
    print_help()

latency_file = sys.argv[1]
temp_file = sys.argv[2]
output_dir = sys.argv[3]

if not os.path.isfile(latency_file):
    print(f"Error: Latency file not found: {latency_file}")
    sys.exit(1)

if not os.path.isfile(temp_file):
    print(f"Error: Temperature file not found: {temp_file}")
    sys.exit(1)

if not os.path.isdir(output_dir):
    print(f"Error: Output directory not found: {output_dir}")
    sys.exit(1)

# ---- Step 2: Prepare output filenames ----
basename = os.path.splitext(os.path.basename(latency_file))[0]
output_plot = os.path.join(output_dir, f"{basename}_latency_temp_plot.png")
output_stats = os.path.join(output_dir, f"{basename}_latency_stats.txt")

# ---- Step 3: Parse latency data ----
with open(latency_file, "r") as file:
    text = file.read()

pattern = re.compile(r"T:\s*(\d+).*?C:\s*(\d+).*?Min:\s*(\d+).*?Avg:\s*(\d+).*?Max:\s*(\d+)", re.MULTILINE)
thread_data = defaultdict(list)

for match in pattern.finditer(text):
    tid = int(match.group(1))   # Thread ID
    c = int(match.group(2))     # Iteration count
    min_v = int(match.group(3))
    avg = int(match.group(4))
    max_v = int(match.group(5))
    if c == 0:
        continue
    thread_data[tid].append((c, avg))

# ---- Step 4: Parse temperature data ----
temp_values = []
with open(temp_file, "r") as f:
    for line in f:
        match = re.search(r"CPU_Temperature:\s*(\d+)", line)
        if match:
            temp_values.append(int(match.group(1)))

# ---- Step 5: Determine max X for latency and stretch temp to fit ----
SKIP_FIRST = 1  # Skip initial samples if needed
max_c = max(c for samples in thread_data.values() for c, _ in samples)

# Spread temperature samples evenly across latency X range
if len(temp_values) > 1:
    temp_x = np.linspace(0, max_c, len(temp_values))
else:
    temp_x = [0]

# ---- Step 6: Generate plot ----
fig, ax1 = plt.subplots(figsize=(10, 6))

# Plot latency curves for each thread
for tid in sorted(thread_data.keys()):
    if len(thread_data[tid]) > SKIP_FIRST:
        x_vals, y_vals = zip(*thread_data[tid][SKIP_FIRST:])
        ax1.plot(x_vals, y_vals, label=f"T{tid}")

ax1.set_xlabel("Iteration (C)")
ax1.set_ylabel("Avg Latency (us)")
ax1.set_xlim(0, max_c)
ax1.grid(True)
ax1.legend(loc="upper left", ncol=2, fontsize="small")

# Add temperature as second Y-axis
ax2 = ax1.twinx()
ax2.plot(temp_x, temp_values, color='red', linewidth=1.5, label='Temperature (°C)')
ax2.set_ylabel("Temperature (°C)", color='red')
ax2.tick_params(axis='y', labelcolor='red')

# Add combined legends
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize="small")

plt.title("Latency Over Time with Temperature Overlay")
plt.tight_layout()
plt.savefig(output_plot, dpi=150)
print(f"Chart saved as {output_plot}")

# ---- Step 7: Final latency statistics ----
all_mins = []
all_maxs = []
all_avgs = []
last_tid_values = {}

matches = list(pattern.finditer(text))
for match in matches:
    tid = int(match.group(1))
    c = int(match.group(2))
    min_v = int(match.group(3))
    avg = int(match.group(4))
    max_v = int(match.group(5))
    if c > 0:
        last_tid_values[tid] = (min_v, avg, max_v)

with open(output_stats, "w") as f:
    f.write("Latency Statistics per Thread (final cyclictest report only):\n")
    for tid in sorted(last_tid_values.keys()):
        min_val, avg_val, max_val = last_tid_values[tid]
        f.write(f"T{tid:2d} -> Min: {min_val} us, Max: {max_val} us, Avg: {avg_val:.2f} us\n")
        all_mins.append(min_val)
        all_maxs.append(max_val)
        all_avgs.append(avg_val)

    if all_mins and all_maxs and all_avgs:
        f.write("\nOverall:\n")
        f.write(f"Min: {min(all_mins)} us\n")
        f.write(f"Max: {max(all_maxs)} us\n")
        f.write(f"Avg: {sum(all_avgs)/len(all_avgs):.2f} us\n")

print(f"Statistics saved as {output_stats}")
