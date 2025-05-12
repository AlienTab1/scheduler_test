import re
import os
import sys
import csv
import matplotlib.pyplot as plt
from collections import defaultdict
from statistics import mean

def parse_and_plot(data_file_path, output_dir):
    with open(data_file_path, 'r') as file:
        lines = file.readlines()

    grouped_data = defaultdict(lambda: {'temps': [], 'cpu0_7': [], 'cpu8_15': []})

    for line in lines:
        ts_match = re.search(r'Timestamp: (\d+)', line)
        temp_match = re.search(r'CPU_Temperature: (\d+)', line)
        if not ts_match or not temp_match:
            continue

        timestamp = int(ts_match.group(1))
        temperature = int(temp_match.group(1))

        cpu_matches = re.findall(r'cpu(\d+): (\d+)kHz', line)
        cpu_freqs = {int(cpu_id): int(freq) for cpu_id, freq in cpu_matches}

        group = grouped_data[timestamp]
        group['temps'].append(temperature)
        group['cpu0_7'].append(mean([cpu_freqs[cpu] for cpu in range(0, 8) if cpu in cpu_freqs]) / 1e6)
        group['cpu8_15'].append(mean([cpu_freqs[cpu] for cpu in range(8, 16) if cpu in cpu_freqs]) / 1e6)

    sorted_ts = sorted(grouped_data.keys())
    base_ts = sorted_ts[0]

    final_timestamps = []
    avg_temps = []
    avg_0_7 = []
    avg_8_15 = []

    for ts in sorted_ts:
        final_timestamps.append(ts - base_ts)  # true relative time
        avg_temps.append(mean(grouped_data[ts]['temps']))
        avg_0_7.append(mean(grouped_data[ts]['cpu0_7']))
        avg_8_15.append(mean(grouped_data[ts]['cpu8_15']))

    os.makedirs(output_dir, exist_ok=True)

    # Export to CSV
    csv_path = os.path.join(output_dir, 'cpu_averages.csv')
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Time (s)', 'CPU Temp (°C)', 'Avg CPU0–7 (GHz)', 'Avg CPU8–15 (GHz)'])
        for i in range(len(final_timestamps)):
            writer.writerow([final_timestamps[i], avg_temps[i], avg_0_7[i], avg_8_15[i]])

    # Plot
    fig, axs = plt.subplots(3, 1, figsize=(18, 10), sharex=True)

    axs[0].plot(final_timestamps, avg_temps, color='tab:red')
    axs[0].set_ylabel("Temp (°C)")
    axs[0].set_title("CPU Temperature")

    axs[1].plot(final_timestamps, avg_0_7, color='tab:blue')
    axs[1].set_ylabel("Freq (GHz)")
    axs[1].set_title("Average CPU0–7 Frequency")

    axs[2].plot(final_timestamps, avg_8_15, color='tab:green')
    axs[2].set_ylabel("Freq (GHz)")
    axs[2].set_title("Average CPU8–15 Frequency")
    axs[2].set_xlabel("Time (s)")

    for ax in axs:
        ax.grid(True)

    plt.tight_layout()
    axs[2].set_xlim(left=0) 
    plt.savefig(os.path.join(output_dir, 'combined_metrics.png'))
    plt.close()

    print(f"Saved: {csv_path}")
    print(f"Saved: {os.path.join(output_dir, 'combined_metrics.png')}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python parse_cpu_data.py <data_file_path> <output_directory>")
        sys.exit(1)

    data_file = sys.argv[1]
    output_dir = sys.argv[2]
    parse_and_plot(data_file, output_dir)
