from scapy.all import *
import matplotlib.pyplot as plt
import pandas as pd

# Load the pcap file
packets = rdpcap('capture.pcap')

# Initialize lists to store data
timestamps = []
throughput = []
window_sizes = []
lost_packets = 0
total_packets = 0

# Analyze packets
for packet in packets:
    if TCP in packet:
        total_packets += 1
        timestamps.append(packet.time)
        throughput.append(len(packet))
        window_sizes.append(packet[TCP].window)

        # Check for lost packets
        if packet[TCP].flags & 0x08:  # PSH flag
            if packet[TCP].seq != expected_seq:
                lost_packets += 1
            expected_seq = packet[TCP].seq + len(packet[TCP].payload)

# Calculate packet loss rate
packet_loss_rate = (lost_packets / total_packets) * 100

# Calculate throughput over time
time_intervals = [t - timestamps[0] for t in timestamps]
throughput_mbps = [8 * t / 1e6 for t in throughput]  # Convert to Mbps

# Plot Throughput Over Time
plt.figure(figsize=(10, 6))
plt.plot(time_intervals, throughput_mbps, label='Throughput (Mbps)')
plt.xlabel('Time (s)')
plt.ylabel('Throughput (Mbps)')
plt.title('Throughput Over Time')
plt.legend()
plt.grid()
plt.savefig('throughput_over_time.png')
plt.show()

# Plot Window Size Over Time
plt.figure(figsize=(10, 6))
plt.plot(time_intervals, window_sizes, label='Window Size (Bytes)', color='orange')
plt.xlabel('Time (s)')
plt.ylabel('Window Size (Bytes)')
plt.title('TCP Window Size Over Time')
plt.legend()
plt.grid()
plt.savefig('window_size_over_time.png')
plt.show()

# Print Packet Loss Rate
print(f"Packet Loss Rate: {packet_loss_rate:.2f}%")

# Print Maximum Window Size
print(f"Maximum Window Size: {max(window_sizes)} Bytes")