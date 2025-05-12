import re
import sys
import os
from collections import defaultdict
import matplotlib.pyplot as plt
from statistics import mean

def print_help():
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

# ---- Step 2: Output filenames ----
basename = os.path.splitext(os.path.basename(latency_file))[0]
output_plot_combined = os.path.join(output_dir, f"{basename}_combined_plot.png")
output_plot_latency_only = os.path.join(output_dir, f"{basename}_latency_only_plot.png")
output_stats = os.path.join(output_dir, f"{basename}_combined_stats.txt")

# ---- Step 3: Parse latency data ----
with open(latency_file, "r") as file:
    text = file.read()

pattern = re.compile(r"T:\s*(\d+).*?C:\s*(\d+).*?Min:\s*(\d+).*?Avg:\s*(\d+).*?Max:\s*(\d+)", re.MULTILINE)
thread_data = defaultdict(list)
last_tid_values = {}

for match in pattern.finditer(text):
    tid = int(match.group(1))
    c = int(match.group(2))
    min_v = int(match.group(3))
    avg = int(match.group(4))
    max_v = int(match.group(5))
    if c == 0:
        continue
    thread_data[tid].append((c, avg))
    last_tid_values[tid] = (min_v, avg, max_v)

# ---- Step 4: Parse temperature and frequency data (universal CPU splitting) ----
grouped_data = defaultdict(lambda: {'temps': [], 'group_a': [], 'group_b': []})
all_cpu_ids = set()

with open(temp_file, 'r') as f:
    for line in f:
        ts_match = re.search(r'Timestamp: (\d+)', line)
        temp_match = re.search(r'CPU_Temperature: (\d+)', line)
        if not ts_match or not temp_match:
            continue
        timestamp = int(ts_match.group(1))
        temperature = int(temp_match.group(1))

        cpu_matches = re.findall(r'cpu(\d+): (\d+)kHz', line)
        cpu_freqs = {int(cpu_id): int(freq) for cpu_id, freq in cpu_matches}
        all_cpu_ids.update(cpu_freqs.keys())

        sorted_cpu_ids = sorted(all_cpu_ids)
        mid_index = len(sorted_cpu_ids) // 2
        group_a_ids = sorted_cpu_ids[:mid_index]
        group_b_ids = sorted_cpu_ids[mid_index:]

        group = grouped_data[timestamp]
        group['temps'].append(temperature)
        group['group_a'].append(mean([cpu_freqs[cpu] for cpu in group_a_ids if cpu in cpu_freqs]) / 1e6)
        group['group_b'].append(mean([cpu_freqs[cpu] for cpu in group_b_ids if cpu in cpu_freqs]) / 1e6)

# Time-aligned data
sorted_ts = sorted(grouped_data.keys())
base_ts = sorted_ts[0]
time_axis = [ts - base_ts for ts in sorted_ts]
avg_temps = [mean(grouped_data[ts]['temps']) for ts in sorted_ts]
avg_group_a = [mean(grouped_data[ts]['group_a']) for ts in sorted_ts]
avg_group_b = [mean(grouped_data[ts]['group_b']) for ts in sorted_ts]

# Dynamic labels for CPU groups
sorted_cpu_ids = sorted(all_cpu_ids)
mid_index = len(sorted_cpu_ids) // 2
label_a = f"CPU{sorted_cpu_ids[0]}–{sorted_cpu_ids[mid_index - 1]}" if mid_index > 0 else f"CPU{sorted_cpu_ids[0]}"
label_b = f"CPU{sorted_cpu_ids[mid_index]}–{sorted_cpu_ids[-1]}" if mid_index < len(sorted_cpu_ids) else f"CPU{sorted_cpu_ids[-1]}"

# ---- Step 5a: Combined plot (latency + temp + freqs) ----
fig, axs = plt.subplots(4, 1, figsize=(18, 12), sharex=False)

# Latency (subplot 1)
for tid in sorted(thread_data.keys()):
    x_vals, y_vals = zip(*thread_data[tid])
    axs[0].plot(x_vals, y_vals, label=f"T{tid}")
axs[0].set_ylabel("Latency (us)")
axs[0].set_title("Avg Latency per Thread")
axs[0].legend(fontsize="x-small", ncol=2)
axs[0].set_xlabel("Iteration (C)")
axs[0].grid(True)

# Temperature (subplot 2)
axs[1].plot(time_axis, avg_temps, color='red')
axs[1].set_ylabel("Temp (°C)")
axs[1].set_title("CPU Temperature")
axs[1].grid(True)

# CPU Group A (subplot 3)
axs[2].plot(time_axis, avg_group_a, color='blue')
axs[2].set_ylabel("Freq (GHz)")
axs[2].set_title(f"Avg Frequency {label_a}")
axs[2].grid(True)

# CPU Group B (subplot 4)
axs[3].plot(time_axis, avg_group_b, color='green')
axs[3].set_ylabel("Freq (GHz)")
axs[3].set_title(f"Avg Frequency {label_b}")
axs[3].set_xlabel("Time (s)")
axs[3].grid(True)

plt.tight_layout()
for ax in axs:
    ax.set_xlim(left=0)
plt.savefig(output_plot_combined, dpi=150)
plt.close()
print(f"Combined plot saved as {output_plot_combined}")

# ---- Step 5b: Latency-only plot ----
plt.figure(figsize=(10, 6))
for tid in sorted(thread_data.keys()):
    x_vals, y_vals = zip(*thread_data[tid])
    plt.plot(x_vals, y_vals, label=f"T{tid}")
plt.xlabel("Iteration (C)")
plt.ylabel("Avg Latency (us)")
plt.title("Latency Over Time (No Temperature or Frequency)")
plt.xlim(left=0)
plt.grid(True)
plt.legend(loc="upper right", ncol=2, fontsize="small")
plt.tight_layout()
plt.savefig(output_plot_latency_only, dpi=150)
print(f"Latency-only plot saved as {output_plot_latency_only}")

# ---- Step 6: Combined stats ----
with open(output_stats, "w") as f:
    f.write("Latency Statistics per Thread (last reported value):\n")
    all_mins, all_maxs, all_avgs = [], [], []
    for tid in sorted(last_tid_values.keys()):
        min_val, avg_val, max_val = last_tid_values[tid]
        f.write(f"T{tid:2d} -> Min: {min_val} us, Max: {max_val} us, Avg: {avg_val:.2f} us\n")
        all_mins.append(min_val)
        all_maxs.append(max_val)
        all_avgs.append(avg_val)

    if all_mins:
        f.write("\nOverall Latency:\n")
        f.write(f"Min: {min(all_mins)} us\n")
        f.write(f"Max: {max(all_maxs)} us\n")
        f.write(f"Avg: {sum(all_avgs)/len(all_avgs):.2f} us\n")

    if avg_temps:
        f.write(f"\nTemperature:\nMin: {min(avg_temps)} °C\nMax: {max(avg_temps)} °C\nAvg: {sum(avg_temps)/len(avg_temps):.2f} °C\n")

    if avg_group_a and avg_group_b:
        f.write(f"\nCPU Frequencies (GHz):\n")
        f.write(f"{label_a} Avg: {sum(avg_group_a)/len(avg_group_a):.2f} GHz\n")
        f.write(f"{label_b} Avg: {sum(avg_group_b)/len(avg_group_b):.2f} GHz\n")

print(f"Statistics saved as {output_stats}")
