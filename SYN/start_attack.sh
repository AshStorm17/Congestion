#!/bin/bash
# start_attack.sh

# Variables
SERVER_IP="192.168.1.2"  # Replace with server IP
SERVER_PORT=80           # Replace with server port
ATTACK_DURATION=100      # Attack duration in seconds
LEGIT_TRAFFIC_DURATION=140 # Total duration for legitimate traffic

# Start tcpdump to capture packets
echo "Starting packet capture..."
sudo tcpdump -i eth0 -w capture.pcap &
TCPDUMP_PID=$!

# Start legitimate traffic
echo "Starting legitimate traffic..."
while true; do
    curl -s http://$SERVER_IP > /dev/null
    sleep 1
done &
LEGIT_TRAFFIC_PID=$!

# Wait 20 seconds before starting the attack
echo "Waiting 20 seconds before starting the attack..."
sleep 20

# Start SYN flood attack
echo "Starting SYN flood attack..."
python3 syn_flood.py &
SYN_FLOOD_PID=$!

# Let the attack run for the specified duration
echo "Attack running for $ATTACK_DURATION seconds..."
sleep $ATTACK_DURATION

# Stop the SYN flood attack
echo "Stopping SYN flood attack..."
kill $SYN_FLOOD_PID

# Wait 20 seconds before stopping legitimate traffic
echo "Waiting 20 seconds before stopping legitimate traffic..."
sleep 20

# Stop legitimate traffic
echo "Stopping legitimate traffic..."
kill $LEGIT_TRAFFIC_PID

# Stop tcpdump
echo "Stopping packet capture..."
kill $TCPDUMP_PID

echo "Attack and packet capture complete. PCAP file saved as capture.pcap."