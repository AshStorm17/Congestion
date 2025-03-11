from mininet.topo import Topo
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
import time

class Topology(Topo):
    def build(self, loss=0):  
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

        self.addLink(s1, s2, bw=100)  
        self.addLink(s2, s3, bw=50, loss=loss)  
        self.addLink(s3, s4, bw=100) 

def run_test(test_name, clients, cc=["reno","bic", "highspeed"], loss=0):
    net = Mininet(topo=Topology(loss=loss))
    net.start()

    server = net.get('h7')
    
    for scheme in cc:
        print(f"Running {test_name} with {scheme} congestion control and {loss}% loss...")

        # server
        server.cmd('iperf3 -s -D &')
        time.sleep(2)

        # packet capture
        pcap_file = f"$(pwd)/outputs/{test_name}_{scheme}_loss{loss}.pcap"
        tcpdump_pid = server.cmd(f'tcpdump -i h7-eth0 -w {pcap_file} & echo $!').strip()
        time.sleep(2)

        # clients
        for client_name in clients:
            client = net.get(client_name)
            client.cmd(f'iperf3 -c {server.IP()} -p 5201 -b 10M -P 10 -t 150 -C {scheme} &')

        time.sleep(155)

        # stopping packet capture
        server.cmd(f'kill {tcpdump_pid}')
        server.cmd('pkill iperf3')  
        print(f"PCAP file saved: outputs/{test_name}_{scheme}_loss{loss}.pcap")

    net.stop()

if __name__ == '__main__':
    test_cases = {
        "d_2a": ["h1", "h2"],
        "d_2b": ["h1", "h3"],
        "d_2c": ["h1", "h3", "h4"]
    }
    
    loss_values = [1, 5]  
    for loss in loss_values:
        for test_name, clients in test_cases.items():
            run_test(test_name, clients, loss=loss)
            time.sleep(5)  
