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


###############################################################################
# Helper
path_checker = utils.PathChecker()
cross_connector = utils.CrossConnector(base, scion_isd, ebgp, scion, path_checker)
ixp_connector = utils.IXPConnector(base, scion_isd, ebgp, scion, path_checker)
maker = utils.AutonomousSystemMaker(base, scion_isd)


###############################################################################
# Europe ISD 1
# Tier 1 ASes
arelion = maker.createTier1AS(1, 100)
# Tier 2 ASes
#swisscom = maker.createTier2AS(1, 101, issuer=100) # Issuer: Arelion


# Asia ISD 2
# Tier 1 ASes
telstra = maker.createTier1AS(2, 150)
# Tier 2 ASes
#microscan = maker.createTier2AS(2, 151, issuer=150) # Issuer: Telstra


###############################################################################
# Links
#cross_connector.XConnect(100, 150, "core")

ixp_connector.IXPConnect(20, 100)
ixp_connector.IXPConnect(20, 150)

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