#!/usr/bin/env python3
import socket

def main():
    SERVER_HOST = '127.0.1.7'
    SERVER_PORT = 8080

    # Step 1: Create socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5)  # Allows up to 5 pending connections in queue
    print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}...")

    try:
        while True:
            # Step 2: Accept connection (Blocking call)
            client_socket, addr = server_socket.accept()
            print(f"Connection from {addr}")

            try:
                # Step 3: Send data after TCP handshake
                client_socket.send(b"Hello from server!")

                # Step 4: Receive data (optional)
                data = client_socket.recv(1024)
                if data:
                    print(f"Received from {addr}: {data.decode()}")

            except Exception as e:
                print(f"Error handling client {addr}: {e}")
            finally:
                client_socket.shutdown(socket.SHUT_RDWR)  # Graceful shutdown
                client_socket.close()
                print(f"Connection with {addr} closed.")

    except KeyboardInterrupt:
        print("\nServer shutting down...")
    finally:
        server_socket.close()

if __name__ == '__main__':
    main()
