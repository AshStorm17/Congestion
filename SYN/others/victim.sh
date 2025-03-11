#!/bin/bash
echo "Setting up the victim machine..."

# Modify kernel parameters to make the system vulnerable
sudo sysctl -w net.ipv4.tcp_syncookies=0
sudo sysctl -w net.ipv4.tcp_max_syn_backlog=65535
sudo sysctl -w net.ipv4.tcp_synack_retries=1

# Keep the server running and listening indefinitely
echo "Server is listening on port 8080..."
while true; do nc -l -p 8080; done
