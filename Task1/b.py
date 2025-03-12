from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
import time

class Topology(Topo):
    def build(self):
        """
        Define the network topology:
        - 4 switches (s1-s4)
        - 7 hosts (h1-h7)
        - Connect hosts to switches and establish inter-switch links
        """
        
        # Adding switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')

        # Adding hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
        h5 = self.addHost('h5')
        h6 = self.addHost('h6')
        h7 = self.addHost('h7')  # h7 acts as the TCP server

        # Connecting hosts to respective switches
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s2)
        self.addLink(h4, s3)
        self.addLink(h5, s3)
        self.addLink(h6, s4)
        self.addLink(h7, s4)  # h7 is the server

        # Connecting switches in a linear topology
        self.addLink(s1, s2)
        self.addLink(s2, s3)
        self.addLink(s3, s4)

def run_experiment():
    """
    Run the network experiment:
    - Start the Mininet network
    - Set up h7 as the TCP server
    - Run iperf3 tests with different congestion control algorithms using multiple clients
    - Capture traffic using tcpdump
    - Stop the network when done
    """
    
    # Initialize the Mininet network
    net = Mininet(topo=Topology())
    net.start()

    # Define server (h7) and clients (h1, h3, h4)
    server = net.get('h7')
    client1 = net.get('h1')
    client2 = net.get('h3')
    client3 = net.get('h4')

    # Start iperf3 server on h7
    server.cmd('iperf3 -s &')

    # List of congestion control algorithms to test
    congestion_algorithms = ["reno", "bic", "highspeed"]

    for scheme in congestion_algorithms:
        print(f"Running experiment with {scheme} congestion control...")

        # Define output PCAP file for capturing traffic
        pcap_file = f"$(pwd)/outputs/b_{scheme}.pcap"  
        
        # Start tcpdump to capture packets on h7
        server.cmd(f'tcpdump -i h7-eth0 -w {pcap_file} &')
        time.sleep(2)  # Allow tcpdump to initialize

        # Start iperf3 clients at different times with different durations
        client1.cmd(f'iperf3 -c {server.IP()} -p 5201 -b 10M -P 10 -t 150 -C {scheme} &')
        time.sleep(15)  # Delay before starting next client

        client2.cmd(f'iperf3 -c {server.IP()} -p 5201 -b 10M -P 10 -t 120 -C {scheme} &')
        time.sleep(15)  # Delay before starting next client

        client3.cmd(f'iperf3 -c {server.IP()} -p 5201 -b 10M -P 10 -t 90 -C {scheme} &')

        time.sleep(160)  # Wait for all clients to finish

        # Stop tcpdump process
        server.cmd('pkill -f tcpdump')
        time.sleep(5)  # Ensure cleanup

        print(f"PCAP file saved at: outputs/b_{scheme}.pcap")

    print("Experiment complete.")
    CLI(net)  # Open Mininet CLI for manual interaction if needed
    net.stop()

if __name__ == '__main__':
    run_experiment()
