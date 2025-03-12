from mininet.topo import Topo
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
import time

class CustomTopology(Topo):
    """
    Defines a custom network topology with 4 switches and 7 hosts.
    The topology includes a configurable packet loss parameter.
    """
    def build(self, loss=0):  
        # Creating switch nodes
        s1, s2, s3, s4 = [self.addSwitch(f's{i}') for i in range(1, 5)]
        
        # Creating host nodes
        hosts = {f'h{i}': self.addHost(f'h{i}') for i in range(1, 8)}

        # Connecting hosts to respective switches
        self.addLink(hosts['h1'], s1)
        self.addLink(hosts['h2'], s1)
        self.addLink(hosts['h3'], s2)
        self.addLink(hosts['h4'], s3)
        self.addLink(hosts['h5'], s3)
        self.addLink(hosts['h6'], s4)
        self.addLink(hosts['h7'], s4)  # h7 acts as the TCP Server

        # Connecting switches with configured bandwidth and packet loss
        self.addLink(s1, s2, bw=100)  # High-speed link
        self.addLink(s2, s3, bw=50, loss=loss)  # Simulating loss
        self.addLink(s3, s4, bw=100)  # Another high-speed link

def run_test(test_name, clients, cc_algorithms=["reno", "bic", "highspeed"], loss=0):
    """
    Sets up the network and runs iperf3 tests with different congestion control algorithms.
    Captures network traffic and saves PCAP files.
    """
    net = Mininet(topo=CustomTopology(loss=loss))
    net.start()

    server = net.get('h7')  # TCP Server node
    
    for cc in cc_algorithms:
        print(f"Running test {test_name} with {cc} congestion control and {loss}% loss...")

        # Start iperf3 server in the background
        server.cmd('iperf3 -s &')
        time.sleep(2)

        # Start packet capture on the server interface
        pcap_file = f"$(pwd)/outputs/{test_name}_{cc}_loss{loss}.pcap"
        tcpdump_pid = server.cmd(f'tcpdump -i h7-eth0 -w {pcap_file} & echo $!').strip()
        time.sleep(2)

        # Start iperf3 clients for traffic generation
        for client_name in clients:
            client = net.get(client_name)
            client.cmd(f'iperf3 -c {server.IP()} -p 5201 -b 10M -P 10 -t 150 -C {cc} &')

        time.sleep(155)  # Wait for tests to complete

        # Stop packet capture and iperf3 processes
        server.cmd(f'kill {tcpdump_pid}')
        server.cmd('pkill iperf3')  
        print(f"PCAP file saved: outputs/{test_name}_{cc}_loss{loss}.pcap")

    net.stop()

if __name__ == '__main__':
    # Define test cases with client sets
    test_cases = {
        "d_2a": ["h1", "h2"],
        "d_2b": ["h1", "h3"],
        "d_2c": ["h1", "h3", "h4"]
    }
    
    # Define packet loss scenarios to test
    loss_values = [1, 5]  
    for loss in loss_values:
        for test_name, clients in test_cases.items():
            run_test(test_name, clients, loss=loss)
            time.sleep(5)  # Pause between tests to ensure stability