#!/usr/bin/env python3

from ipaddress import IPv4Network
from seedemu.compiler import Docker, Graphviz
from seedemu.core import Emulator
from seedemu.layers import ScionBase, ScionRouting, ScionIsd, Scion, Ospf, Ibgp, Ebgp, PeerRelationship 
from seedemu.layers.Scion import LinkType as ScLinkType


###############################################################################
# Numbering:
#
# ISD numbering is from 1 to 19
# IX numbering is from 20 to 39
#
# AS numbering follows the convention:
#
# ISD 1 + 2
# 100 to 125
# 
# ISD 3 + 4
# 126 to 139
#
# ISD 5
# 140 to 149
#
# ISD 6
# 150 to 159 
# 
# ISD 7 + 8
# 160 to 180 


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
def create_tier3_as(isd, asn, issuer=None):
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


###############################################################################
# Initialize
emu = Emulator()
base = ScionBase()
routing = ScionRouting()
ospf = Ospf()
scion_isd = ScionIsd()
scion = Scion()
ibgp = Ibgp()
ebgp = Ebgp()


###############################################################################
# Isolation Domains
isd1 = base.createIsolationDomain(1) # Europe
isd2 = base.createIsolationDomain(2) # Cloud - Europe
isd3 = base.createIsolationDomain(3) # Asia
isd4 = base.createIsolationDomain(4) # Cloud - Asia
isd5 = base.createIsolationDomain(5) # Africa
isd6 = base.createIsolationDomain(6) # South America
isd7 = base.createIsolationDomain(7) # North America
isd8 = base.createIsolationDomain(8) # Cloud - North America

# Customize names (for visualization purpose)
isd1.setLabel('Europe')
isd2.setLabel('Cloud - Europe')
isd3.setLabel('Asia')
isd4.setLabel('Cloud - Asia')
isd5.setLabel('Africa')
isd6.setLabel('South America')
isd7.setLabel('North America')
isd8.setLabel('Cloud - North America')


###############################################################################
# Internet Exchanges
ix20 = base.createInternetExchange(20) # Frankfurt (Europe)
ix21 = base.createInternetExchange(21) # London (Europe)
ix22 = base.createInternetExchange(22) # Amsterdam (Europe)
ix23 = base.createInternetExchange(23) # Hong Kong (Asia)
ix24 = base.createInternetExchange(24) # Singapore (Asia)
ix25 = base.createInternetExchange(25) # Accra (Africa)
ix26 = base.createInternetExchange(26) # Sao Paulo (South America)
ix27 = base.createInternetExchange(27) # Los Angeles (North America)
ix28 = base.createInternetExchange(28) # Miami (North America)


# Customize names (for visualization purpose)
ix20.getPeeringLan().setDisplayName('Frankfurt-100')
ix21.getPeeringLan().setDisplayName('London-101')
ix22.getPeeringLan().setDisplayName('Amsterdam-102')
ix23.getPeeringLan().setDisplayName('Hong Kong-103')
ix24.getPeeringLan().setDisplayName('Singapore-104')
ix25.getPeeringLan().setDisplayName('Accra-105')
ix26.getPeeringLan().setDisplayName('Sao Paulo-106')
ix27.getPeeringLan().setDisplayName('Los Angeles-107')
ix28.getPeeringLan().setDisplayName('Miami-108')


###############################################################################
# Europe ISD 1 (100 to 122)
# Tier 1 ASes
arelion = create_tier1_as(1, 100)
telecom_italia = create_tier1_as(1, 101)
deutsche_telekom = create_tier1_as(1, 102)
retn_limited= create_tier1_as(1,103)

# Tier 2 ASes
core_backbone = create_tier2_as(1, 104, issuer=102) # Issuer: Deutsche Telekom
swisscom = create_tier2_as(1, 105, issuer=102) # Issuer: Deutsche Telekom
tele_2 = create_tier2_as(1, 106, issuer=102) # Issuer: Deutsche Telekom

# Tier 3 ASes
stub_as_isd1 = {}
for asn in range(107, 123):
    as_ = create_tier3_as(1, asn, issuer=102) # Issuer: Deutsche Telekom
    stub_as_isd1[asn] = as_


###############################################################################
# Cloud - Europe ISD 2 (123 to 125)
ovh_cloud = create_tier1_as(2, 123)
contabo_cloud = create_tier1_as(2, 124)
hetzner_cloud = create_tier1_as(2, 125)


###############################################################################
# Asia ISD 3 (126 to 138)
# Tier 1 ASes
telstra = create_tier1_as(3, 126)
singapore_telecommunication = create_tier1_as(3, 127)

# Tier 2 ASes
microscan = create_tier2_as(3, 128, issuer=126) # Issuer: Telstra
tm_technology = create_tier2_as(3, 129, issuer=126) # Issuer: Telstra
kinx = create_tier2_as(3, 130, issuer=126) # Issuer: Telstra

# Tier 3 ASes
stub_as_isd3 = {}
for asn in range(131, 139):
    as_ = create_tier3_as(3, asn, issuer=126) # Issuer: Telstra
    stub_as_isd3[asn] = as_


###############################################################################
# Cloud - Asia ISD 4 (139)
alibab_cloud = create_tier1_as(4, 139)


###############################################################################
# Africa ISD 5 (140 to 149)
# Tier 1 ASes
angola_cables = create_tier1_as(5, 140)

# Tier 2 ASes
ecoband = create_tier2_as(5, 141, issuer=140) # Issuer: Angola Cables
africom = create_tier2_as(5, 142, issuer=140) # Issuer: Angola Cables

# Tier 3 ASes
stub_as_isd5 = {}
for asn in range(143, 150):
    as_ = create_tier3_as(5, asn, issuer=140) # Issuer: Angola Cables
    stub_as_isd5[asn] = as_


###############################################################################
# South America ISD 6 (150 to 159)
# Tier 1 ASes
algar_telecomm = create_tier1_as(6, 150)
globe_net = create_tier1_as(6, 151)

# Tier 2 ASes
locaweb = create_tier2_as(6, 152, issuer=150)

# Tier 3 ASes
stub_as_isd6 = {}
for asn in range(153, 160):
    as_ = create_tier3_as(6, asn, issuer=150) # Issuer: Algar Telecomm
    stub_as_isd6[asn] = as_

###############################################################################
# North America ISD 7 (160 to 175 )
# Tier 1 ASes
level_3 = create_tier1_as(7, 160)
cogent = create_tier1_as(7, 161)
verizon = create_tier1_as(7, 162)

# Tier 2 ASes
liquidweb = create_tier2_as(7, 163, issuer=160)
lunavi = create_tier2_as(7, 164, issuer=160)

# Tier 3 ASes
stub_as_isd7 = {}
for asn in range(165, 176):
    as_ = create_tier3_as(7, asn, issuer=160) # Issuer: level3
    stub_as_isd7[asn] = as_

###############################################################################
# Cloud - North America ISD 8 (176 to 178)
# Tier 2 ASes
aws_cloud = create_tier1_as(8, 176)
google_cloud = create_tier1_as(8, 177)
digital_ocean_cloud = create_tier1_as(8, 178)


###############################################################################
# Links originating in Tier 1 ASes

# Arelion 1-100 to 
# Tier1: 1-101, 1-102, 7-161, 
# Tier2: 1-104
br = arelion.getRouter('br0')
br.crossConnect(101, 'br0', xc_nets.next_addr('100-101'))
br.crossConnect(102, 'br0', xc_nets.next_addr('100-102'))
br.crossConnect(161, 'br0', xc_nets.next_addr('100-161'))
br.crossConnect(104, 'br0', xc_nets.next_addr('100-104'))
scion.addXcLink((1, 100), (1, 101), ScLinkType.Core)
scion.addXcLink((1, 100), (1, 102), ScLinkType.Core)
scion.addXcLink((1, 100), (7, 161), ScLinkType.Core)
scion.addXcLink((1, 100), (1, 104), ScLinkType.Transit)
ebgp.addCrossConnectPeering(100, 101, PeerRelationship.Peer)
ebgp.addCrossConnectPeering(100, 102, PeerRelationship.Peer)
ebgp.addCrossConnectPeering(100, 161, PeerRelationship.Peer)
ebgp.addCrossConnectPeering(100, 104, PeerRelationship.Provider)

# Telecom Italia 1-101 to 
# Tier1: 1-102, 1-103, 7-162
# Tier2: 1-105
br = telecom_italia.getRouter('br0')
br.crossConnect(102, 'br0', xc_nets.next_addr('101-102'))
br.crossConnect(105, 'br0', xc_nets.next_addr('101-105'))
br.crossConnect(103, 'br0', xc_nets.next_addr('101-103'))
br.crossConnect(162, 'br0', xc_nets.next_addr('101-162'))
scion.addXcLink((1, 101), (1, 102), ScLinkType.Core)
scion.addXcLink((1, 101), (1, 105), ScLinkType.Core)
scion.addXcLink((1, 101), (1, 103), ScLinkType.Peer)
scion.addXcLink((1, 101), (7, 162), ScLinkType.Core)
ebgp.addCrossConnectPeering(101, 102, PeerRelationship.Peer)
ebgp.addCrossConnectPeering(101, 105, PeerRelationship.Peer)
ebgp.addCrossConnectPeering(101, 103, PeerRelationship.Peer)
ebgp.addCrossConnectPeering(101, 162, PeerRelationship.Peer)

# Deutsche Telekom 1-102 to 
# Tier1: 5-140
# Tier2: 1-106, 1-104
br = deutsche_telekom.getRouter('br0')
br.crossConnect(140, 'br0', xc_nets.next_addr('102-140'))
br.crossConnect(106, 'br0', xc_nets.next_addr('102-106'))
br.crossConnect(104, 'br0', xc_nets.next_addr('102-104'))
scion.addXcLink((1, 102), (5, 140), ScLinkType.Core)
scion.addXcLink((1, 102), (1, 106), ScLinkType.Transit)
scion.addXcLink((1, 102), (1, 104), ScLinkType.Transit)
ebgp.addCrossConnectPeering(102, 140, PeerRelationship.Peer)
ebgp.addCrossConnectPeering(102, 106, PeerRelationship.Provider)
ebgp.addCrossConnectPeering(102, 104, PeerRelationship.Provider)

# RETN Limited 1-103 to 
# Tier1: 3-127
br = retn_limited.getRouter('br0')
br.crossConnect(127, 'br0', xc_nets.next_addr('103-127'))
scion.addXcLink((1, 103), (3, 127), ScLinkType.Core)
ebgp.addCrossConnectPeering(103, 127, PeerRelationship.Peer)

# Singapore Telecommunication 3-127 to 
# Tier1: 3-126, 5-140
# Tier2: 3-128, 3-129
br = singapore_telecommunication.getRouter('br0')
br.crossConnect(127, 'br0', xc_nets.next_addr('127-126'))
br.crossConnect(127, 'br0', xc_nets.next_addr('127-140'))
br.crossConnect(127, 'br0', xc_nets.next_addr('127-128'))
br.crossConnect(127, 'br0', xc_nets.next_addr('127-129'))
scion.addXcLink((3, 127), (3, 126), ScLinkType.Core)
scion.addXcLink((3, 127), (5, 140), ScLinkType.Core)
scion.addXcLink((3, 127), (3, 128), ScLinkType.Transit)
scion.addXcLink((3, 127), (3, 129), ScLinkType.Transit)
ebgp.addCrossConnectPeering(127, 126, PeerRelationship.Peer)
ebgp.addCrossConnectPeering(127, 140, PeerRelationship.Peer)
ebgp.addCrossConnectPeering(127, 128, PeerRelationship.Provider)
ebgp.addCrossConnectPeering(127, 129, PeerRelationship.Provider)

# Telstra 3-139 to 
# Tier1: 7-160
# Tier2: 3-129
br = telstra.getRouter('br0')
br.crossConnect(160, 'br0', xc_nets.next_addr('126-160'))
br.crossConnect(129, 'br0', xc_nets.next_addr('126-129'))
scion.addXcLink((3, 126), (7, 160), ScLinkType.Core)
scion.addXcLink((3, 126), (3, 129), ScLinkType.Transit)
ebgp.addCrossConnectPeering(126, 160, PeerRelationship.Peer)
ebgp.addCrossConnectPeering(126, 129, PeerRelationship.Provider)

# Alibab 3-126 to 
# ix103 and 104
br = alibab_cloud.getRouter('br0')

# Angola Cable 5-140 to 
# Tier1: 6-150
# Tier2: 1-104, 5-141, 5-142
br = telstra.getRouter('br0')
br.crossConnect(150, 'br0', xc_nets.next_addr('140-150'))
br.crossConnect(104, 'br0', xc_nets.next_addr('140-104'))
br.crossConnect(141, 'br0', xc_nets.next_addr('140-141'))
br.crossConnect(142, 'br0', xc_nets.next_addr('140-142'))
scion.addXcLink((5, 140), (6, 150), ScLinkType.Core)
scion.addXcLink((5, 140), (1, 104), ScLinkType.Peer)
scion.addXcLink((5, 140), (5, 141), ScLinkType.Transit)
scion.addXcLink((5, 140), (5, 142), ScLinkType.Transit)
ebgp.addCrossConnectPeering(140, 150, PeerRelationship.Peer)
ebgp.addCrossConnectPeering(140, 104, PeerRelationship.Peer)
ebgp.addCrossConnectPeering(140, 141, PeerRelationship.Provider)
ebgp.addCrossConnectPeering(140, 142, PeerRelationship.Provider)

# Algar Telecom 6-150 to 
# Tier1: 6-151, 7-162
br = algar_telecomm.getRouter('br0')
br.crossConnect(151, 'br0', xc_nets.next_addr('150-151'))
br.crossConnect(162, 'br0', xc_nets.next_addr('150-162'))
scion.addXcLink((6, 150), (6, 151), ScLinkType.Core)
scion.addXcLink((6, 150), (7, 162), ScLinkType.Core)
ebgp.addCrossConnectPeering(150, 151, PeerRelationship.Peer)
ebgp.addCrossConnectPeering(150, 162, PeerRelationship.Peer)

# GlobeNet 6-151 to 
# Tier1: 7-162
# Tier2: 6-152
br = globe_net.getRouter('br0')
br.crossConnect(162, 'br0', xc_nets.next_addr('151-162'))
br.crossConnect(152, 'br0', xc_nets.next_addr('151-152'))
scion.addXcLink((6, 151), (7, 162), ScLinkType.Core)
scion.addXcLink((6, 151), (5, 152), ScLinkType.Transit)
ebgp.addCrossConnectPeering(151, 162, PeerRelationship.Peer)
ebgp.addCrossConnectPeering(151, 152, PeerRelationship.Provider)

# Level3 7-160 to 
# Tier1: 7-161, 7-162
# Tier2: 1-104, 7-164
br = level_3.getRouter('br0')
br.crossConnect(161, 'br0', xc_nets.next_addr('160-161'))
br.crossConnect(162, 'br0', xc_nets.next_addr('160-162'))
br.crossConnect(104, 'br0', xc_nets.next_addr('160-104'))
br.crossConnect(164, 'br0', xc_nets.next_addr('160-164'))
scion.addXcLink((7, 160), (7, 161), ScLinkType.Core)
scion.addXcLink((7, 160), (7, 162), ScLinkType.Core)
scion.addXcLink((7, 160), (1, 104), ScLinkType.Transit)
scion.addXcLink((7, 160), (7, 164), ScLinkType.Transit)
ebgp.addCrossConnectPeering(160, 161, PeerRelationship.Peer)
ebgp.addCrossConnectPeering(160, 162, PeerRelationship.Peer)
ebgp.addCrossConnectPeering(160, 104, PeerRelationship.Provider)
ebgp.addCrossConnectPeering(160, 164, PeerRelationship.Provider)

# Cogent 7-161 to 
# Tier1: 7-162
# Tier2: 1-104
br = cogent.getRouter('br0')
br.crossConnect(162, 'br0', xc_nets.next_addr('161-162'))
br.crossConnect(104, 'br0', xc_nets.next_addr('161-104'))
scion.addXcLink((7, 161), (7, 162), ScLinkType.Core)
scion.addXcLink((7, 161), (1, 104), ScLinkType.Transit)
ebgp.addCrossConnectPeering(160, 162, PeerRelationship.Peer)
ebgp.addCrossConnectPeering(160, 104, PeerRelationship.Provider)

# Verizon 7-162 to 
# Tier2: 7-163
br = verizon.getRouter('br0')
br.crossConnect(163, 'br0', xc_nets.next_addr('162-163'))
scion.addXcLink((7, 162), (7, 163), ScLinkType.Transit)
ebgp.addCrossConnectPeering(162, 163, PeerRelationship.Provider)

###############################################################################
# Rendering
emu.addLayer(base)
emu.addLayer(routing)
emu.addLayer(ospf)
emu.addLayer(scion_isd)
emu.addLayer(scion)
emu.addLayer(ibgp)
emu.addLayer(ebgp)

emu.render()

###############################################################################
# Compilation
emu.compile(Docker(), "./output", override=True)
emu.compile(Graphviz(), "./output/graphs", override=True)