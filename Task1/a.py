from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
import os
import time

class Topology(Topo):
    def build(self):
        # switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')

        # hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
        h5 = self.addHost('h5')
        h6 = self.addHost('h6')
        h7 = self.addHost('h7')  # TCP Server

        # connecting hosts to switches
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s2)
        self.addLink(h4, s3)
        self.addLink(h5, s3)
        self.addLink(h6, s4)
        self.addLink(h7, s4)  # H7 is the server

        # connecting switches
        self.addLink(s1, s2)
        self.addLink(s2, s3)
        self.addLink(s3, s4)

def run_experiment():
    net = Mininet(topo=Topology())
    net.start()

    server = net.get('h7')
    client = net.get('h1')

    server.cmd('iperf3 -s -D &')

    # Congestion control schemes
    cc = ["reno","bic","highspeed"]

    for scheme in cc:
        print(f"Running experiment with {scheme} congestion control...")

        pcap_file = f"$(pwd)/outputs/a_{scheme}.pcap"
        tcpdump_pid = server.cmd(f'tcpdump -i h7-eth0 -w {pcap_file} & echo $!').strip()
        time.sleep(2)

        iperf_output = f"outputs/iperf_{scheme}.txt"
        client.cmd(f'iperf3 -c {server.IP()} -p 5201 -b 10M -P 10 -t 150 -C {scheme} > {iperf_output} &')
        time.sleep(155)

        server.cmd(f'kill {tcpdump_pid}')
        time.sleep(5)

        print(f"PCAP file saved at: {scheme}.pcap")
        analyze_metrics(pcap_file, iperf_output, scheme)

    print("Experiment complete.")
    net.stop()

def analyze_metrics(pcap_file, iperf_output, scheme):
    """
    Extracts and analyzes throughput, goodput, packet loss, and window size from the PCAP and iperf logs.
    Also generates Wireshark I/O graphs and prints the final outputs to the command line.
    """
    print(f"\nAnalyzing results for {scheme}...")

    # Throughput calculation (Bytes per second)
    throughput_file = f"outputs/throughput_{scheme}.txt"
    os.system(f"sudo tshark -r {pcap_file} -q -z io,stat,1 > {throughput_file}")
    
    # Goodput (Extract only the payload bytes)
    goodput_file = f"outputs/goodput_{scheme}.txt"
    os.system(f"sudo tshark -r {pcap_file} -Y 'tcp.payload' | wc -l > {goodput_file}")

    # Packet loss rate (SYN packets that did not receive SYN-ACK)
    loss_file = f"outputs/loss_{scheme}.txt"
    os.system(f"sudo tshark -r {pcap_file} -Y 'tcp.analysis.lost_segment' | wc -l > {loss_file}")

    # Maximum Window Size achieved
    window_file = f"outputs/window_{scheme}.txt"
    os.system(f"sudo tshark -r {pcap_file} -Y 'tcp.window_size_value' -T fields -e tcp.window_size_value | sort -nr | head -1 > {window_file}")

    # Generate Wireshark I/O graphs
    io_graph_file = f"outputs/io_graph_{scheme}.png"
    os.system(f"sudo tshark -r {pcap_file} -q -z io,stat,1 -X lua_script:wireshark_io_graph.lua -w {io_graph_file}")

    # Print the final outputs to the command line
    with open(throughput_file, 'r') as f:
        throughput = f.read()
    with open(goodput_file, 'r') as f:
        goodput = f.read()
    with open(loss_file, 'r') as f:
        loss = f.read()
    with open(window_file, 'r') as f:
        window = f.read()

    print(f"\nResults for {scheme}:")
    print(f"Throughput: {throughput}")
    print(f"Goodput: {goodput}")
    print(f"Packet Loss: {loss}")
    print(f"Maximum Window Size: {window}")

    print(f"Wireshark I/O graph saved at: {io_graph_file}")
    print(f"Analysis complete for {scheme}. Check outputs directory for results.")

if __name__ == '__main__':
    run_experiment()
