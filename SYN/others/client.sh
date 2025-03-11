#!/bin/bash
SERVER_IP="127.0.0.1"
PCAP_FILE="attack_capture.pcap"
echo "Starting packet capture on the client..."
sudo tcpdump -i eth0 -w "$PCAP_FILE" &
TCPDUMP_PID=$!
sleep 2
echo "Starting legitimate traffic..."
while true; do nc "$SERVER_IP" 8080; sleep 1; done &
LEGIT_PID=$!
sleep 20
echo "Waiting for attack to start..."
sleep 100
echo "Stopping legitimate traffic..."
sudo pkill -f nc
sleep 20
echo "Stopping packet capture..."
sudo kill $TCPDUMP_PID
echo "Packet capture saved to $PCAP_FILE"
echo "Running Python analysis script..."
python3 analyze_pcap.py "$PCAP_FILE"
echo "Opening Wireshark..."
wireshark "$PCAP_FILE" &