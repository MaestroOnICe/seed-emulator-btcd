from typing import List
import python_on_whales
import subprocess
import docker

command_measure = "nohup /shared/measure &"
command_hijack = '''/bin/cat <<EOM >>/etc/bird/bird.conf
protocol static hijacks {
    ipv4 {
        table t_bgp;
    };
    route 10.102.0.0/25 blackhole   { bgp_large_community.add(LOCAL_COMM); };
    route 10.102.0.128/25 blackhole { bgp_large_community.add(LOCAL_COMM); };
}
EOM'''


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
        try:
            whales = python_on_whales.DockerClient(compose_files=["./output/docker-compose.yml"])
            client: docker.DockerClient = docker.from_env()
            ctrs = {ctr.name: client.containers.get(ctr.id) for ctr in whales.compose.ps()}

            attacker_node = f'as{attacker_asn}h-cs1-10.{attacker_asn}.0.71'
            attacker_container = ctrs[attacker_node]
            attacker_container.exec_run("cp /etc/bird/bird.conf /etc/bird/bird.bak")
            attacker_container.exec_run(command_hijack)
            attacker_container.exec_run("birdc configure")
            # subprocess.run(["docker", "exec", attacker_container, "cp /etc/bird/bird.conf /etc/bird/bird.bak" ], check=True)
            # subprocess.run(["docker", "exec", attacker_container, command_hijack ], check=True)
            # subprocess.run(["docker", "exec", attacker_container, "birdc configure"], check=True)

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
            attacker_node = f'as{attacker_asn}h-cs1-10.{attacker_asn}.0.71'
            attacker_container = ctrs[attacker_node]
            
            attacker_container.exec_run("mv /etc/bird/bird.bak /etc/bird/bird.conf")
            attacker_container.exec_run("birdc configure")
            # subprocess.run(["docker", "exec", attacker_container, "mv /etc/bird/bird.bak /etc/bird/bird.conf"], check=True)
            # subprocess.run(["docker", "exec", attacker_container, "birdc configure"], check=True)

        except KeyboardInterrupt:
            print("Keyboard interrupt received. Cleaning up...")
            whales.compose.down()
        except subprocess.CalledProcessError as e:
            print(f"Error executing command in container: {e}")
            whales.compose.down()
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            whales.compose.down()