import re
import sys
import os
from collections import defaultdict
import matplotlib.pyplot as plt

def print_help():
    print("Usage: python plot_latency_from_cyclictest.py <input_file> [output_file]")
    print("  <input_file>   Path to latency log file (e.g., from cyclictest)")
    print("  [output_file]  Optional: name of output PNG file (default: latency_chart.png)")
    sys.exit(1)

# ---- Step 1: Parse command-line arguments ----
if len(sys.argv) < 2:
    print("Error: Missing input file.\n")
    print_help()

input_file = sys.argv[1]
output_file = sys.argv[2] if len(sys.argv) > 2 else "latency_chart.png"

if not os.path.isfile(input_file):
    print(f"Error: File not found: {input_file}")
    sys.exit(1)

# ---- Step 2: Parse the file ----
with open(input_file, "r") as file:
    text = file.read()

pattern = re.compile(r"T:\s*(\d+).*?C:\s*(\d+).*?Avg:\s*(\d+)", re.MULTILINE)

thread_data = defaultdict(list)
cumulative_c = defaultdict(int)

for match in pattern.finditer(text):
    tid = int(match.group(1))
    c = int(match.group(2))
    avg = int(match.group(3))
    cumulative_c[tid] += c
    thread_data[tid].append((cumulative_c[tid], avg))

# ---- Step 3: Plotting ----
plt.figure(figsize=(8.15, 6.00))  

for tid, values in thread_data.items():
    if len(values) > 1:
        x_vals, y_vals = zip(*values)
        plt.plot(x_vals, y_vals, label=f"T{tid}")

#plt.title("Thread Avg Latency vs. Cumulative Iteration")
plt.xlabel("Iteration (C)")
plt.ylabel("Avg Latency (us)")
plt.xlim(0, 10000)
plt.grid(True)
plt.legend(loc="lower right", ncol=2, fontsize="small")
plt.tight_layout()

plt.savefig(output_file, dpi=150)
print(f"Chart saved as {output_file}")
