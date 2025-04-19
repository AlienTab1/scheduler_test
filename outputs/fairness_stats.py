import re
from collections import defaultdict
import statistics

with open('thread_lwps.txt') as f:
    lwps = set(line.strip() for line in f)

stats = defaultdict(lambda: {
    'cpu_times_us': [],
    'wait_times_us': [],
    'switches': 0,
    'last_on_timestamp_us': None,
    'last_off_timestamp_us': None,
    'on_cpu': False
})

sched_switch_re = re.compile(
    r'sched_switch: prev_comm=.* prev_pid=(\d+) .* ==> next_comm=.* next_pid=(\d+) '
)
runtime_re = re.compile(
    r'sched_stat_runtime: comm=.* pid=(\d+) runtime=(\d+) \[ns\]'
)

with open('perf_trace.txt') as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) < 5 or ':' not in parts[3]:
            continue

        try:
            timestamp_sec = float(parts[3].rstrip(':'))
        except ValueError:
            continue

        timestamp_us = int(timestamp_sec * 1e6)

        if 'sched_switch:' in line:
            match = sched_switch_re.search(line)
            if match:
                prev_pid, next_pid = match.groups()

                if prev_pid in lwps:
                    prev_data = stats[prev_pid]
                    if prev_data['on_cpu'] and prev_data['last_on_timestamp_us'] is not None:
                        cpu_time = timestamp_us - prev_data['last_on_timestamp_us']
                        prev_data['cpu_times_us'].append(cpu_time)
                    prev_data['on_cpu'] = False
                    prev_data['last_off_timestamp_us'] = timestamp_us
                    prev_data['switches'] += 1

                if next_pid in lwps:
                    next_data = stats[next_pid]
                    if not next_data['on_cpu']:
                        if next_data['last_off_timestamp_us'] is not None:
                            wait_time = timestamp_us - next_data['last_off_timestamp_us']
                            next_data['wait_times_us'].append(wait_time)
                        next_data['on_cpu'] = True
                        next_data['last_on_timestamp_us'] = timestamp_us

        elif 'sched_stat_runtime:' in line:
            match = runtime_re.search(line)
            if match:
                pid, runtime_ns = match.groups()
                if pid in lwps:
                    runtime_us = int(runtime_ns) // 1000
                    stats[pid]['cpu_times_us'].append(runtime_us)

# Collect overall statistics
pid_cpu_totals = []
pid_wait_totals = []
pid_switch_totals = []

for pid, data in stats.items():
    total_cpu_time = sum(data['cpu_times_us'])
    total_wait_time = sum(data['wait_times_us'])
    total_switches = data['switches']

    pid_cpu_totals.append(total_cpu_time)
    pid_wait_totals.append(total_wait_time)
    pid_switch_totals.append(total_switches)

    print(f"PID: {pid}")
    print(f"  Total CPU Time: {total_cpu_time} µs")
    print(f"  Total Wait Time: {total_wait_time} µs")
    print(f"  CPU Switches: {total_switches}")
    print()

# Overall statistics across all PIDs (based on PID totals)
print("--- Overall Statistics (per PID aggregated) ---")
if pid_cpu_totals:
    print(f"Average Total CPU Time: {statistics.mean(pid_cpu_totals):.2f} µs")
    print(f"Max Total CPU Time: {max(pid_cpu_totals)} µs")
    print(f"Min Total CPU Time: {min(pid_cpu_totals)} µs")
else:
    print("No CPU time data available.")

if pid_wait_totals:
    print(f"Average Total Wait Time: {statistics.mean(pid_wait_totals):.2f} µs")
    print(f"Max Total Wait Time: {max(pid_wait_totals)} µs")
    print(f"Min Total Wait Time: {min(pid_wait_totals)} µs")
else:
    print("No wait time data available.")

if pid_switch_totals:
    print(f"Average CPU Switches: {statistics.mean(pid_switch_totals):.2f}")
    print(f"Max CPU Switches: {max(pid_switch_totals)}")
    print(f"Min CPU Switches: {min(pid_switch_totals)}")
else:
    print("No CPU switch data available.")
