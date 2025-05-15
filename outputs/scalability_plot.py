import os
import sys
import re
import matplotlib.pyplot as plt

# ==============================================================================
# Improved Scheduler Scalability Plot Script + Statistics Output
# ==============================================================================

def print_help():
    print("Usage: python scalability_parser.py <input_file> <output_directory>")
    sys.exit(1)

# ------------------------- Argument Parsing -------------------------
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

# ------------------------- Output Paths -------------------------
basename = os.path.splitext(os.path.basename(input_file))[0]
plot_path = os.path.join(output_dir, f"{basename}_scalability_histogram.png")
stats_path = os.path.join(output_dir, f"{basename}_scalability_stats.txt")

# ------------------------- Parse the Sysbench Output -------------------------
threads = []
events_per_sec = []
total_events = []

with open(input_file, 'r') as f:
    lines = f.readlines()

current_threads = None
for i, line in enumerate(lines):
    line = line.strip()
    if line.startswith(">> Running sysbench with"):
        m = re.search(r"(\d+) threads", line)
        if m:
            current_threads = int(m.group(1))
    elif "events per second:" in line:
        m = re.search(r"events per second:\s+([\d.]+)", line)
        if m and current_threads is not None:
            eps = float(m.group(1))
            threads.append(current_threads)
            events_per_sec.append(eps)

            # Look ahead for total number of events
            for j in range(i, min(i+10, len(lines))):
                if "total number of events:" in lines[j]:
                    total = int(re.search(r"(\d+)", lines[j]).group(1))
                    total_events.append(total)
                    break
            else:
                total_events.append(None)

            current_threads = None

# ------------------------- Plot -------------------------
plt.figure(figsize=(16, 9))
bars = plt.bar(range(len(threads)), events_per_sec, width=0.6, color='skyblue', edgecolor='black')

plt.title("Sysbench CPU Scalability - Events per Second")
plt.xlabel("Number of Threads")
plt.ylabel("Events per Second")
plt.xticks(range(len(threads)), threads)
plt.grid(axis='y', linestyle='--', alpha=0.6)

# Annotate bars with total number of events
for i, bar in enumerate(bars):
    label = f"{total_events[i]}" if total_events[i] is not None else "N/A"
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height + 500, label, ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.savefig(plot_path)
plt.close()

# ------------------------- Statistics Output -------------------------
with open(stats_path, "w") as f:
    f.write("Sysbench Scalability Statistics\n")
    f.write("=================================\n\n")
    f.write(f"{'Threads':>8} | {'EPS':>10} | {'Total Events':>14} | {'% EPS Gain':>10} | {'% Eff Drop':>14}\n")
    f.write("-" * 70 + "\n")

    for i in range(len(threads)):
        t = threads[i]
        eps = events_per_sec[i]
        total = total_events[i] if total_events[i] is not None else 0
        gain = ""
        drop = ""
        eff = eps / t
        if i > 0:
            prev_eps = events_per_sec[i - 1]
            prev_eff = events_per_sec[i - 1] / threads[i - 1]
            gain = f"{((eps - prev_eps) / prev_eps) * 100:.1f}%"
            drop = f"{((prev_eff - eff) / prev_eff) * 100:.1f}%"
        f.write(f"{t:8d} | {eps:10.2f} | {total:14,} | {gain:>10} | {drop:>14}\n")

print(f"Scalability histogram saved to: {plot_path}")
print(f"Statistics saved to: {stats_path}")
