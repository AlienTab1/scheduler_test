import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==============================================================================
# Scheduler Starvation Parser
# ----------------------------
# Parses the output of a scheduler starvation test script and visualizes:
# - Per-PID CPU time progression
# - Boxplot of CPU time grouped by nice values
# - Outputs statistics useful for analyzing starvation
# ==============================================================================

def print_help():
    print("Usage: python starvation_parser.py <input_file> <output_directory>")
    sys.exit(1)

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
plot_progress_path = os.path.join(output_dir, f"{basename}_progression.png")
plot_boxplot_path = os.path.join(output_dir, f"{basename}_boxplot.png")
stats_path = os.path.join(output_dir, f"{basename}_stats.txt")

# ------------------------- Parse Input -------------------------
clk_tck = 100  # Default Linux clock ticks
logical_cpus = None

lines = []
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
            lines.append(line)

records = []
for line in lines:
    parts = line.split(',')
    if len(parts) != 6:
        continue
    try:
        timestamp = float(parts[0])
        starttime = float(parts[1])
        pid = int(parts[2])
        nice = int(parts[3])
        utime = int(parts[4])
        stime = int(parts[5])
        cpu_time = (utime + stime) / clk_tck
        uptime = (starttime + utime + stime) / clk_tck
        records.append((timestamp, starttime, pid, nice, utime, stime, cpu_time, uptime))
    except ValueError:
        continue

columns = ["timestamp", "starttime", "pid", "nice", "utime", "stime", "cpu_time", "uptime"]
df = pd.DataFrame(records, columns=columns)

# ------------------------- Align start time -------------------------
#boot_time = df["timestamp"].min() - (df["starttime"].min() / clk_tck)
#df["time_sec"] = df["timestamp"] - boot_time
#df["start_sec"] = boot_time + (df["starttime"] / clk_tck)

df["time_sec"] = df["timestamp"] - (df["starttime"] / clk_tck)


# ------------------------- Plot CPU Time Progression -------------------------
plt.figure(figsize=(16, 9))
colors = {-10: 'tab:blue', 19: 'tab:red'}
for (pid, nice), group in df.groupby(["pid", "nice"]):
    plt.plot(group["time_sec"], group["cpu_time"], alpha=0.3, color=colors.get(nice, 'gray'))

plt.title("CPU Time Progression per PID")
plt.xlabel("Wall Clock Time (seconds)")
plt.ylabel("CPU Time (seconds)")
plt.grid(True, linestyle='--', alpha=0.5)

# Hide offset label like "+1.747e9"
plt.gca().xaxis.get_offset_text().set_visible(False)

custom_lines = [
    plt.Line2D([0], [0], color='tab:blue', lw=2, label='High-priority (nice -10)'),
    plt.Line2D([0], [0], color='tab:red', lw=2, label='Low-priority (nice 19)')
]
plt.legend(handles=custom_lines)
plt.tight_layout()
plt.savefig(plot_progress_path, transparent=False)
plt.close()

# ------------------------- Plot Boxplot by Nice -------------------------
final_snapshot = df.sort_values("timestamp").groupby("pid").tail(1)

plt.figure(figsize=(10, 6))
#sns.boxplot(data=final_snapshot, x="nice", y="cpu_time", palette="Set2")
sns.boxplot(data=final_snapshot, x="nice", y="cpu_time", hue="nice", palette="Set2", legend=False)
plt.title("Final CPU Time per Process by Nice Value")
plt.xlabel("Nice Value")
plt.ylabel("CPU Time (seconds)")
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig(plot_boxplot_path, transparent=False)
plt.close()

# ------------------------- Write Summary Statistics -------------------------
with open(stats_path, "w") as f:
    f.write("Starvation Test Summary Statistics\n")
    f.write("=================================\n\n")
    f.write(f"Logical CPUs: {logical_cpus if logical_cpus else 'N/A'}\n")
    f.write(f"CLK_TCK: {clk_tck}\n")
    f.write(f"Sample Count: {len(df)}\n")
    f.write(f"Unique PIDs (seen in samples): {df['pid'].nunique()}\n")

    total_pids_declared = None
    with open(input_file) as raw:
        for line in raw:
            if "# Total PIDs being logged:" in line:
                total_pids_declared = int(line.split(':')[1].strip())
                f.write(f"Total PIDs declared in file: {total_pids_declared}\n")
                break

    f.write("\n")
    for nice_val, group in final_snapshot.groupby("nice"):
        f.write(f"Nice Value = {nice_val}:\n")
        f.write(f"  Count: {len(group)}\n")
        f.write(f"  Avg CPU Time: {group['cpu_time'].mean():.3f} s\n")
        f.write(f"  Min CPU Time: {group['cpu_time'].min():.3f} s\n")
        f.write(f"  Max CPU Time: {group['cpu_time'].max():.3f} s\n")
        f.write(f"  Std Dev: {group['cpu_time'].std():.3f} s\n")
        f.write("\n")

print(f"Plots saved to: {plot_progress_path} and {plot_boxplot_path}")
print(f"Statistics saved to: {stats_path}")
