#!/bin/bash
# server_setup.sh

# Set kernel parameters for SYN flood vulnerability
echo "Configuring server for SYN flood attack..."
sudo sysctl -w net.ipv4.tcp_max_syn_backlog=1000
sudo sysctl -w net.ipv4.tcp_syncookies=0
sudo sysctl -w net.ipv4.tcp_synack_retries=1

# Make changes persistent by appending to /etc/sysctl.conf if they are not already present
echo "Making changes persistent..."
grep -q "^net.ipv4.tcp_max_syn_backlog=" /etc/sysctl.conf || echo "net.ipv4.tcp_max_syn_backlog=1000" | sudo tee -a /etc/sysctl.conf
grep -q "^net.ipv4.tcp_syncookies=" /etc/sysctl.conf || echo "net.ipv4.tcp_syncookies=0" | sudo tee -a /etc/sysctl.conf
grep -q "^net.ipv4.tcp_synack_retries=" /etc/sysctl.conf || echo "net.ipv4.tcp_synack_retries=1" | sudo tee -a /etc/sysctl.conf

# Start the TCP server using the separate Python script
echo "Starting TCP server on port 8080..."
python3 tcp_server.py
