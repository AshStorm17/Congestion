from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
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
    client1 = net.get('h1')
    client2 = net.get('h3')
    client3 = net.get('h4')

    server.cmd('iperf3 -s -D &')

    # Congestion control schemes
    cc = ["reno","bic","highspeed"]

    for scheme in cc:
        print(f"Running experiment with {scheme} congestion control...")

        pcap_file = f"$(pwd)/outputs/b_{scheme}.pcap"  
        server.cmd(f'tcpdump -i h7-eth0 -w {pcap_file} &')
        time.sleep(2)  

        client1.cmd(f'iperf3 -c {server.IP()} -p 5201 -b 10M -P 10 -t 150 -C {scheme} &')
        time.sleep(15)  

        client2.cmd(f'iperf3 -c {server.IP()} -p 5201 -b 10M -P 10 -t 120 -C {scheme} &')
        time.sleep(15) 

        client3.cmd(f'iperf3 -c {server.IP()} -p 5201 -b 10M -P 10 -t 90 -C {scheme} &')

        time.sleep(160)  

        server.cmd('pkill -f tcpdump')
        time.sleep(5)  

        print(f"PCAP file saved at: {scheme}.pcap")

    print("Experiment complete.")
    CLI(net)
    net.stop()

if __name__ == '__main__':
    run_experiment()
