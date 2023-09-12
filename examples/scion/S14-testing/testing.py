#!/usr/bin/env python3

from ipaddress import IPv4Network
from seedemu.compiler import Docker, Graphviz
from seedemu.core import Emulator
from seedemu.layers import ScionBase, ScionRouting, ScionIsd, Scion, Ospf, Ibgp, Ebgp, PeerRelationship 
from seedemu.layers.Scion import LinkType as ScLinkType


# ###############################################################################
# AS factory

# Tier 1 ASes have 4 border routers
def create_tier1_as(isd, asn):
    as_ = base.createAutonomousSystem(asn)
    scion_isd.addIsdAs(isd, asn, is_core=True)
    as_.setBeaconingIntervals('30s', '30s', '30s')

    as_.createNetwork('net0')
    as_.createNetwork('net1')
    as_.createNetwork('net2')    
    as_.createNetwork('net3')
    as_.createControlService('cs1').joinNetwork('net0')

    br0 = as_.createRouter('br0')
    br1 = as_.createRouter('br1')
    br2 = as_.createRouter('br2')
    br3 = as_.createRouter('br3')

    br0.joinNetwork('net0').joinNetwork('net1')
    br1.joinNetwork('net1').joinNetwork('net2')
    br2.joinNetwork('net2').joinNetwork('net3')
    br3.joinNetwork('net3').joinNetwork('net0')
    return as_

# Tier 2 ASes have 2 border routers
def create_tier2_as(isd, asn, issuer=None):
    as_ = base.createAutonomousSystem(asn)
    scion_isd.addIsdAs(isd, asn, False)
    scion_isd.setCertIssuer((isd, asn), issuer)
    as_.setBeaconingIntervals('30s', '30s', '30s')

    as_.createNetwork('net0')
    as_.createNetwork('net1')
    as_.createControlService('cs1').joinNetwork('net0')

    br0 = as_.createRouter('br0')
    br1 = as_.createRouter('br1')
    
    br0.joinNetwork('net0').joinNetwork('net1')
    br1.joinNetwork('net0').joinNetwork('net1')
    return as_

# Tier 3 ASes have 1 border router
def create_tier3_as(isd: int, asn: int, issuer=None):
    as_ = base.createAutonomousSystem(asn)
    scion_isd.addIsdAs(isd, asn, False)
    scion_isd.setCertIssuer((isd, asn), issuer)
    as_.setBeaconingIntervals('30s', '30s', '30s')

    as_.createNetwork('net0')
    as_.createControlService('cs1').joinNetwork('net0')

    br0 = as_.createRouter('br0')
    br0.joinNetwork('net0')
    return as_

class CrossConnectNetAssigner:
    def __init__(self):
        self.subnet_iter = IPv4Network("10.3.0.0/16").subnets(new_prefix=29)
        self.xc_nets = {}

    def next_addr(self, net):
        if net not in self.xc_nets:
            hosts = next(self.subnet_iter).hosts()
            next(hosts) # Skip first IP (reserved for Docker)
            self.xc_nets[net] = hosts
        return "{}/29".format(next(self.xc_nets[net]))

xc_nets = CrossConnectNetAssigner()


ebgp_types = {
    "peer": PeerRelationship.Peer,
    "provider": PeerRelationship.Provider,
    "core": PeerRelationship.Peer
}

sclink_type = {
    "peer": ScLinkType.Peer,
    "provider": ScLinkType.Transit,
    "core": ScLinkType.Core   
}

# SCION and BGP cross connect two ASes
def XConnect(asn_a: int, asn_b: int, type: str):
    # cross connecting AS a <-> AS b
    as_a = base.getAutonomousSystem(asn_a)
    as_b = base.getAutonomousSystem(asn_b)
    br_a = as_a.getRouter('br0')
    br_b = as_b.getRouter('br0')
    br_a.crossConnect(asn_b, 'br0', xc_nets.next_addr(f'{asn_a}-{asn_b}'))
    br_b.crossConnect(asn_a, 'br0', xc_nets.next_addr(f'{asn_a}-{asn_b}'))

    # lookup ISD AS a and ISD b are in, at this time, one AS is only in one ISD
    as_a_isd = scion_isd.getAsIsds(asn_a)[0]
    as_b_isd = scion_isd.getAsIsds(asn_b)[0]

    # loggng each connection (BGP and SCION) to a file, of later use
    source_as = asn_a
    bgp_destination = f'10.{asn_b}.0.71'
    scion_destination = f'{as_b_isd[0]}-{asn_b},10.{asn_b}.0.71'
    with open(txt_file, mode='a', newline='') as file:
        file.write(f'1 |{source_as} |{bgp_destination}\n2 |{source_as} |{scion_destination}\n')

    # will throw error if link type does not match
    scion.addXcLink((as_a_isd[0],asn_a), (as_b_isd[0],asn_b), sclink_type.get(type, "null"))
    
    # will throw error if link type does not match
    ebgp.addCrossConnectPeering(asn_a, asn_b, ebgp_types.get(type, "null"))


# Connect an AS to an IXP, with SCION and BGP
# SCION connections are saved, because they will be added in the end
# due to the need to specify each connectin like 
# scion.addIxLink(IXn, (ISD, ASn), (ISD, ASn), Linktype)

def IXPConnect(ixn: int, asn: int):
    # AS has to join the network of IXP 
    br = base.getAutonomousSystem(asn).getRouter('br0')
    br.joinNetwork(f'ix{ixn}')
    ebgp.addRsPeer(ixn, asn)
    ixs[ixn].append(asn)

def AddScionIXPConnections():
    addedIXConnections = []
    for ixn, ixn_list in ixs.items():
        for asn_a in ixn_list:
            for asn_b in ixn_list:
                if asn_a != asn_b:
                    # skip this pair, when both endpoints have already an IX link between them
                    if([ixn, asn_a, asn_b ] in addedIXConnections or [ixn, asn_b, asn_a ]in addedIXConnections):
                         continue

                    # lookup ISD AS a and ISD b are in, at this time, one AS is only in one ISD
                    as_a_isd = scion_isd.getAsIsds(asn_a)[0]
                    as_b_isd = scion_isd.getAsIsds(asn_b)[0]

                    # loggng each connection (BGP and SCION) to a file, of later use
                    source_as = asn_a
                    bgp_destination = f'10.{asn_b}.0.71'
                    scion_destination = f'{as_b_isd[0]}-{asn_b},10.{asn_b}.0.71'
                    with open(txt_file, mode='a', newline='') as file:
                        file.write(f'1 |{source_as} |{bgp_destination}\n2 |{source_as} |{scion_destination}\n')

                    # A link of an IX should only be scripted once, otherwise the link would be created twice in both directions
                    addedIXConnections.append([ixn, asn_a, asn_b]) 
                    #print(ixn, "connect ",as_a_isd[0], asn_a," to ",as_b_isd[0], asn_b, "as peer")            
                    scion.addIxLink(ixn, (as_a_isd[0], asn_a), (as_b_isd[0], asn_b), ScLinkType.Peer)


###############################################################################
# Initialize
emu = Emulator()
base = ScionBase()
routing = ScionRouting()
ospf = Ospf()
scion_isd = ScionIsd()
scion = Scion()
ebgp = Ebgp()


###############################################################################
# Isolation Domains
isd1 = base.createIsolationDomain(1) # Europe
isd2 = base.createIsolationDomain(2) # Asia

# Customize names (for visualization purpose)
isd1.setLabel('Europe')
isd2.setLabel('Asia')

###############################################################################
# Internet Exchanges
ix20 = base.createInternetExchange(20) # Frankfurt (Europe)
#ix21 = base.createInternetExchange(21) # London (Europe)
#ix22 = base.createInternetExchange(22) # London (Europe)

# # Customize names (for visualization purpose)
ix20.getPeeringLan().setDisplayName('Frankfurt-20')
#ix21.getPeeringLan().setDisplayName('London-21')

ixs = {}
ixn_list = base.getInternetExchangeIds()
for ixn in ixn_list:
    ixs[ixn] = []

###############################################################################
# Europe ISD 1
# Tier 1 ASes
arelion = create_tier1_as(1, 100)
# Tier 2 ASes
swisscom = create_tier2_as(1, 101, issuer=100) # Issuer: Arelion


###############################################################################
# Asia ISD 2
# Tier 1 ASes
telstra = create_tier1_as(2, 150)
# Tier 2 ASes
microscan = create_tier2_as(2, 151, issuer=150) # Issuer: Telstra

###############################################################################
# Links
XConnect(100, 101, "provider")
XConnect(100, 150, "core")

telstra.getRouter('br0').joinNetwork('ix20')
swisscom.getRouter('br0').joinNetwork('ix20')

IXPConnect(20, 150)
IXPConnect(20, 101)

###############################################################################
#Rendering
AddScionIXPConnections()
emu.addLayer(base)
emu.addLayer(routing)
emu.addLayer(ospf)
emu.addLayer(scion_isd)
emu.addLayer(scion)
emu.addLayer(ebgp)

emu.render()

# ##############################################################################
# Compilation
emu.compile(Docker(), "./output", override=True)
emu.compile(Graphviz(), "./output/graphs", override=True)