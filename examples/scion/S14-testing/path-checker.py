#!/usr/bin/env python3
import docker
import python_on_whales
import time

def ping(type: str, source: str, destination: str):
    if(type == "bgp"):
        cmd = f'ping {destination}'
    
    if(type == "scion"):
        cmd = f'scion ping {destination}'
    else:
        print("Error, not bgp or scion")
    
    for name, ctr in ctrs.items():
        if "cs" not in name:
            continue
        print("Run path check in", name, end="")
        ec, output = ctr.exec_run(cmd)
        for line in output.decode('utf8').splitlines():
            print("  " + line)

# Build Docker containers and run the network
whales = python_on_whales.DockerClient(compose_files=["./output/docker-compose.yml"])
whales.compose.build()
whales.compose.up(detach=True)    
     
# Use Docker SDK to interact with the containers
client: docker.DockerClient = docker.from_env()
ctrs = {ctr.name: client.containers.get(ctr.id) for ctr in whales.compose.ps()}

#sleep for 15 seconds to up paths
time.sleep(15)

txt_file = 'paths.txt'
with open(txt_file, mode='r') as file:
    # Loop through each line in the file
    for line in file:
        # Split the line into three parts based on the "|" character
        parts = line.strip().split('|')
        
        # Check if the line contains exactly three parts
        if len(parts) == 3:
            # Assign each part to separate variables
            column1, column2, column3 = parts
            ping(column1, column2, column3)
        else:
            print(f"Skipping line: {line.strip()}")