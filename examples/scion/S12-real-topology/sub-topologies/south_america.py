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
isd6.setLabel('South America')



###############################################################################
# Internet Exchanges
ix26 = base.createInternetExchange(26) # London (Europe)

# # Customize names (for visualization purpose)
ix26.getPeeringLan().setDisplayName('Sao Paulo-26')


###############################################################################
# Helper
path_checker = utils.PathChecker()
cross_connector = utils.CrossConnector(base, scion_isd, ebgp, scion, path_checker)
ixp_connector = utils.IXPConnector(base, scion_isd, ebgp, scion, path_checker)
maker = utils.AutonomousSystemMaker(base, scion_isd)


###############################################################################
# South America ISD 6 (150 to 159)
# Tier 1 ASes
algar_telecomm = maker.createTier1AS(6, 150)
globe_net = maker.createTier1AS(6, 151)

# Tier 2 ASes
locaweb = maker.createTier2AS(6, 152, issuer=150)

# Tier 3 ASes
# 153 - 155
stub_groupA_isd6 = []
for asn in range(153, 156):
    as_ = maker.createTier3AS(6, asn, issuer=150) # Issuer: Algar Telecomm
    stub_groupA_isd6.append(asn)

# 156 - 159
stub_groupB_isd6 = []
for asn in range(156, 160):
    as_ = maker.createTier3AS(6, asn, issuer=150) # Issuer: Algar Telecomm
    stub_groupB_isd6.append(asn)


###############################################################################
# Links

# Algar Telecom 6-150
# Tier1: 6-151
cross_connector.XConnect(150, 151, "core")

# GlobeNet 6-151
# Tier2: 6-152
cross_connector.XConnect(151, 152, "provider")

# Locaweb 6-152
# Tier3: 6-156 until 6-159 and 6-153 until 6-155
# IX: IX26
ixp_connector.IXPConnect(26, 152)
for asn in stub_groupB_isd6:
    cross_connector.XConnect(152, asn, "provider")

for asn in stub_groupA_isd6:
    cross_connector.XConnect(152, asn, "provider")

# Tier 3 ASes 
#IX: IX26
for asn in stub_groupA_isd6:
    ixp_connector.IXPConnect(26, asn)


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