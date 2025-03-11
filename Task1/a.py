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

    server.cmd('iperf3 -s &')

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
    """
    print(f"\nAnalyzing results for {scheme}...")

    # Throughput calculation (Bytes per second)
    os.system(f"sudo tshark -r {pcap_file} -q -z io,stat,1 > outputs/throughput_{scheme}.txt")
    
    # Goodput (Extract only the payload bytes)
    os.system(f"sudo tshark -r {pcap_file} -Y 'tcp.payload' | wc -l > outputs/goodput_{scheme}.txt")

    # Packet loss rate (SYN packets that did not receive SYN-ACK)
    os.system(f"sudo tshark -r {pcap_file} -Y 'tcp.analysis.lost_segment' | wc -l > outputs/loss_{scheme}.txt")

    # Maximum Window Size achieved
    os.system(f"sudo tshark -r {pcap_file} -Y 'tcp.window_size_value' -T fields -e tcp.window_size_value | sort -nr | head -1 > outputs/window_{scheme}.txt")

    print(f"Analysis complete for {scheme}. Check outputs directory for results.")

if __name__ == '__main__':
    run_experiment()
