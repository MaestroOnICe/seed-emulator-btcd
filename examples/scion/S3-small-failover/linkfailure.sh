#! /bin/bash
echo "disabling ix20"
docker exec -it as100r-br0-10.100.0.254 /bin/zsh -c "tc qdisc del dev ix20 root && tc qdisc add dev ix20 root netem loss 100%"

# loop five times
for i in {1..49}
do
    sleep 5
    echo "enabling ix20"
    docker exec -it as100r-br0-10.100.0.254 /bin/zsh -c "tc qdisc del dev ix20 root"
    sleep 5
    echo "disabling ix20"
    docker exec -it as100r-br0-10.100.0.254 /bin/zsh -c "tc qdisc add dev ix20 root netem loss 100%"
done

sleep 2
docker exec -it as100r-br0-10.100.0.254 /bin/zsh -c "tc qdisc del dev ix20 root"