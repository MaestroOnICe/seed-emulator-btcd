#! /bin/bash
echo "disabling ix10"
docker exec -it as200r-br0-10.200.0.254 /bin/zsh -c "tc qdisc del dev ix10 root && tc qdisc add dev ix10 root netem loss 100%"

# loop five times
for i in {1..49}
do
    sleep 2
    echo "enabling ix10"
    docker exec -it as200r-br0-10.200.0.254 /bin/zsh -c "tc qdisc del dev ix10 root"
    sleep 5
    echo "disabling ix10"
    docker exec -it as200r-br0-10.200.0.254 /bin/zsh -c "tc qdisc add dev ix10 root netem loss 100%"
done

sleep 2
docker exec -it as200r-br0-10.200.0.254 /bin/zsh -c "tc qdisc del dev ix10 root"