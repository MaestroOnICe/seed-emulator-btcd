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
isd6 = base.createIsolationDomain(6) # Asia

# Customize names (for visualization purpose)
isd6.setLabel('Africa')



###############################################################################
# Internet Exchanges
ix25 = base.createInternetExchange(25) # London (Europe)

ix25.getPeeringLan().setDisplayName('Singapore-24')


###############################################################################
# Helper
path_checker = utils.PathChecker()
cross_connector = utils.CrossConnector(base, scion_isd, ebgp, scion, path_checker)
ixp_connector = utils.IXPConnector(base, scion_isd, ebgp, scion, path_checker)
maker = utils.AutonomousSystemMaker(base, scion_isd)


###############################################################################
# Africa ISD 5 (140 to 149)
# Tier 1 ASes
angola_cables = maker.createTier1AS(5, 140)

# Tier 2 ASes
ecoband = maker.createTier2AS(5, 141, issuer=140) # Issuer: Angola Cables
africom = maker.createTier2AS(5, 142, issuer=140) # Issuer: Angola Cables

# Tier 3 ASes
# 143 - 149
stub_groupA_isd5 = []
for asn in range(143, 150):
    as_ = maker.createTier3AS(5, asn, issuer=140) # Issuer: Angola Cables
    stub_groupA_isd5.append(asn)


###############################################################################
# Links
# Angola Cables 5-140
# Tier2: 5-142, 5-141
cross_connector.XConnect(140, 141, "provider")
cross_connector.XConnect(140, 142, "provider")

# Ecoband 5-141
# Tier2: 5-142
# IX: IX25
cross_connector.XConnect(141, 142, "peer")
ixp_connector.IXPConnect(25, 141)

# Africom 5-142
# IX: IX25
ixp_connector.IXPConnect(25, 142)
for asn in stub_groupA_isd5:
    ixp_connector.addIXLink(25, 142, asn, ScLinkType.Transit)

# Tier3 ASes in ISD 5
# IX: IX2025
for asn in stub_groupA_isd5:
    ixp_connector.IXPConnect(25, asn)

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