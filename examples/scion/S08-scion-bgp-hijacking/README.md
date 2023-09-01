# SCION and BGP mixed topology hijacking example

In this example a mixed topology with BGP and SCION is used. There a two SCION ISDs. Each ISD has one core AS and two none-core ASes.

## ISD 1

- Core AS 1-150
- None-Core AS 1-151 and 1-152

## ISD 2

- Core AS 2-160
- None-Core AS 2-161 and 2-162

## BGP hijacking AS 2-161

In this example `AS 1-151` is going to observe the hijacking of `AS 2-161` by advisory `AS 2-162`. The IP prefix `10.161.0.0/24` is targeted. To do that, `AS 2-162` is going to announce a false BGP route/path. On all BGP border routers [bird](<https://bird.network.cz/>) is installed. Open the BGP configuration of `AS 2-162` in `/etc/bird/bird.conf` and append the lines below to the end of the configuration.

Any IP address inside 10.161.0.0/24 will match with the true IP prefix and the fake IP prefixes announced by the attacker and `AS 2-161`, but the two announced by the attacker have a longer match (25 bits, compared to the 24 bits from AS-153), so the attacker's prefixes will be selected by all the BGP routers on the Internet.

```xml
protocol static hijacks {
    ipv4 {
        table t_bgp;
    };
    route 10.161.0.0/25 blackhole   { bgp_large_community.add(LOCAL_COMM); };
    route 10.161.0.128/25 blackhole { bgp_large_community.add(LOCAL_COMM); };
}
```

To make the changes public, the BGP configuration has to be reloaded with

```bash
birdc configure
```

## Testing

Now any host in the emulated Internet can be used to ping the victim `10.161.0.71` in `AS 2-161`. ICMP pinging the victim will not be possible, because the packets are hijacked by `AS 2-162` and discarded/blackholed. To see where the packets go, we can start the map tool and set the filter to icmp.

```bash
ping 10.161.0.71 
```

The hijack can be ended by removing the above configuration. After a reload of bird, the original/true routes should be used again.

## SCION

Using the SCION architecture to ping the victim `10.161.0.71` in `AS 2-161` should still be possible, since only BGP is affected. In practice (in the SEED emulator) it does not work. Why?
We use SCMP messages and `scion ping` to reach the victim. The following filter can be used to visualize the flow of packets: `udp[12] == 202``

```bash
scion ping 2-161,10.161.0.71
```

We see that contrary to the assumption SCION packets are diverted. Although we notice that the traffic reaches `AS 2-161` border router and then is directed to the attacker. Lets look at the routing table of `AS 2-161` border router with `ip route`.

```bash
10.0.0.7 dev dummy0 proto bird scope link metric 32 
10.101.0.0/24 dev ix101 proto kernel scope link src 10.101.0.161 
10.101.0.0/24 dev ix101 proto bird scope link metric 32 
10.150.0.0/24 via 10.101.0.160 dev ix101 proto bird metric 32 
10.151.0.0/24 via 10.101.0.160 dev ix101 proto bird metric 32 
10.152.0.0/24 via 10.101.0.160 dev ix101 proto bird metric 32 
10.160.0.0/24 via 10.101.0.160 dev ix101 proto bird metric 32 
10.161.0.0/25 via 10.101.0.160 dev ix101 proto bird metric 32 
10.161.0.0/24 dev net0 proto kernel scope link src 10.161.0.254 
10.161.0.0/24 dev net0 proto bird scope link metric 32 
10.161.0.128/25 via 10.101.0.160 dev ix101 proto bird metric 32 
10.162.0.0/24 via 10.101.0.160 dev ix101 proto bird metric 32 
```

Both /25 entries are present. Because SCION and BGP run on the same container, the SCION packages are also forwarded to the advisory instead of being forwarded internally. Lets fix that, by adding to new routes:

```bash
ip route add 10.161.0.0/25 dev net0 metric 10
ip route add 10.161.0.128/25 dev net0 metric 10 
```

Now SCION pings are forwarded to the end host, while the BGP hijacking attack is still present.
