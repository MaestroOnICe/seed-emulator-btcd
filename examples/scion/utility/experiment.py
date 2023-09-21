from typing import List
import python_on_whales
import subprocess
import docker
import subprocess

command_measure = "nohup /shared/measure &"

def measureDataPoints():      
    measuring_node = ["as130h-node_130_100-10.130.0.100", "as101h-node_101_100-10.101.0.200"]
    try:
        whales = python_on_whales.DockerClient(compose_files=["./output/docker-compose.yml"])
        client: docker.DockerClient = docker.from_env()
        ctrs = {ctr.name: client.containers.get(ctr.id) for ctr in whales.compose.ps()}

        for node in measuring_node:
            container = ctrs[node]
            container.exec_run(cmd = command_measure, detach = True)

    except KeyboardInterrupt:
        print("Keyboard interrupt received. Cleaning up...")
        whales.compose.down()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command in container: {e}")
        whales.compose.down()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        whales.compose.down()

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
        attacker_container.exec_run(" [ ! -e /etc/bird/bird.bak ] && cp /etc/bird/bird.conf /etc/bird/bird.bak")
        subprocess.run(f"./hijack.sh {victim_asn}", stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
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