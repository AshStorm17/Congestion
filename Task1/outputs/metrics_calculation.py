import os
import subprocess
import csv

def extract_metrics(pcap_file):
    """
    Extracts network performance metrics from a given pcap file.
    Metrics include:
    - Goodput (excluding retransmissions)
    - Packet loss rate
    - Maximum TCP window size
    """
    
    # Calculate goodput by summing the sizes of TCP data packets (excluding retransmissions)
    cmd_goodput = f"tshark -r {pcap_file} -Y 'tcp.len > 0 && !tcp.analysis.retransmission && !tcp.analysis.duplicate_ack' -T fields -e frame.len"
    result_goodput = subprocess.run(cmd_goodput, shell=True, capture_output=True, text=True)
    
    goodput_bytes = sum(int(pkt_len) for pkt_len in result_goodput.stdout.splitlines() if pkt_len.isdigit())

    # Count total TCP packets in the capture
    cmd_total_tcp = f"tshark -r {pcap_file} -Y 'tcp' -T fields -e frame.number | wc -l"
    total_tcp_packets = int(subprocess.run(cmd_total_tcp, shell=True, capture_output=True, text=True).stdout.strip() or 0)

    # Identify lost packets (considering retransmissions and duplicate ACKs)
    cmd_lost = f"tshark -r {pcap_file} -Y 'tcp.analysis.retransmission || tcp.analysis.duplicate_ack' | wc -l"
    lost_packets = int(subprocess.run(cmd_lost, shell=True, capture_output=True, text=True).stdout.strip() or 0)

    # Compute packet loss percentage
    packet_loss_rate = (lost_packets / total_tcp_packets) * 100 if total_tcp_packets > 0 else 0

    # Determine the maximum TCP window size observed
    cmd_window = f"tshark -r {pcap_file} -Y 'tcp' -T fields -e tcp.window_size_value"
    result_window = subprocess.run(cmd_window, shell=True, capture_output=True, text=True)
    
    max_window_size = max([int(size) for size in result_window.stdout.splitlines() if size.isdigit()], default=0)

    # Convert goodput from bytes to Mbps
    return goodput_bytes / 1e6, packet_loss_rate, max_window_size  

def process_and_store_metrics(directory, csv_file):
    """
    Processes all .pcap files in the specified directory and extracts key metrics.
    The results are stored in a CSV file for analysis.
    """
    
    os.makedirs("results", exist_ok=True)  # Ensure output directory exists
    
    # Open CSV file to store extracted metrics
    with open(csv_file, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Experiment", "Algorithm", "Goodput (Mbps)", "Packet Loss Rate (%)", "Max Window Size (Bytes)"])

        for file in os.listdir(directory):
            if file.endswith(".pcap"):
                file_path = os.path.join(directory, file)
                
                # Extract experiment name and congestion control algorithm from filename
                parts = file.replace('.pcap', '').rsplit('_', 1)
                exp_name = parts[0] if len(parts) > 1 else parts[0]  # Extract experiment name
                algorithm = parts[1] if len(parts) > 1 else "Unknown"  # Extract congestion algorithm

                # Get performance metrics from the pcap file
                goodput_mbps, packet_loss_rate, max_window_size = extract_metrics(file_path)
                
                # Write extracted metrics to CSV
                writer.writerow([exp_name, algorithm, f"{goodput_mbps:.2f}", f"{packet_loss_rate:.2f}", max_window_size])

# Define paths
pcap_directory = "/mnt/d/SEM6/CN/final/Congestion/Task1/outputs"  # Directory containing pcap files
csv_filename = "results/congestion_metrics.csv"  # Output CSV file to store results

# Process the pcap files and store extracted metrics in the CSV
process_and_store_metrics(pcap_directory, csv_filename)
