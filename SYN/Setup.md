On the server machine, modify the following Linux kernel parameters to optimize the SYN flood attack:
```
# Increase the maximum number of pending SYN requests
sudo sysctl -w net.ipv4.tcp_max_syn_backlog=1000

# Disable SYN cookies
sudo sysctl -w net.ipv4.tcp_syncookies=0

# Reduce the number of SYN-ACK retries
sudo sysctl -w net.ipv4.tcp_synack_retries=1
```

On the client machine, start capturing packets using tcpdump:
```
sudo tcpdump -i <interface> -w syn_flood.pcap
```
