# process_connections.py

from collections import defaultdict
import matplotlib.pyplot as plt

connections = defaultdict(list)

with open("connections.txt", "r") as file:
    for line in file:
        parts = line.strip().split()
        if len(parts) != 9:  # Ensure all fields are present
            continue
        time, src_ip, dst_ip, src_port, dst_port, syn, ack, fin, reset = parts
        key = (src_ip, dst_ip, src_port, dst_port)
        connections[key].append((float(time), syn, ack, fin, reset))

durations = []
start_times = []

for key, packets in connections.items():
    syn_time = None
    fin_time = None
    reset_time = None

    for packet in packets:
        time, syn, ack, fin, reset = packet
        if syn == "1" and syn_time is None:
            syn_time = time
        if fin == "1" and ack == "1":
            fin_time = time
        if reset == "1":
            reset_time = time

    if syn_time is not None:
        if fin_time is not None:
            durations.append(fin_time - syn_time)
        elif reset_time is not None:
            durations.append(reset_time - syn_time)
        else:
            durations.append(100)  # Default duration
        start_times.append(syn_time)

# Plot connection duration vs. connection start time
plt.figure(figsize=(10, 6))
plt.scatter(start_times, durations, marker="o")
plt.axvline(x=20, color="r", linestyle="--", label="Attack Start")
plt.axvline(x=120, color="g", linestyle="--", label="Attack End")
plt.xlabel("Connection Start Time (s)")
plt.ylabel("Connection Duration (s)")
plt.title("Connection Duration vs. Start Time")
plt.legend()
plt.grid()
plt.savefig("connection_duration_plot.png")
plt.show()
