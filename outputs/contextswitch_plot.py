import sys
import os
from collections import defaultdict
from datetime import datetime
import matplotlib.pyplot as plt
from statistics import mean, stdev

def print_help():
    print("Usage: python extract_stress_lines.py <input_file> <output_directory>")
    sys.exit(1)

# ----------------------- Argument Parsing -----------------------
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

basename = os.path.splitext(os.path.basename(input_file))[0]
plot_path = os.path.join(output_dir, f"{basename}_plot.png")
text_path = os.path.join(output_dir, f"{basename}_parsed.txt")

# ----------------------- Step 1: Extract Relevant Lines -----------------------
cpu_threads = None
duration = None
stress_lines = []

with open(input_file, "r") as f:
    for line in f:
        stripped = line.strip()
        if "Current logical CPUs:" in stripped:
            cpu_threads = int(stripped.split(":")[1].strip())
        elif "Test duration:" in stripped:
            duration = int(stripped.split(":")[1].strip().split()[0])
        elif "stress-ng-cpu" in stripped and "|__" not in stripped:
            stress_lines.append(stripped)

if cpu_threads is None or duration is None:
    print("Error: Missing CPU thread count or duration in the input.")
    sys.exit(1)

# ----------------------- Step 2: Parse TGID → (timestamp, nvcswch/s) -----------------------
tgid_data = defaultdict(list)
base_timestamp = None

for line in stress_lines:
    parts = line.split()
    if len(parts) < 7:
        continue

    try:
        timestamp = datetime.strptime(parts[0], "%H:%M:%S")
        if base_timestamp is None:
            base_timestamp = timestamp
        rel_second = int((timestamp - base_timestamp).total_seconds())

        tgid = parts[2]
        nvcswch = float(parts[5])
        tgid_data[tgid].append((rel_second, nvcswch))
    except Exception:
        continue

# ----------------------- Step 3: Plotting -----------------------
plt.figure(figsize=(12, 7))

all_times = [t for samples in tgid_data.values() for t, _ in samples]
x_min = int(min(all_times))
x_max = int(max(all_times))

for idx, (tgid, samples) in enumerate(sorted(tgid_data.items())):
    x_vals = [round(s[0]) for s in samples]
    y_vals = [s[1] for s in samples]
    plt.plot(x_vals, y_vals, label=f"T{idx}")

plt.xlabel("Time (s)")
plt.ylabel("Involuntary Context Switches per Second (nvcswch/s)")
plt.title("Per-Thread Involuntary Context Switching")
plt.grid(True)
plt.legend(fontsize="small", loc="upper right", ncol=2)
plt.xlim(x_min, x_max)
plt.xticks(range(x_min, x_max + 1))
plt.tight_layout()
plt.savefig(plot_path, dpi=150)
print(f"\nPlot saved as: {plot_path}")

# ----------------------- Step 4: Write Stats -----------------------
with open(text_path, "w") as f:
    f.write(f"Parsed nvcswch/s values per thread (Duration: {duration}s):\n\n")

    thread_totals = []
    thread_averages = []
    all_switches = []

    for idx, tgid in enumerate(sorted(tgid_data)):
        values = [val for _, val in tgid_data[tgid]]
        total = sum(values)
        avg = total / len(values) if values else 0
        thread_totals.append(total)
        thread_averages.append(avg)
        all_switches.extend(values)

        f.write(f"Thread_{idx} (Tgid {tgid}):\n")
        for sec, val in tgid_data[tgid]:
            f.write(f"  Second {sec} -> {val:.2f} nvcswch/s\n")
        f.write(f"  Total: {total:.2f} nvcswch/s\n")
        f.write(f"  Average: {avg:.2f} nvcswch/s\n\n")

    overall_total = sum(thread_totals)
    overall_avg = sum(thread_averages) / len(thread_averages) if thread_averages else 0
    peak_value = max(all_switches) if all_switches else 0
    stddev_avg = stdev(thread_averages) if len(thread_averages) > 1 else 0
    max_avg = max(thread_averages) if thread_averages else 0
    min_avg = min(thread_averages) if thread_averages else 1  # avoid div by zero
    imbalance_ratio = (max_avg / min_avg) if min_avg != 0 else float('inf')

    f.write("--- Overall Statistics ---\n")
    f.write(f"Total CS across all threads: {overall_total:.2f} cswch/s\n")
    f.write(f"Average per thread: {overall_avg:.2f} cswch/s\n")
    f.write(f"Peak context switch rate (max nvcswch/s): {peak_value:.2f}\n")
    f.write(f"Standard deviation of per-thread averages: {stddev_avg:.2f}\n")
    f.write(f"Thread avg max/min ratio (imbalance): {imbalance_ratio:.2f}\n")

print(f"Parsed data written to: {text_path}")
