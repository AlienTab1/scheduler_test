import re
import sys
import os
import matplotlib.pyplot as plt


def print_help():
    print("Usage: python sysbench_parser.py <input_file> <output_directory>")
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

basename = os.path.splitext(os.path.basename(input_file))[0]
output_plot = os.path.join(output_dir, f"{basename}_events_histogram.png")
output_stats = os.path.join(output_dir, f"{basename}_sysbench_stats.txt")

# ---- Step 2: Parse input file ----
with open(input_file, 'r') as file:
    content = file.read()

# Extract thread count
thread_count_match = re.search(r'Current CPU threads:\s*(\d+)', content)
thread_count = thread_count_match.group(1) if thread_count_match else "N/A"

# Append fake separator to ensure last scenario is captured properly
scenarios = re.findall(r"=== (Scenario .*?) ===(.*?)(?=^===|\Z)", content + "\n===", re.DOTALL | re.MULTILINE)

data = []
scenario_labels = []
total_events = []

for scenario, details in scenarios:
    time_match = re.search(r'total time:\s+(\d+\.\d+)s', details)
    events_match = re.search(r'total number of events:\s+(\d+)', details)
    eps_match = re.search(r'events per second:\s+(\d+\.\d+)', details)

    if time_match and events_match and eps_match:
        total_time = float(time_match.group(1))
        total_event_count = int(events_match.group(1))
        eps = float(eps_match.group(1))

        label = f"{int(total_time)}s"
        if re.search(r'with .*?background load', scenario, re.IGNORECASE):
            label += " + bg"

        scenario_data = {
            'scenario': scenario.strip(),
            'total_time': total_time,
            'total_events': total_event_count,
            'events_per_second': eps
        }
        data.append(scenario_data)
        scenario_labels.append(label)
        total_events.append(total_event_count)

# ---- Step 3: Generate histogram plot ----
plt.figure(figsize=(10, 6))
bars = plt.bar(scenario_labels, total_events, color='skyblue')
plt.xlabel('Test scenario: (test execution time) + (with or without background load)')
plt.ylabel('Total Number of Events')
plt.title('Sysbench Total Events per Scenario')

# Custom legend for thread info
plt.legend([f"Thread count: {thread_count}"], loc="upper left", fontsize="small", frameon=False)
#plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', linestyle='--', alpha=0.7)
for bar, value in zip(bars, total_events):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"{value:,}", 
             ha='center', va='bottom', fontsize=8, rotation=0)

plt.tight_layout()
plt.savefig(output_plot, dpi=150)
print(f"Chart saved as {output_plot}")

# ---- Step 4: Output statistics ----
with open(output_stats, "w") as f:
    f.write("Sysbench Scenario Statistics:\n")
    for entry in data:
        f.write(f"{entry['scenario']}\n")
        f.write(f"  Total Time: {entry['total_time']} s\n")
        f.write(f"  Total Events: {entry['total_events']}\n")
        f.write(f"  Events per Second: {entry['events_per_second']}\n\n")

print(f"Statistics saved as {output_stats}")
