from mininet.topo import Topo
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
import time

class Topology(Topo):
    def build(self, loss=0):
        """
        Defines the network topology with switches and hosts.
        The topology includes four switches and seven hosts, 
        where h7 acts as the TCP server.
        """
        # Create switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')

        # Create hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
        h5 = self.addHost('h5')
        h6 = self.addHost('h6')
        h7 = self.addHost('h7')  # TCP Server

        # Connect hosts to respective switches
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s2)
        self.addLink(h4, s3)
        self.addLink(h5, s3)
        self.addLink(h6, s4)
        self.addLink(h7, s4)  # h7 is designated as the server

        # Connect switches with specific bandwidth and packet loss
        self.addLink(s2, s3, bw=50, loss=loss)   # Link between s2 and s3 with configurable loss
        self.addLink(s3, s4, bw=100, loss=loss)  # Link between s3 and s4 with configurable loss


def run_experiment(loss):
    """
    Runs a network experiment using Mininet.
    Starts a TCP server on h7 and a client on h3 to measure performance
    under different congestion control algorithms and packet loss conditions.
    """
    net = Mininet(topo=Topology(loss=loss))  # Initialize network with given loss parameter
    net.start()

    # Get the server and client nodes
    server = net.get('h7')
    client = net.get('h3')  

    # Start iperf3 server in the background
    server.cmd('iperf3 -s &')

    # Define congestion control schemes to test
    cc_algorithms = ["reno", "bic", "highspeed"]

    for scheme in cc_algorithms:
        print(f"Running experiment with {scheme} congestion control and {loss}% packet loss...")

        # Start packet capture on the server interface
        pcap_file = f"$(pwd)/outputs/d_{scheme}_loss{loss}.pcap"
        tcpdump_pid = server.cmd(f'tcpdump -i h7-eth0 -w {pcap_file} & echo $!').strip()
        time.sleep(2)  # Allow tcpdump to initialize

        # Run iperf3 client from h3 to h7 with specified congestion control
        client.cmd(f'iperf3 -c {server.IP()} -p 5201 -b 10M -P 10 -t 150 -C {scheme} &')
        time.sleep(155)  # Wait for the test to complete

        # Stop packet capture
        server.cmd(f'kill {tcpdump_pid}')
        time.sleep(5)  # Ensure cleanup is done

        print(f"PCAP file saved at: outputs/d_{scheme}_loss{loss}.pcap")

    print("Experiment complete.")
    net.stop()  # Stop the Mininet network

if __name__ == '__main__':
    # Run experiments with different packet loss percentages
    for loss in [1, 5]:  
        run_experiment(loss)
