#!/bin/bash
# process_pcap.sh

# Extract TCP connection details using tshark
echo "Extracting TCP connection details..."
tshark -r capture.pcap -T fields -e frame.time_relative -e ip.src -e ip.dst -e tcp.srcport -e tcp.dstport -e tcp.flags.syn -e tcp.flags.ack -e tcp.flags.fin -e tcp.flags.reset -Y "tcp" > connections.txt

# Process the connections file and generate the plot
echo "Processing connections and generating plot..."
python3 process_connections.py

echo "Plot saved as connection_duration_plot.png."
