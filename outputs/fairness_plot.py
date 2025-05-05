import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==============================================================================
# Fairness Log Parser
# --------------------
# This script processes hackbench scheduler fairness logs.
# For each unique PID, it calculates:
# - CPU time (user + system) using utime + stime
# - Wall time based on timestamps and process start time
# - Group-level fairness statistics aggregated by 'nice' level
# - Efficiency metrics:
#     - CPU Efficiency = CPU time / wall time
#     - Group CPU Utilization = total CPU time / (lifetime span × logical CPUs)
# It outputs three plots and a text summary.
# ==============================================================================

def print_help():
    print("Usage: python fairness_parser.py <input_file> <output_directory>")
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
stats_path = os.path.join(output_dir, f"{basename}_fairness_stats.txt")
boxplot_path = os.path.join(output_dir, f"{basename}_boxplot_cpu_time.png")
utilization_path = os.path.join(output_dir, f"{basename}_barplot_utilization.png")

# ------------------------- Read and Parse Input -------------------------
logical_cpus = None
clk_tck = 100  # Default CLK_TCK
data_lines = []

with open(input_file, 'r') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        if line.startswith("# Logical CPUs:"):
            logical_cpus = int(line.split(":")[1].strip())
        elif line.startswith("# CLK_TCK:"):
            clk_tck = int(line.split(":")[1].strip())
        elif line[0].isdigit():
            data_lines.append(line)

# ------------------------- Parse Raw Data into DataFrame -------------------------
records = []
for line in data_lines:
    parts = line.split(',')
    if len(parts) != 6:
        continue
    ts, st, pid, nice, utime, stime = parts
    try:
        ts = float(ts)
        st = float(st)
        pid = int(pid)
        nice = int(nice)
        ut = int(utime)
        stt = int(stime)
        ut_sec = ut / clk_tck
        st_sec = stt / clk_tck
        cpu_time = ut_sec + st_sec
        records.append((ts, st, pid, nice, ut, stt, ut_sec, st_sec, cpu_time))
    except:
        continue

columns = [
    "timestamp", "starttime", "pid", "nice", "utime", "stime",
    "utime_sec", "stime_sec", "cpu_time"
]
df = pd.DataFrame(records, columns=columns)

# ------------------------- Align Starttime to Real Clock -------------------------
boot_time = df["timestamp"].min() - (df["starttime"].min() / clk_tck)
df["start_sec"] = boot_time + (df["starttime"] / clk_tck)

# ------------------------- Select Final Snapshot Per PID -------------------------
last_rows = df.sort_values("timestamp").groupby("pid").tail(1)
first_start = df.groupby("pid")["start_sec"].min().reset_index().rename(columns={"start_sec": "start_sec_first"})
summary = pd.merge(last_rows, first_start, on="pid", how="left")
summary["wall_time"] = summary["timestamp"] - summary["start_sec_first"]

# ------------------------- Group By Nice Value -------------------------
grouped = summary.groupby("nice").agg(
    count=("pid", "count"),
    avg_cpu_time=("cpu_time", "mean"),
    median_cpu_time=("cpu_time", "median"),
    std_cpu_time=("cpu_time", "std"),
    avg_wall_time=("wall_time", "mean"),
    total_wall_time=("wall_time", "sum"),
    total_cpu_time=("cpu_time", "sum"),
    span_start=("start_sec_first", "min"),
    span_end=("timestamp", "max")
).reset_index()

grouped["lifetime_span"] = grouped["span_end"] - grouped["span_start"]
grouped["avg_cpu_efficiency"] = grouped["avg_cpu_time"] / grouped["avg_wall_time"]
grouped["utilization"] = grouped["total_cpu_time"] / (grouped["lifetime_span"] * logical_cpus)

# ------------------------- Plot: Boxplot of CPU Time -------------------------
plt.figure(figsize=(10, 6))
sns.boxplot(data=summary, x="nice", y="cpu_time", palette="Blues")
plt.title("Boxplot: CPU Time per Nice Value")
plt.xlabel("Nice Value")
plt.ylabel("CPU Time (seconds)")
plt.ylim(0.60, 0.90)
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig(boxplot_path)
plt.close()

# ------------------------- Plot: Barplot Utilization -------------------------
plt.figure(figsize=(10, 6))
sns.barplot(data=grouped, x="nice", y="utilization", palette="Oranges")
plt.title("Group CPU Utilization by Nice Value")
plt.xlabel("Nice Value")
plt.ylabel("CPU Utilization (%)")
plt.ylim(0, 1)
plt.tight_layout()
plt.savefig(utilization_path)
plt.close()

# ------------------------- Save Summary Statistics -------------------------
with open(stats_path, "w") as f:
    f.write("Fairness Test Summary Statistics (Per Unique PID)\n")
    f.write("==================================================\n\n")
    f.write(f"Logical CPUs: {logical_cpus if logical_cpus else 'N/A'}\n")
    f.write(f"CLK_TCK: {clk_tck}\n\n")

    for _, row in grouped.iterrows():
        f.write(f"Nice = {int(row['nice'])}:\n")
        f.write(f"  Count: {int(row['count'])}\n")
        f.write(f"  Avg CPU Time: {row['avg_cpu_time']:.2f} s\n")
        f.write(f"  Median CPU Time: {row['median_cpu_time']:.2f} s\n")
        f.write(f"  Std Dev: {row['std_cpu_time']:.2f} s\n")
        f.write(f"  Avg Wall Time: {row['avg_wall_time']:.2f} s\n")
        f.write(f"  Total Wall Time: {row['total_wall_time']:.2f} s\n")
        f.write(f"  Total CPU Time: {row['total_cpu_time']:.2f} s\n")
        f.write(f"  Lifetime Span: {row['lifetime_span']:.2f} s\n")
        f.write(f"  Avg CPU Efficiency (CPU time / wall time): {row['avg_cpu_efficiency']:.2%}\n")
        f.write(f"  Group CPU Utilization (% of cores used, total_cpu_time / (lifetime_span * logical_cpus)): {row['utilization']:.2%}\n\n")

print(f"Statistics saved: {stats_path}")
