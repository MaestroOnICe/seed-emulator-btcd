#! /bin/bash

docker exec -it as200h-cs1-10.200.0.71 /bin/zsh -c "ping 10.72.0.2 -c 1"
docker exec -it as200h-cs1-10.200.0.71 /bin/zsh -c "ping 10.180.0.71 -c 1"

echo "starting pings"
docker exec -d as200h-cs1-10.200.0.71 /bin/zsh -c "ping 10.72.0.2 -s 1400 -i 0.01 > /dev/null 2>&1 &"
docker exec -d as200h-cs1-10.200.0.71 /bin/zsh -c "ping 10.180.0.71 -s 1400 -i 0.01 > /dev/null 2>&1 &"