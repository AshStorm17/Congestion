#!/bin/bash
# server_setup.sh

# Set kernel parameters for SYN flood vulnerability
echo "Configuring server for SYN flood attack..."
sudo sysctl -w net.ipv4.tcp_max_syn_backlog=1000
sudo sysctl -w net.ipv4.tcp_syncookies=0
sudo sysctl -w net.ipv4.tcp_synack_retries=1

# Make changes persistent
echo "Making changes persistent..."
echo "net.ipv4.tcp_max_syn_backlog=1000" | sudo tee -a /etc/sysctl.conf
echo "net.ipv4.tcp_syncookies=0" | sudo tee -a /etc/sysctl.conf
echo "net.ipv4.tcp_synack_retries=1" | sudo tee -a /etc/sysctl.conf

echo "Server setup complete. Ready for SYN flood attack."