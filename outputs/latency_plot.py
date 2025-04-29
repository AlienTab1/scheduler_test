import re
import sys
import os
from collections import defaultdict
import matplotlib.pyplot as plt

def print_help():
    """Print usage help and exit."""
    print("Usage: python latency_plot.py <input_file> <output_directory>")
    sys.exit(1)

# ---- Step 1: Parse arguments ----
if len(sys.argv) != 3:
    print("Error: Missing arguments.\n")
    print_help()

input_file = sys.argv[1]
output_dir = sys.argv[2]

if not os.path.isfile(input_file):
    print(f"Error: File not found: {input_file}")
    sys.exit(1)

if not os.path.isdir(output_dir):
    print(f"Error: Output directory not found: {output_dir}")
    sys.exit(1)

# Prepare output filenames based on input filename
basename = os.path.splitext(os.path.basename(input_file))[0]
output_plot = os.path.join(output_dir, f"{basename}_latency_plot.png")
output_stats = os.path.join(output_dir, f"{basename}_latency_stats.txt")

# ---- Step 2: Parse input file ----
with open(input_file, "r") as file:
    text = file.read()

# Regex pattern to match each latency report line
pattern = re.compile(r"T:\s*(\d+).*?C:\s*(\d+).*?Min:\s*(\d+).*?Avg:\s*(\d+).*?Max:\s*(\d+)", re.MULTILINE)

thread_data = defaultdict(list)  # For plotting: (counter C, avg latency)

# Parse all matches in the input
for match in pattern.finditer(text):
    tid = int(match.group(1))   # Thread ID
    c = int(match.group(2))     # Counter C (number of iterations)
    min_v = int(match.group(3)) # Minimum latency
    avg = int(match.group(4))   # Average latency
    max_v = int(match.group(5)) # Maximum latency

    if c == 0:
        continue  # Ignore invalid measurements

    thread_data[tid].append((c, avg))  # Store real C value for correct plotting

# ---- Step 3: Generate plot ----

SKIP_FIRST = 1  # <<< Skip first N samples to avoid initial warm-up instability (set to 0 if not wanted)

plt.figure(figsize=(8.15, 6.00))

# Plot curve for each thread
for tid in sorted(thread_data.keys()):
    if len(thread_data[tid]) > SKIP_FIRST:
        x_vals, y_vals = zip(*thread_data[tid][SKIP_FIRST:])  # Skip first N points
        plt.plot(x_vals, y_vals, label=f"T{tid}")

plt.xlabel("Iteration (C)")
plt.ylabel("Avg Latency (us)")
plt.xlim(0, 10000)
plt.grid(True)
plt.legend(loc="upper right", ncol=2, fontsize="small")
plt.tight_layout()

plt.savefig(output_plot, dpi=150)
print(f"Chart saved as {output_plot}")

# ---- Step 4: Final statistics based ONLY on last cyclictest burst ----
all_mins = []
all_maxs = []
all_avgs = []

# Find only the last set of statistics
matches = list(pattern.finditer(text))
last_tid_values = {}

for match in matches:
    tid = int(match.group(1))
    c = int(match.group(2))
    min_v = int(match.group(3))
    avg = int(match.group(4))
    max_v = int(match.group(5))

    if c > 0:
        last_tid_values[tid] = (min_v, avg, max_v)  # Always overwrite to capture the latest valid stats

# Write statistics to output text file
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
