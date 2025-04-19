import re
from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt

# Load your input file
with open("latency_pavlik.txt", "r") as file:
    text = file.read()

# Match each line with T: N C: X Avg: Y
pattern = re.compile(r"T:\s*(\d+).*?C:\s*(\d+).*?Avg:\s*(\d+)", re.MULTILINE)

# Track cumulative iteration counts and average latencies
thread_data = defaultdict(list)
cumulative_c = defaultdict(int)

for match in pattern.finditer(text):
    tid = int(match.group(1))
    c = int(match.group(2))
    avg = int(match.group(3))
    cumulative_c[tid] += c
    thread_data[tid].append((cumulative_c[tid], avg))

# Plotting
plt.figure(figsize=(8.15, 6.00))  # A4 portrait size in inches

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

# Save the output
plt.savefig("latency_chart.png", dpi=150)
print("✅ Chart saved as latency_chart.png")
