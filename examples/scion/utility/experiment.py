from typing import List
import python_on_whales
import subprocess
import docker
import subprocess
import os
import shutil

# command_measure = "nohup /shared/measure &"

# def measureDataPoints():      
#     measuring_node = ["as125h-node_125_100-10.125.0.100", "as176h-node_176_100-10.176.0.100","as124h-node_124_100-10.124.0.100", "as139h-node_139_100-10.139.0.100"]
#     try:
#         whales = python_on_whales.DockerClient(compose_files=["./output/docker-compose.yml"])
#         client: docker.DockerClient = docker.from_env()
#         ctrs = {ctr.name: client.containers.get(ctr.id) for ctr in whales.compose.ps()}

#         for node in measuring_node:
#             container = ctrs[node]
#             container.exec_run(cmd = command_measure, detach = True)

#     except KeyboardInterrupt:
#         print("Keyboard interrupt received. Cleaning up...")
#         whales.compose.down()
#     except subprocess.CalledProcessError as e:
#         print(f"Error executing command in container: {e}")
#         whales.compose.down()
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#         whales.compose.down()

def hijackAS(attacker_asn: int, victim_asn: int):
    try:
        whales = python_on_whales.DockerClient(compose_files=["./output/docker-compose.yml"])
        client: docker.DockerClient = docker.from_env()
        ctrs = {ctr.name: client.containers.get(ctr.id) for ctr in whales.compose.ps()}

        attacker_router = f'as{attacker_asn}r-br0-10.{attacker_asn}.0.254'
        victim_router = f'as{victim_asn}r-br0-10.{victim_asn}.0.254'

        attacker_container = ctrs[attacker_router]
        victim_container = ctrs[victim_router]

        # XXX this route needs to be added so that SCION works inside the AS, due to forwarding
        # we do this before the hijack
        victim_container.exec_run(f"ip route add 10.{victim_asn}.0.0/25 dev net0 metric 10")
        victim_container.exec_run(f"ip route add 10.{victim_asn}.0.128/25 dev net0 metric 10")

        # save config, add hijack and execute
        #attacker_container.exec_run("[! -e /etc/bird/bird.bak] && cp /etc/bird/bird.conf /etc/bird/bird.bak")
        attacker_container.exec_run("cp /etc/bird/bird.conf /etc/bird/bird.bak")

        subprocess.run([f"echo $(./hijack.sh {str(victim_asn)} {str(attacker_asn)})"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        attacker_container.exec_run("birdc configure")

    except KeyboardInterrupt:
        print("Keyboard interrupt received. Cleaning up...")
        whales.compose.down()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command in container: {e}")
        whales.compose.down()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        whales.compose.down()

def endHijack(attacker_asn: int):
    try:
        whales = python_on_whales.DockerClient(compose_files=["./output/docker-compose.yml"])
        client: docker.DockerClient = docker.from_env()
        ctrs = {ctr.name: client.containers.get(ctr.id) for ctr in whales.compose.ps()}
        attacker_node = f'as{attacker_asn}r-br0-10.{attacker_asn}.0.254'
        attacker_container = ctrs[attacker_node]
        
        attacker_container.exec_run("mv /etc/bird/bird.bak /etc/bird/bird.conf")
        attacker_container.exec_run("birdc configure")

    except KeyboardInterrupt:
        print("Keyboard interrupt received. Cleaning up...")
        whales.compose.down()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command in container: {e}")
        whales.compose.down()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        whales.compose.down()

def down():
    whales = python_on_whales.DockerClient(compose_files=["./output/docker-compose.yml"])
    whales.compose.down()

def deploy():
    try:
        whales = python_on_whales.DockerClient(compose_files=["./output/docker-compose.yml"])
        whales.compose.build()
        whales.compose.up(detach=True)    

    except KeyboardInterrupt:
        print("Keyboard interrupt received. Cleaning up...")
        whales.compose.down()
    except Exception as e:
        print(e)
        whales.compose.down()

def up():
    try:
        whales = python_on_whales.DockerClient(compose_files=["./output/docker-compose.yml"])
        whales.compose.up(detach=True)    

    except KeyboardInterrupt:
        print("Keyboard interrupt received. Cleaning up...")
        whales.compose.down()
    except Exception as e:
        print(e)
        whales.compose.down()

def build():
    try:
        whales = python_on_whales.DockerClient(compose_files=["./output/docker-compose.yml"])
        whales.compose.build()
        
    except KeyboardInterrupt:
        print("Keyboard interrupt received. Cleaning up...")
        whales.compose.down()
    except Exception as e:
        print(e)
        whales.compose.down()

def moveLogs():
    data_dir = "/home/justus/seed-emulator/examples/scion/data"
    old_logs = "/home/justus/seed-emulator/examples/scion/old_logs"
    # Get a list of all log folders in data_dir
    log_folders = [f for f in os.listdir(data_dir) if f.startswith("logs_") and os.path.isdir(os.path.join(data_dir, f))]

    # Sort the log folders
    log_folders.sort(key=lambda x: int(x.split("_")[1]))


    if not log_folders:
        print("No log folders found in data directory.")
        return
    
    print(log_folders)

    # Get the newest log folder
    newest_log_folder = os.path.join(data_dir, log_folders[-1])
    print("Newest log folder", newest_log_folder)

    # Prepare the destination folder name in old_logs
    destination_folder_name = log_folders[-1]
    destination_path = os.path.join(old_logs, destination_folder_name)

    # Handle the case where the destination folder already exists
    index = 1
    while os.path.exists(destination_path):
        destination_folder_name = f"{log_folders[-1]}_{index}"
        destination_path = os.path.join(old_logs, destination_folder_name)
        index += 1

    # Copy the newest log folder to old_logs_dir
    print(f"copying {newest_log_folder} to {destination_path}")
    shutil.copytree(newest_log_folder, destination_path)

    # Clear the contents of the newest log folder
    node_dirs = os.listdir(newest_log_folder)
    for dir in node_dirs:
        for item in os.listdir(os.path.join(newest_log_folder, dir)):
            item_path = os.path.join(newest_log_folder, dir, item)

            if os.path.isfile(item_path):
                os.remove(item_path)
        