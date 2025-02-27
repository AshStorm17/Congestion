import subprocess
import pandas as pd
import os
from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel, info
import time
import argparse

def start_iperf_server(host):
    """Start the iperf3 TCP server on the given host."""
    info(f'*** Starting iperf3 server on {host.name}\n')
    host.cmd('iperf3 -s -D &')  # -D runs the server in the background

def start_iperf_client(client, server_ip, duration=150, congestion_control='cubic', start_delay=0):
    """Start iperf3 clients that connect to the server."""
    time.sleep(start_delay)
    info(f'*** Starting iperf3 client on {client.name} after {start_delay}s\n')
    client.cmd(f'iperf3 -c {server_ip} -p 5201 -b 10M -t {duration} -C {congestion_control} &')

def start_tshark(interface='s1-eth1', capture_file='capture.pcap'):
    """Starts tshark to capture packets."""
    print(f"Starting Wireshark capture on {interface}...")
    command = f"tshark -i {interface} -w {capture_file}"
    process = subprocess.Popen(command, shell=True)
    return process

def analyze_pcap(capture_file='capture.pcap'):
    """Analyze the captured packets for throughput, goodput, packet loss, and max window size."""
    print("Analyzing packet capture...")
    
    throughput_cmd = f"tshark -r {capture_file} -q -z io,stat,1"
    throughput_output = subprocess.check_output(throughput_cmd, shell=True).decode()
    print("Throughput Over Time:")
    print(throughput_output)
    
    goodput_cmd = f"tshark -r {capture_file} -Y \"tcp.analysis.ack_rtt\" -T fields -e frame.time_epoch -e tcp.len"
    goodput_output = subprocess.check_output(goodput_cmd, shell=True).decode()
    
    goodput_values = [int(line.split('\t')[1]) for line in goodput_output.split('\n') if '\t' in line]
    goodput = sum(goodput_values) / 1024  # Convert to KB
    print(f"Total Goodput: {goodput:.2f} KB")
    
    loss_cmd = f"tshark -r {capture_file} -Y \"tcp.analysis.lost_segment\" | wc -l"
    lost_packets = int(subprocess.check_output(loss_cmd, shell=True).decode())
    total_packets_cmd = f"tshark -r {capture_file} -Y \"tcp\" | wc -l"
    total_packets = int(subprocess.check_output(total_packets_cmd, shell=True).decode())
    loss_rate = (lost_packets / total_packets) * 100 if total_packets > 0 else 0
    print(f"Packet Loss Rate: {loss_rate:.2f}%")
    
    window_cmd = f"tshark -r {capture_file} -Y \"tcp.window_size_value\" -T fields -e tcp.window_size_value"
    window_output = subprocess.check_output(window_cmd, shell=True).decode()
    window_sizes = [int(x) for x in window_output.split('\n') if x.isdigit()]
    max_window_size = max(window_sizes) if window_sizes else 0
    print(f"Maximum Window Size: {max_window_size} bytes")
    
    return throughput_output, goodput, loss_rate, max_window_size

def create_topology(congestion_control="cubic", option='a', duration=10, loss=0, capture_file='capture.pcap'):
    """Creates the Mininet topology and starts TCP traffic analysis."""
    net = Mininet(controller=RemoteController, link=TCLink)

    # Add a controller
    info('*** Adding controller\n')
    net.addController('c0')

    # Add hosts
    info('*** Adding hosts\n')
    h1 = net.addHost('h1')
    h2 = net.addHost('h2')
    h3 = net.addHost('h3')
    h4 = net.addHost('h4')
    h5 = net.addHost('h5')
    h6 = net.addHost('h6')
    h7 = net.addHost('h7')

    # Add switches
    info('*** Adding switches\n')
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    s3 = net.addSwitch('s3')
    s4 = net.addSwitch('s4')

    # Add links
    info('*** Creating links\n')
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s2)
    net.addLink(h4, s3)
    net.addLink(h5, s3)
    net.addLink(h6, s4)
    net.addLink(h7, s4)        

    if option == "c":
        net.addLink(s1, s2, bw=100)  # 100 Mbps
        net.addLink(s2, s3, bw=50, loss=loss)  # 50 Mbps, loss configurable
        net.addLink(s3, s4, bw=100)  # 100 Mbps

    else :
        net.addLink(s1, s2)
        net.addLink(s2, s3)
        net.addLink(s3, s4)

    # Start the network
    info('*** Starting network\n')
    net.start()

    # Start Wireshark capture
    tshark_process = start_tshark(interface='s1-eth1', capture_file=capture_file)
    time.sleep(2)  # Give tshark time to start

    # Start iperf3 server on h7
    start_iperf_server(h7)

    # Give server time to start
    time.sleep(2)

    if option == "a":
        info("*** Running option a: Single Client h1 to h7\n")
        start_iperf_client(h1, h7.IP(), 150, congestion_control)

    elif option == "b":
        info("*** Running option b: Staggered Clients h1, h3, h4 to h7\n")
        start_iperf_client(h1, h7.IP(), 150, congestion_control, start_delay=0)
        start_iperf_client(h3, h7.IP(), 120, congestion_control, start_delay=15)
        start_iperf_client(h4, h7.IP(), 90, congestion_control, start_delay=30)

    # Stop wireshark and analyse the pcap file 
    time.sleep(duration+5)  # Ensure traffic has been captured before stopping tshark
    tshark_process.terminate()
    print("Capture complete.")
    
    analyze_pcap(capture_file)

    # Stop the network
    info('*** Stopping network\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    parser = argparse.ArgumentParser()
    parser.add_argument('--option', type=str, required=True, help='option')
    args = parser.parse_args()

    # Run topology with default congestion control (change as needed)
    create_topology(congestion_control="cubic",loss=0)
