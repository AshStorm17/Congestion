import socket
import time

# Configuration (Modify as needed)
HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 12345      # Port number
DELAYED_ACK = True  # Set to False to disable delayed ACK
BUFFER_SIZE = 1024  # Buffer size for receiving data

# Create TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print("Server listening on port", PORT)
conn, addr = server_socket.accept()
print(f"Connection from {addr}")

start_time = time.time()
total_bytes_received = 0
packet_count = 0

while True:
    data = conn.recv(BUFFER_SIZE)
    if not data:
        break

    total_bytes_received += len(data)
    packet_count += 1

    if DELAYED_ACK:
        time.sleep(0.2)  # Simulate delayed ACK (200ms)
    
    conn.sendall(b"ACK")  # Send ACK back

    elapsed_time = time.time() - start_time
    if elapsed_time >= 120:  # Run for ~2 minutes
        break

print(f"Total data received: {total_bytes_received} bytes")
print(f"Total packets received: {packet_count}")
conn.close()
server_socket.close()
