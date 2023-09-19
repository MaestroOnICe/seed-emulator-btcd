#!/bin/bash

# Get all interfaces
interfaces=$(ls /sys/class/net)

# Apply tc netem commands on all interfaces
for interface in $interfaces
do
    if [ "$interface" == "lo" ]; then
        continue
    fi
    # Reset the qdisc to default before applying the new rules
    tc qdisc del dev $interface root

    # Limit bandwidth and latency
    tc qdisc add dev $interface root netem rate 10mbit delay 5ms
done
