from typing import List
import python_on_whales
import subprocess
import docker
import subprocess

command_measure = "nohup /shared/measure &"
# command_hijack1 = """\"echo
# protocol static hijacks {
#     ipv4 {
#         table t_bgp;
#     };
#     route 10.130.0.0/25 blackhole   { bgp_large_community.add(LOCAL_COMM); };
#     route 10.130.0.128/25 blackhole { bgp_large_community.add(LOCAL_COMM); };
# }
# >> /etc/bird/bird.conf\""""
# command_hijack = "echo test >> /etc/bird/bird.conf"


def measureDataPoints():      
    measuring_node = ["as130h-node_130_1-10.130.0.100", "as101h-node_101_1-10.101.0.100"]
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

#victim_as: List[int]
def hijackAS(attacker_asn: int):
        print("hello")
        try:
            whales = python_on_whales.DockerClient(compose_files=["./output/docker-compose.yml"])
            client: docker.DockerClient = docker.from_env()
            ctrs = {ctr.name: client.containers.get(ctr.id) for ctr in whales.compose.ps()}

            attacker_node = f'as{attacker_asn}r-br0-10.{attacker_asn}.0.254'

            attacker_container = ctrs[attacker_node]
            attacker_container.exec_run("cp /etc/bird/bird.conf /etc/bird/bird.bak")            
            subprocess.run("./hijack.sh", stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            #attacker_container.exec_run(command_hijack)
            #subprocess.run(f"docker exec {attacker_node} bash -c {command_hijack}")
            # attacker_container.exec_run(f"echo -e {command_hijack} >> /hijack.txt")
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