#!/usr/bin/env python3
import docker
import python_on_whales


def ping(type: str, source: str, destination: str):
    if(type == "bgp"):
        cmd = f'ping {destination}'
    
    if(type == "scion"):
        cmd = f'scion ping {destination}'
    else:
        print("Error, not bgp or scion")
     


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

            # Append the values to their respective lists
            print(column1, column2, column3)
        else:
            print(f"Skipping line: {line.strip()}")


# # Build the Docker exec command
# docker_exec_cmd = f'docker exec {container_name_or_id} {command}'

# # Execute the Docker exec command
# try:
#     result = subprocess.run(
#         docker_exec_cmd,
#         shell=True,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#         text=True,
#     )
    
#     if result.returncode == 0:
#         print(f"Command Output:\n{result.stdout}")
#     else:
#         print(f"Command Error:\n{result.stderr}")
# except Exception as e:
#     print(f"An error occurred: {str(e)}")
