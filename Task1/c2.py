from mininet.topo import Topo
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
import time

class Topology(Topo):
    def build(self, loss=0):  
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

        # Connect hosts to switches
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s2)
        self.addLink(h4, s3)
        self.addLink(h5, s3)
        self.addLink(h6, s4)
        self.addLink(h7, s4)  # H7 acts as the server

        # Configure switch-to-switch links with bandwidth and optional packet loss
        self.addLink(s1, s2, bw=100)  # High-bandwidth link
        self.addLink(s2, s3, bw=50, loss=loss)  # Limited bandwidth with possible packet loss
        self.addLink(s3, s4, bw=100)  # High-bandwidth link

def run_test(test_name, clients, cc=['reno', 'bic', 'highspeed']):
    """
    Run an iperf3 experiment with different congestion control algorithms.
    :param test_name: Name of the test case.
    :param clients: List of client hosts initiating traffic.
    :param cc: List of congestion control algorithms to test.
    """
    net = Mininet(topo=Topology())
    net.start()

    server = net.get('h7')  # Get the TCP server
    
    for scheme in cc:
        print(f"Running {test_name} with {scheme} congestion control...")
        
        # Start the iperf3 server in the background
        server.cmd('iperf3 -s &')
        time.sleep(2)

        # Start packet capture on the server
        pcap_file = f"$(pwd)/outputs/{test_name}_{scheme}.pcap"
        tcpdump_pid = server.cmd(f'tcpdump -i h7-eth0 -w {pcap_file} & echo $!').strip()
        time.sleep(2)

        # Start client traffic
        for client_name in clients:
            client = net.get(client_name)
            client.cmd(f'iperf3 -c {server.IP()} -p 5201 -b 10M -P 10 -t 150 -C {scheme} &')

        time.sleep(155)  # Allow test to run

        # Stop packet capture and iperf3 server
        server.cmd(f'kill {tcpdump_pid}')
        server.cmd('pkill iperf3')  
        print(f"PCAP file saved: outputs/{test_name}_{scheme}.pcap")
    
    net.stop()

if __name__ == '__main__':
    # Define test cases with client configurations
    test_cases = {
        "c_2a": ["h1", "h2"],
        "c_2b": ["h1", "h3"],
        "c_2c": ["h1", "h3", "h4"]
    }
    
    # Run each test case sequentially
    for test_name, clients in test_cases.items():
        run_test(test_name, clients)
        time.sleep(5)  # Small delay between test cases
