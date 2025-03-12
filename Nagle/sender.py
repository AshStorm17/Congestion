import socket
import time

# Configuration
SERVER_IP = "127.0.0.1"  # Change if server is remote
PORT = 12345
NAGLE_ALGORITHM = True  # Set to False to disable Nagle’s Algorithm
TRANSFER_RATE = 40  # Bytes per second
FILE_SIZE = 4096  # 4 KB file
CHUNK_SIZE = 40  # Sending 40 bytes at a time

# Create TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if not NAGLE_ALGORITHM:
    client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # Disable Nagle

client_socket.connect((SERVER_IP, PORT))

print("Connected to server, starting data transfer...")

start_time = time.time()
bytes_sent = 0
packet_count = 0

while bytes_sent < FILE_SIZE:
    chunk = b"x" * CHUNK_SIZE  # Sending dummy 40-byte data
    client_socket.sendall(chunk)
    bytes_sent += CHUNK_SIZE
    packet_count += 1

    response = client_socket.recv(1024)  # Wait for ACK
    print(f"Sent {bytes_sent} bytes, Received: {response.decode()}")

    time.sleep(1)  # Maintain transfer rate of 40 bytes/sec

print("File transfer complete")
client_socket.close()
