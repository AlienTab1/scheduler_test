import sys
import os
from collections import defaultdict
import matplotlib.pyplot as plt

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

# ----------------------- Step 1: Extract Header + Matching Lines -----------------------

cpu_threads = None
duration = None
stress_lines = []

with open(input_file, "r") as f:
    for line in f:
        stripped = line.strip()

        if "Current CPU threads:" in stripped:
            cpu_threads = int(stripped.split(":")[1])
        elif "Test duration:" in stripped:
            duration = int(stripped.split(":")[1].split()[0])
        elif "stress-ng-cpu" in stripped and not "|__" in stripped:
            stress_lines.append(stripped)

if cpu_threads is None or duration is None:
    print("Error: Missing CPU thread count or duration in the input.")
    sys.exit(1)

# ----------------------- Step 2: Parse TGID -> (sample_index, nvcswch/s) -----------------------

tgid_data = defaultdict(list)
sample_counter = 1
lines_in_current_sample = 0

for line in stress_lines:
    parts = line.split()
    if len(parts) < 7:
        continue  # malformed line

    tgid = parts[3]
    try:
        nvcswch = float(parts[6])
    except ValueError:
        continue

    tgid_data[tgid].append((sample_counter, nvcswch))
    lines_in_current_sample += 1

    if lines_in_current_sample == cpu_threads:
        sample_counter += 1
        lines_in_current_sample = 0

# ----------------------- Step 3: Plotting -----------------------

plt.figure(figsize=(10, 6))

for idx, (tgid, samples) in enumerate(sorted(tgid_data.items())):
    x_vals = [s[0] for s in samples]
    y_vals = [s[1] for s in samples]
    plt.plot(x_vals, y_vals, label=f"Thread_{idx}")

plt.xlabel("Sample Index (s)")
plt.ylabel("Involuntary Context Switches per Second (nvcswch/s)")
plt.title("Per-Thread Involuntary Context Switching Over Time")
plt.grid(True)
plt.legend(fontsize="small", loc="upper right", ncol=2)
plt.tight_layout()
plt.savefig(plot_path, dpi=150)

print(f"\nPlot saved as: {plot_path}")

# ----------------------- Optional Text Dump -----------------------

with open(text_path, "w") as f:
    f.write(f"Parsed nvcswch/s values per thread (Duration: {duration}s):\n\n")

    thread_totals = []
    thread_averages = []

    for idx, tgid in enumerate(sorted(tgid_data)):
        values = [val for _, val in tgid_data[tgid]]
        total = sum(values)
        avg = total / len(values) if values else 0
        thread_totals.append(total)
        thread_averages.append(avg)

        f.write(f"Thread_{idx} (Tgid {tgid}):\n")
        for x, val in tgid_data[tgid]:
            f.write(f"  Sample {x} -> {val:.2f} cswch/s\n")
        f.write(f"  Total: {total:.2f} cswch/s\n")
        f.write(f"  Average: {avg:.2f} cswch/s\n\n")

    overall_total = sum(thread_totals)
    overall_avg = sum(thread_averages) / len(thread_averages) if thread_averages else 0

    f.write("--- Overall Statistics ---\n")
    f.write(f"Total CS across all threads: {overall_total:.2f} cswch/s\n")
    f.write(f"Average per thread: {overall_avg:.2f} cswch/s\n")


print(f"Parsed data written to: {text_path}")
