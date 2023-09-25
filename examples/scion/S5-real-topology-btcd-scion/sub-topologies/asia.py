#!/usr/bin/env python3

from ipaddress import IPv4Network
from seedemu.compiler import Docker, Graphviz
from seedemu.core import Emulator
from seedemu.layers import ScionBase, ScionRouting, ScionIsd, Scion, Ospf, Ibgp, Ebgp, PeerRelationship 
from seedemu.layers.Scion import LinkType as ScLinkType
import examples.scion.utility.utils as utils
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
isd3 = base.createIsolationDomain(3) # Asia
isd4 = base.createIsolationDomain(4) # Asia CLoud

# Customize names (for visualization purpose)
isd3.setLabel('Asia')
isd4.setLabel('Asia Cloud')


###############################################################################
# Internet Exchanges
#ix23 = base.createInternetExchange(23) # Frankfurt (Europe)
ix24 = base.createInternetExchange(24) # London (Europe)
#ix22 = base.createInternetExchange(22) # London (Europe)

# # Customize names (for visualization purpose)
#ix23.getPeeringLan().setDisplayName('HongKong-23')
ix24.getPeeringLan().setDisplayName('Singapore-24')


###############################################################################
# Helper
path_checker = utils.PathChecker()
cross_connector = utils.CrossConnector(base, scion_isd, ebgp, scion, path_checker)
ixp_connector = utils.IXPConnector(base, scion_isd, ebgp, scion, path_checker)
maker = utils.AutonomousSystemMaker(base, scion_isd)


###############################################################################
# ASIA ISD 3
# Tier 1 ASes
telstra = maker.createTier1AS(3, 126)
singapor_com = maker.createTier1AS(3, 127)

# Tier 2 ASes
tm = maker.createTier2AS(3, 129, issuer=126) # Issuer: Telstra
micro = maker.createTier2AS(3, 128, issuer=126) # Issuer: Telstra
kinx = maker.createTier2AS(3, 130, issuer=126) # Issuer: Telstra

# Tier 3 ASes
# 131 - 135
stub_groupA_isd3 = []
for asn in range(131, 136):
    as_ = maker.createTier3AS(3, asn, issuer=126) # Issuer: Telstra
    stub_groupA_isd3.append(asn)
                     
# 136 -138
stub_groupB_isd3 = []
for asn in range(136, 139):
    as_ = maker.createTier3AS(3, asn, issuer=126) # Issuer: Telstra
    stub_groupB_isd3.append(asn)


# ASIA CLOUD ISD 4
# Tier 1 ASes
alibaba = maker.createTier1AS(4, 139)

###############################################################################
# Links


# Singapore Telecommunication 3-127 to 
# Tier1: 3-126
# Tier2: 3-128, 3-129
cross_connector.XConnect(127, 126, "core")
cross_connector.XConnect(127, 128, "provider")
cross_connector.XConnect(127, 129, "provider")

# Telstra 3-126 to 
# Tier1: 4-139
# Tier2: 3-129
cross_connector.XConnect(126, 139, "core")
cross_connector.XConnect(126, 129, "provider")


# Microscan 3-128 to
# Tier2: 3-130
cross_connector.XConnect(128, 130, "provider")

# Kinx 3-130 to
# Tier2: 3-129
# IX: IX24
cross_connector.XConnect(130, 129, "peer")
ixp_connector.IXPConnect(24, 130)

# TM 3-129 to
# Tier2: 3-136 tp 3-138
# IX subscribe to IX23 and IX24
for asn in stub_groupB_isd3:
    cross_connector.XConnect(129, asn, "provider")

#ixp_connector.IXPConnect(23, 129) 
ixp_connector.IXPConnect(24, 129)


# ISD 3 Stub Group A
# IX24
for asn in stub_groupA_isd3:
    ixp_connector.IXPConnect(24, asn)
    ixp_connector.addIXLink(24, 128, asn, ScLinkType.Transit)
    #scion.addIxLink(24, (3, 128), (3, asn), ScLinkType.Transit)

# Alibaba IX link

cross_connector.XConnect(139, 129, "provider")


###############################################################################
#Rendering
ixp_connector.addScionIXPConnections()
emu.addLayer(base)
emu.addLayer(routing)
emu.addLayer(ospf)
emu.addLayer(scion_isd)
emu.addLayer(scion)
emu.addLayer(ebgp)

emu.render()

###############################################################################
# Compilation
emu.compile(Docker(), "./output", override=True)
emu.compile(Graphviz(), "./output/graphs", override=True)

###############################################################################
# Deploy and check all paths
path_checker.deployAndCheck()