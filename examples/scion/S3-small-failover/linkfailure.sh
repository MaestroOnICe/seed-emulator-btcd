#! /bin/bash
echo "disabling ix21"
docker exec -it as100r-br0-10.100.0.254 /bin/zsh -c "tc qdisc del dev ix21 root && tc qdisc add dev ix21 root netem loss 100%"

#loop five times
for i in {1..49}
do
    sleep 10
    echo "enabling ix21"
    docker exec -it as100r-br0-10.100.0.254 /bin/zsh -c "tc qdisc del dev ix21 root"
    sleep 10
    echo "disabling ix21"
    docker exec -it as100r-br0-10.100.0.254 /bin/zsh -c "tc qdisc add dev ix21 root netem loss 100%"
done

sleep 10
docker exec -it as100r-br0-10.100.0.254 /bin/zsh -c "tc qdisc del dev ix21 root"