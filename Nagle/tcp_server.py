import socket
import time

def tcp_server(port, nagle_enabled, delayed_ack_enabled):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Configure Nagle’s Algorithm
    if not nagle_enabled:
        server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    server_socket.bind(('127.0.1.15', port))
    server_socket.listen(1)

    print(f"Server listening on port {port}...")
    conn, addr = server_socket.accept()
    print(f"Connection from {addr}")

    received_data = b""
    packet_count = 0
    start_time = time.time()

    while True:
        data = conn.recv(1024)  # Allow some variability in chunk size
        if not data:
            break
        received_data += data
        packet_count += 1  # Count received packets

        # Configure Delayed ACK
        if not delayed_ack_enabled:
            conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_QUICKACK, 1)

    end_time = time.time()
    total_bytes_received = len(received_data)
    duration = end_time - start_time

    with open("received_file.txt", "wb") as f:
        f.write(received_data)

    conn.close()
    server_socket.close()
    
    # Compute metrics
    throughput = total_bytes_received / duration if duration > 0 else 0
    goodput = total_bytes_received / duration if duration > 0 else 0
    expected_packets = 4096 // 40 + 1  # Expected packets based on 4KB file
    packet_loss = ((expected_packets - packet_count) / expected_packets) * 100

    print("\n Performance Analysis ")
    print(f"Total Data Received: {total_bytes_received} bytes")
    print(f"Total Time: {duration:.2f} seconds")
    print(f"Throughput: {throughput:.2f} bytes/sec")
    print(f"Goodput: {goodput:.2f} bytes/sec")
    print(f"Packet Loss Rate: {packet_loss:.2f}%")
    print(f"Max Packet Size: Variable (Observed via tcpdump)")
    print("File received successfully.")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="TCP Server")
    parser.add_argument("--port", type=int, default=12345, help="Server port")
    parser.add_argument("--nagle", action="store_true", help="Enable Nagle's Algorithm")
    parser.add_argument("--delayed_ack", action="store_true", help="Enable Delayed ACK")
    
    args = parser.parse_args()
    
    tcp_server(args.port, args.nagle, args.delayed_ack)
