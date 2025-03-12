from collections import defaultdict
import matplotlib.pyplot as plt

# Dictionary to store connection details
connections = defaultdict(list)

# Read the connections file
with open("connections.txt", "r") as file:
    for line in file:
        time, src_ip, dst_ip, src_port, dst_port, syn, ack, fin, reset = line.strip().split()
        key = (src_ip, dst_ip, src_port, dst_port)
        reverse_key = (dst_ip, src_ip, dst_port, src_port)  # To handle flipped ports during closure
        connections[key].append((float(time), syn, ack, fin, reset))
        connections[reverse_key].append((float(time), syn, ack, fin, reset))

# Lists to store connection durations and start times
durations = []
start_times = []

# Process each connection
for key, packets in connections.items():
    syn_time = None
    ack_received = False
    connection_closed = False
    end_time = None
    
    for packet in packets:
        time, syn, ack, fin, reset = packet
        time = float(time)

        # Track the first SYN packet
        if syn == "1" and syn_time is None:
            syn_time = time

        # Track if an ACK is received (successful handshake)
        if ack == "1":
            ack_received = True

        # Check if the connection is closing
        if fin == "1" or reset == "1":
            connection_closed = True
            end_time = time  # Ensure we capture the earliest closing event

    # Assign duration
    if syn_time is not None:
        if connection_closed and end_time is not None:
            durations.append(end_time - syn_time)  # Successfully closed connection
        elif not ack_received:
            durations.append(100)  # Dropped connection (no ACK received)
        else:
            durations.append(100)  # Connection was never closed properly

        start_times.append(syn_time)  # Record the connection start time

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
