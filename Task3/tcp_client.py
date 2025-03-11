import socket
import time

def tcp_client(server_ip, port, nagle_enabled, delayed_ack_enabled):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Configure Nagle’s Algorithm
    if not nagle_enabled:
        client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    client_socket.connect((server_ip, port))

    with open("file.txt", "rb") as f:
        file_data = f.read()

    total_bytes_sent = 0
    packet_count = 0
    start_time = time.time()

    for i in range(0, len(file_data), 40):
        chunk = file_data[i:i+40]
        client_socket.send(chunk)
        total_bytes_sent += len(chunk)
        packet_count += 1  # Count sent packets

        if not delayed_ack_enabled:
            client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_QUICKACK, 1)

        time.sleep(1)  # Simulating 40 bytes per second transfer

    end_time = time.time()
    client_socket.close()

    # Compute metrics
    duration = end_time - start_time
    throughput = total_bytes_sent / duration if duration > 0 else 0
    goodput = total_bytes_sent / duration if duration > 0 else 0

    print("\n Performance Analysis ")
    print(f"Total Data Sent: {total_bytes_sent} bytes")
    print(f"Total Time: {duration:.2f} seconds")
    print(f"Throughput: {throughput:.2f} bytes/sec")
    print(f"Goodput: {goodput:.2f} bytes/sec")
    print(f"Total Packets Sent: {packet_count}")
    print(f"Max Packet Size: 40 bytes (Fixed in this test)")
    print("File sent successfully.")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="TCP Client")
    parser.add_argument("server_ip", type=str, help="Server IP address")
    parser.add_argument("--port", type=int, default=12345, help="Server port")
    parser.add_argument("--nagle", action="store_true", help="Enable Nagle's Algorithm")
    parser.add_argument("--delayed_ack", action="store_true", help="Enable Delayed ACK")
    
    args = parser.parse_args()
    
    tcp_client(args.server_ip, args.port, args.nagle, args.delayed_ack)
