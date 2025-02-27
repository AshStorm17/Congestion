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

def start_iperf_client(client, server_ip, duration, congestion_control, start_delay=0):
    """Start iperf3 clients that connect to the server."""
    time.sleep(start_delay)
    info(f'*** Starting iperf3 client on {client.name} after {start_delay}s\n')
    client.cmd(f'iperf3 -c {server_ip} -p 5201 -b 10M -t {duration} -C {congestion_control} &')

def create_topology(congestion_control="cubic", option='a', loss=0):
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
    net.addLink(s1, s2)
    net.addLink(s2, s3)
    net.addLink(s3, s4)

    # net.addLink(s1, s2, bw=100)  # 100 Mbps
    # net.addLink(s2, s3, bw=50, loss=loss)  # 50 Mbps, loss configurable
    # net.addLink(s3, s4, bw=100)  # 100 Mbps
    
    # Start the network
    info('*** Starting network\n')
    net.start()

    # Start iperf3 server on h7
    start_iperf_server(h7)

    # Give server time to start
    time.sleep(2)

    if option == "a":
        info("*** Running option a: Single Client h1 to h7\n")
        start_iperf_client(h1, h7.IP(), 30, congestion_control)

    elif option == "b":
        info("*** Running option b: Staggered Clients h1, h3, h4 to h7\n")
        start_iperf_client(h1, h7.IP(), 150, congestion_control, start_delay=0)
        start_iperf_client(h3, h7.IP(), 120, congestion_control, start_delay=15)
        start_iperf_client(h4, h7.IP(), 90, congestion_control, start_delay=30)

    # Start iperf3 clients (h1 to h6) connecting to h7
    start_iperf_client(h1, h7.IP(), 10, congestion_control)
    start_iperf_client(h2, h7.IP(), 10, congestion_control)
    start_iperf_client(h3, h7.IP(), 10, congestion_control)
    start_iperf_client(h4, h7.IP(), 10, congestion_control)
    start_iperf_client(h5, h7.IP(), 10, congestion_control)
    start_iperf_client(h6, h7.IP(), 10, congestion_control)

    # Run CLI for testing
    info('*** Running CLI\n')
    CLI(net)

    # Stop the network
    info('*** Stopping network\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    parser = argparse.ArgumentParser()
    parser.add_argument('--option', type=str, required=True, help='option')

    # Run topology with default congestion control (change as needed)
    create_topology(congestion_control="cubic",loss=0)
