from scapy.all import *
from multiprocessing import Process
import time

# Set up the target IPs and the interfaces
targets = {
    "net0": "10.180.0.71", 
    "dmtpif": "10.72.0.2",  
}

# Function to send a ping request every 10ms
def send_pings(interface, target_ip):
    while True:
        # Send the ICMP request
        send(IP(dst=target_ip, version=4)/ICMP(), iface=interface, verbose=0)
        
        # Wait 10ms
        time.sleep(0.02)

for interface, (target_ip) in targets.items():
    process = Process(target=send_pings, args=(interface, target_ip))
    process.start()
