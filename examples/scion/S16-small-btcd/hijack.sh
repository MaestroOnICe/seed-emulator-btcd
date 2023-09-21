#!/bin/bash

asn="$1"

filename="/etc/bird/bird.conf"

command="/bin/cat <<EOM >>/etc/bird/bird.conf
protocol static hijacks {
    ipv4 {
        table t_bgp;
    };
    route 10.$asn.0.0/25 blackhole   { bgp_large_community.add(LOCAL_COMM); };
    route 10.$asn.0.128/25 blackhole { bgp_large_community.add(LOCAL_COMM); };
}
EOM"

docker exec -it as${asn}r-br0-10.${asn}.0.254 /bin/zsh -c "$command"

