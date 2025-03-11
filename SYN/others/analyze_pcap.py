import sys
import pyshark
import matplotlib.pyplot as plt
from collections import defaultdict

def extract_connections(pcap_file):
    cap = pyshark.FileCapture(pcap_file, display_filter="tcp")
    connections = {}
    start_times = {}
    durations = defaultdict(lambda: 100)  # Default duration is 100s if no proper closure

    for pkt in cap:
        try:
            src_ip = pkt.ip.src
            dst_ip = pkt.ip.dst
            src_port = pkt.tcp.srcport
            dst_port = pkt.tcp.dstport
            timestamp = float(pkt.sniff_time.timestamp())

            conn_tuple = (src_ip, dst_ip, src_port, dst_port)

            if pkt.tcp.flags == '0x0002':  # SYN packet
                start_times[conn_tuple] = timestamp
            
            elif pkt.tcp.flags == '0x0012':  # SYN-ACK
                pass  # Ignore for connection duration

            elif pkt.tcp.flags == '0x0010':  # ACK (part of handshake)
                if conn_tuple in start_times:
                    durations[conn_tuple] = timestamp - start_times[conn_tuple]

            elif pkt.tcp.flags == '0x0011' or pkt.tcp.flags == '0x0004':  # FIN-ACK or RST
                if conn_tuple in start_times:
                    durations[conn_tuple] = timestamp - start_times[conn_tuple]

        except AttributeError:
            continue  # Ignore packets without required fields

    cap.close()
    return start_times, durations

def plot_durations(start_times, durations):
    sorted_connections = sorted(start_times.items(), key=lambda x: x[1])
    start_times_list = [x[1] for x in sorted_connections]
    duration_list = [durations[x[0]] for x in sorted_connections]

    plt.figure(figsize=(10, 5))
    plt.scatter(start_times_list, duration_list, label="TCP Connection Durations", alpha=0.7)
    
    # Mark attack start and stop
    plt.axvline(x=start_times_list[0] + 20, color='r', linestyle='--', label="Attack Start")
    plt.axvline(x=start_times_list[0] + 120, color='g', linestyle='--', label="Attack End")

    plt.xlabel("Connection Start Time (s)")
    plt.ylabel("Connection Duration (s)")
    plt.title("TCP Connection Duration Analysis")
    plt.legend()
    plt.grid()
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 analyze_pcap.py <pcap_file>")
        sys.exit(1)

    pcap_file = sys.argv[1]
    start_times, durations = extract_connections(pcap_file)
    plot_durations(start_times, durations)
