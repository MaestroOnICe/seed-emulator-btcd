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
# setting crossconnect and ixconnect
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
def XConnect(asn_a: int, asn_b: int, type: str, as_a_router="br0", as_b_router="br0"):
    # cross connecting AS a <-> AS b
    as_a = base.getAutonomousSystem(asn_a)
    as_b = base.getAutonomousSystem(asn_b)
    br_a = as_a.getRouter(as_a_router)
    br_b = as_b.getRouter(as_b_router)
    br_a.crossConnect(asn_b, as_b_router, xc_nets.next_addr(f'{asn_a}-{asn_b}'))
    br_b.crossConnect(asn_a, as_a_router, xc_nets.next_addr(f'{asn_a}-{asn_b}'))

    # lookup ISD AS a and ISD b are in, at this time, one AS is only in one ISD
    as_a_isd = scion_isd.getAsIsds(asn_a)[0]
    as_b_isd = scion_isd.getAsIsds(asn_b)[0]

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
                    if([asn_a, asn_b ] in addedIXConnections or [asn_b, asn_a ]in addedIXConnections):
                         continue

                    # lookup ISD AS a and ISD b are in, at this time, one AS is only in one ISD
                    as_a_isd = scion_isd.getAsIsds(asn_a)[0]
                    as_b_isd = scion_isd.getAsIsds(asn_b)[0]
                    addedIXConnections.append([asn_a, asn_b]) 
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
#ibgp = Ibgp()
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

# dict for registering IX scion paths
ixs = {}
ixn_list = base.getInternetExchangeIds()
for ixn in ixn_list:
    ixs[ixn] = []

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
stub_groupA_isd1 = {}
for asn in range(107, 119):
    as_ = create_tier3_as(1, asn, issuer=102) # Issuer: Deutsche Telekom
    stub_groupA_isd1[asn] = as_

stub_groupB_isd1 = {}
for asn in range(119, 123):
    as_ = create_tier3_as(1, asn, issuer=102) # Issuer: Deutsche Telekom
    stub_groupB_isd1[asn] = as_


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
stub_groupA_isd3 = {}
for asn in range(131, 136):
    as_ = create_tier3_as(3, asn, issuer=126) # Issuer: Telstra
    stub_groupA_isd3[asn] = as_

stub_groupB_isd3 = {}
for asn in range(136, 139):
    as_ = create_tier3_as(3, asn, issuer=126) # Issuer: Telstra
    stub_groupB_isd3[asn] = as_


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
stub_groupA_isd5 = {}
for asn in range(143, 150):
    as_ = create_tier3_as(5, asn, issuer=140) # Issuer: Angola Cables
    stub_groupA_isd5[asn] = as_


###############################################################################
# South America ISD 6 (150 to 159)
# Tier 1 ASes
algar_telecomm = create_tier1_as(6, 150)
globe_net = create_tier1_as(6, 151)

# Tier 2 ASes
locaweb = create_tier2_as(6, 152, issuer=150)

# Tier 3 ASes
stub_groupA_isd6 = {}
for asn in range(153, 156):
    as_ = create_tier3_as(6, asn, issuer=150) # Issuer: Algar Telecomm
    stub_groupA_isd6[asn] = as_

stub_groupB_isd6 = {}
for asn in range(156, 160):
    as_ = create_tier3_as(6, asn, issuer=150) # Issuer: Algar Telecomm
    stub_groupB_isd6[asn] = as_

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
stub_groupA_isd7 = {}
for asn in range(165, 170):
    as_ = create_tier3_as(7, asn, issuer=160) # Issuer: level3
    stub_groupA_isd7[asn] = as_

stub_groupB_isd7 = {}
for asn in range(170, 176):
    as_ = create_tier3_as(7, asn, issuer=160) # Issuer: level3
    stub_groupB_isd7[asn] = as_

###############################################################################
# Cloud - North America ISD 8 (176 to 178)
# Tier 1 ASes
aws_cloud = create_tier1_as(8, 176)
google_cloud = create_tier1_as(8, 177)
digital_ocean_cloud = create_tier1_as(8, 178)


###############################################################################
# Links originating in Tier 1 ASes

# Arelion 1-100 to 
# Tier1: 1-101, 1-102, 7-161, 
# Tier2: 1-104
XConnect(100, 101, "core")
XConnect(100, 102, "core")
XConnect(100, 161, "core")
XConnect(100, 104, "provider")

# Telecom Italia 1-101 to 
# Tier1: 1-102, 1-103, 7-162
# Tier2: 1-105
XConnect(101, 102, "core")
XConnect(101, 103, "core")
XConnect(101, 162, "core")
XConnect(101, 105, "peer")

# Deutsche Telekom 1-102 to 
# Tier1: 5-140
# Tier2: 1-106, 1-104
XConnect(102, 140, "core")
XConnect(102, 106, "provider")
XConnect(102, 164, "provider")

# RETN Limited 1-103 to 
# Tier1: 3-127
XConnect(103, 127, "core")

# Cloud ovh 2-123 to
# IX100, IX101, IX102
IXPConnect(100, 123)
IXPConnect(101, 123)
IXPConnect(102, 123)

# Cloud Contabo 2-124 to
# IX100, IX101, IX102
IXPConnect(100, 124)
IXPConnect(101, 124)
IXPConnect(102, 124)

# Cloud Hetzner 2-125 to
# IX100, IX101, IX102
IXPConnect(100, 125)
IXPConnect(101, 125)
IXPConnect(102, 125)

# Singapore Telecommunication 3-127 to 
# Tier1: 3-126, 5-140
# Tier2: 3-128, 3-129
XConnect(127, 126, "core")
XConnect(127, 140, "core")
XConnect(127, 128, "provider")
XConnect(127, 129, "provider")

# Telstra 3-126 to 
# Tier1: 7-160
# Tier2: 3-129
XConnect(126, 160, "core")
XConnect(126, 129, "provider")

# Cloud Alibaba 3-139 to 
# ix103 and ix104
IXPConnect(103, 139)
IXPConnect(104, 139)

# Angola Cable 5-140 to 
# Tier1: 6-150
# Tier2: 1-104, 5-141, 5-142
XConnect(140, 150, "core")
XConnect(140, 104, "peer")
XConnect(140, 141, "provider")
XConnect(140, 142, "provider")

# Algar Telecom 6-150 to 
# Tier1: 6-151, 7-162
XConnect(150, 151, "core")
XConnect(150, 162, "core")

# GlobeNet 6-151 to 
# Tier1: 7-162
# Tier2: 6-152
XConnect(151, 162, "core")
XConnect(151, 152, "provider")

# Level3 7-160 to 
# Tier1: 7-161, 7-162
# Tier2: 1-104, 7-164
XConnect(160, 161, "core")
XConnect(160, 162, "core")
XConnect(160, 104, "provider")
XConnect(160, 164, "provider")

# Cogent 7-161 to 
# Tier1: 7-162
# Tier2: 1-104
XConnect(161, 162, "core")
XConnect(161, 104, "provider")

# Verizon 7-162 to 
# Tier2: 7-163
XConnect(162, 163, "provider")

# AWS Cloud 8-176 to
# IX107, IX108
IXPConnect(107, 176)
IXPConnect(108, 176)

# Google Cloud 8-177 to
# IX107, IX108
IXPConnect(107, 177)
IXPConnect(108, 177)

# Digital Ocean 8-178 to 
# Tier2:  Liquidweb 7-163
# IX108
XConnect(178, 163, "peer")
IXPConnect(108, 178)

###############################################################################
# Links originating in Tier 2 ASes

# core-Backbone 1-104 to
# Tier2: 5-141
# IX100, IX101, IX101
XConnect(104, 141, "peer")
IXPConnect(100, 104)
IXPConnect(101, 104)
IXPConnect(102, 104)
IXPConnect(107, 104)

# Swisscom 1-105 to
# Tier2: 1-104, 1-106
# IX100, IX101, IX101
XConnect(105, 104, "peer")
XConnect(105, 106, "peer")
IXPConnect(100, 105)
IXPConnect(101, 105)
IXPConnect(102, 105)

# Microscan 3-128 to
# Tier2: 3-130
XConnect(128, 130, "peer")

# TM Techbology 3-129 to
# IX103, IX104
IXPConnect(103, 129)
IXPConnect(104, 129)

# Kinx 3-130 to
# Tier2: 3-129
XConnect(130, 129, "peer")

# Ecoband 5-141 to
# Tier2: 5-142
# IX 105
XConnect(141, 142, "peer")
IXPConnect(105, 141)

# Africom 5-142 to
# IX 105
IXPConnect(105, 142)

# locaweb 6-152 to
# IX106
IXPConnect(106, 152)

# liquidweb 7-163 to
# Tier2: 7-164
# IX108
XConnect(163, 164, "peer")
IXPConnect(108, 163)

# lunavi 7-164 to
# IX107, IX108
IXPConnect(107, 164)
IXPConnect(108, 164)


###############################################################################
# Rendering
AddScionIXPConnections()
emu.addLayer(base)
emu.addLayer(routing)
emu.addLayer(ospf)
emu.addLayer(scion_isd)
emu.addLayer(scion)
#emu.addLayer(ibgp)
emu.addLayer(ebgp)

emu.render()

###############################################################################
# Compilation
emu.compile(Docker(), "./output", override=True)
emu.compile(Graphviz(), "./output/graphs", override=True)