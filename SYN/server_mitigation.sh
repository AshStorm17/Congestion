#!/bin/bash

# Enable SYN cookies to prevent half-open connection exhaustion
echo "Enabling SYN cookies..."
sudo sysctl -w net.ipv4.tcp_syncookies=1

echo "Making SYN cookies persistent..."
echo "net.ipv4.tcp_syncookies = 1" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Limit the rate of incoming SYN packets to prevent flooding
echo "Applying rate limiting for SYN packets..."
sudo iptables -A INPUT -p tcp --syn -m limit --limit 5/s --limit-burst 10 -j ACCEPT

# Drop packets from blacklisted IPs (Replace with known attacker IPs)
BLACKLISTED_IPS=("192.168.1.100" "192.168.1.101")
echo "Blocking known malicious IPs..."
for ip in "${BLACKLISTED_IPS[@]}"; do
    sudo iptables -A INPUT -s "$ip" -j DROP
done

# Save iptables rules
echo "Saving iptables rules..."
sudo iptables-save | sudo tee /etc/iptables.rules

# Start the TCP server
echo "Starting TCP server on port 8080..."
python3 tcp_server.py
