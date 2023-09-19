import subprocess
import multiprocessing
from time import monotonic
import time

def ping_host(cmd):
    results = []

    for i in range(18):
        host = cmd[1]
        command = cmd[0]
        start_time = monotonic()
        process = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        end_time = monotonic()

        result = f"{start_time} {host} {'success' if process.returncode == 0 else 'failure'} {end_time-start_time}"
        results.append(result)
        # time.sleep(0.02)

    with open('ping_logs.txt', 'a') as f:
        for result in results:
            f.write(result + '\n')


def execute_command_after_delay(delay, command):
    time.sleep(delay)
    start_time = monotonic()
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    end_time = monotonic()

    result = f"{start_time} {'hijack'} {'success' if process.returncode == 0 else 'failure'} {end_time-start_time}"
    with open('ping_logs.txt', 'a') as f:
        f.write(result + '\n')


if __name__ == '__main__':
    hosts = ["8.8.8.8", "8.8.4.4", "208.67.222.222", "208.67.220.220"]
    cmds = [
        ('docker exec -it as170h-cs1-10.170.0.71 /bin/bash -c "ping 10.200.0.71 -c 1 -W 0.1"' , 'as170-BGP'),
        ('docker exec -it as162h-cs1-10.162.0.71 /bin/bash -c "ping 10.200.0.71 -c 1 -W 0.1"' , 'as162-BGP'),
        ('docker exec -it as150h-cs1-10.150.0.71 /bin/bash -c "ping 10.200.0.71 -c 1 -W 0.1"' , 'as150-BGP'),
        ('docker exec -it as180h-cs1-10.180.0.71 /bin/bash -c "ping 10.200.0.71 -c 1 -W 0.1"' , 'as180-BGP'),
        ('docker exec -it as170h-cs1-10.170.0.71 /bin/bash -c "scion ping 1-200,10.200.0.71 -c 1 --timeout 100ms"' , 'as170-SCION'),
        ('docker exec -it as162h-cs1-10.162.0.71 /bin/bash -c "scion ping 1-200,10.200.0.71 -c 1 --timeout 100ms"' , 'as162-SCION'),
        ('docker exec -it as150h-cs1-10.150.0.71 /bin/bash -c "scion ping 1-200,10.200.0.71 -c 1 --timeout 100ms"' , 'as150-SCION'),
        ('docker exec -it as180h-cs1-10.180.0.71 /bin/bash -c "scion ping 1-200,10.200.0.71 -c 1 --timeout 100ms"' , 'as180-SCION'),
    ]
    command = "./hijack_as200.sh"

    # Create separate process to run command after delay
    p = multiprocessing.Process(target=execute_command_after_delay, args=(4, command,))
    p.start()


    pool = multiprocessing.Pool()
    pool.map(ping_host, cmds)
    pool.close()  # Close pool to prevent any more tasks from being submitted to the pool
    pool.join() 

    p.join()