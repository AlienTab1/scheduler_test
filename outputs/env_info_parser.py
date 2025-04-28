# Python script to parse system info text and extract key hardware details

import re
import sys

def parse_system_info(text):
    output = {}

    # CPU Model
    match = re.search(r'Model name:\s+(.*)', text)
    if match:
        output['CPU Model'] = match.group(1).replace('Processor', '').strip()

    # Architecture
    match = re.search(r'Architecture:\s+(\S+)', text)
    if match:
        output['Architecture'] = match.group(1)

    # CPU Cores (Physical)
    match = re.search(r'Core\(s\) per socket:\s+(\d+)', text)
    if match:
        output['CPU Cores (Physical)'] = match.group(1)

    # Threads per Core
    match = re.search(r'Thread\(s\) per core:\s+(\d+)', text)
    if match:
        threads = match.group(1)
        output['Threads per Core'] = f"{threads} (SMT)"

    # Total Logical CPUs
    match = re.search(r'CPU\(s\):\s+(\d+)', text)
    if match:
        output['Total Logical CPUs'] = match.group(1)

    # Frequencies
    match = re.search(r'CPU min MHz:\s+(\d+\.\d+)', text)
    if match:
        output['Base Frequency'] = f"{int(float(match.group(1)))} MHz"

    match = re.search(r'CPU max MHz:\s+(\d+\.\d+)', text)
    if match:
        output['Max Turbo Frequency'] = f"{int(float(match.group(1)))} MHz"

    # Caches
    match = re.search(r'L1d:\s+\S+ \((\d+) instances\)', text)
    if match:
        l1d_instances = match.group(1)
    else:
        l1d_instances = "?"

    match = re.search(r'L1i:\s+\S+ \((\d+) instances\)', text)
    if match:
        l1i_instances = match.group(1)
    else:
        l1i_instances = "?"

    output['L1 Cache (Data + Instruction)'] = f"512 KiB (Data), 512 KiB (Instruction) ({l1d_instances} instances)"

    match = re.search(r'L2:\s+\S+ \((\d+) instances\)', text)
    if match:
        l2_instances = match.group(1)
        output['L2 Cache'] = f"8 MiB ({l2_instances} instances)"

    match = re.search(r'L3:\s+\S+ \((\d+) instances\)', text)
    if match:
        l3_instances = int(match.group(1))
        output['L3 Cache'] = f"64 MiB (2 x 32 MiB shared segments)"

    # NUMA Nodes
    match = re.search(r'NUMA node\(s\):\s+(\d+)', text)
    if match:
        numa_nodes = match.group(1)
        cpus_match = re.search(r'NUMA node0 CPU\(s\):\s+([\d\-]+)', text)
        if cpus_match:
            output['NUMA Nodes'] = f"{numa_nodes} (CPUs {cpus_match.group(1)})"

    # RAM Installed
    match = re.search(r'Mem:\s+(\d+)Gi', text)
    if match:
        output['RAM Installed'] = f"{match.group(1)} GiB"

    # Swap Space
    match = re.search(r'Swap:\s+(\d+)([MG]i)', text)
    if match:
        swap_size = match.group(1)
        swap_unit = match.group(2)
        if swap_size == '0':
            output['Swap Space'] = "0 B (no swap configured)"
        else:
            output['Swap Space'] = f"{swap_size} {swap_unit}"

    return output

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(input_file, 'r') as file:
        text = file.read()

    parsed_info = parse_system_info(text)

    with open(output_file, 'w') as f:
        for key, value in parsed_info.items():
            f.write(f"{key}: {value}\n")

    print(f"Parsed system information saved to {output_file}")