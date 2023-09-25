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
isd7 = base.createIsolationDomain(7) # NA
isd8 = base.createIsolationDomain(8) # NA Cloud

# Customize names (for visualization purpose)
isd7.setLabel('North America')
isd8.setLabel('North America Cloud')


###############################################################################
# Internet Exchanges
#ix27 = base.createInternetExchange(27) 
ix28 = base.createInternetExchange(28)
ix30 = base.createInternetExchange(30)  


# # Customize names (for visualization purpose)
ix28.getPeeringLan().setDisplayName('Miami-28')
ix30.getPeeringLan().setDisplayName('NA Cloud-30')


###############################################################################
# Helper
path_checker = utils.PathChecker()
cross_connector = utils.CrossConnector(base, scion_isd, ebgp, scion, path_checker)
ixp_connector = utils.IXPConnector(base, scion_isd, ebgp, scion, path_checker)
maker = utils.AutonomousSystemMaker(base, scion_isd)


###############################################################################
# North America ISD 7 (160 to 175 )
# Tier 1 ASes
level_3 = maker.createTier1AS(7, 160)
cogent = maker.createTier1AS(7, 161)
verizon = maker.createTier1AS(7, 162)

# Tier 2 ASes
liquidweb = maker.createTier2AS(7, 163, issuer=160)
lunavi = maker.createTier2AS(7, 164, issuer=160)
t_mobile = maker.createTier2AS(7, 165, issuer=160)

# Tier 3 ASes
# 166 - 169
stub_groupA_isd7 = []
for asn in range(166, 170):
    as_ = maker.createTier3AS(7, asn, issuer=160) # Issuer: level3
    stub_groupA_isd7.append(asn)

# 170 - 175
stub_groupB_isd7 = []
for asn in range(170, 176):
    as_ = maker.createTier3AS(7, asn, issuer=160) # Issuer: level3
    stub_groupB_isd7.append(asn)

###############################################################################
# Cloud - North America ISD 8 (176 to 178)
# Tier 1 ASes
aws_cloud = maker.createTier1AS(8, 176)
google_cloud = maker.createTier1AS(8, 177)
digital_ocean_cloud = maker.createTier1AS(8, 178)


###############################################################################
# Links

# Level3 7-160 to 
# Tier1: 7-161, 7-162
# Tier2: 7-164, 7-165
cross_connector.XConnect(160, 161, "core")
cross_connector.XConnect(160, 162, "core")
cross_connector.XConnect(160, 164, "provider")
cross_connector.XConnect(160, 165, "provider")

# Cogent 7-161 to 
# Tier1: 7-162
cross_connector.XConnect(161, 162, "core")

# Verizon 7-162 to 
# Tier2: 7-163
cross_connector.XConnect(162, 163, "provider")

#NA CLOUD IX30
ixp_connector.IXPConnect(30, 176)
ixp_connector.IXPConnect(30, 177)
ixp_connector.IXPConnect(30, 178)
cross_connector.XConnect(176, 160, "core")

# AWS Cloud 8-176 to
# IX27, IX28
ixp_connector.IXPConnect(28, 176)

# Google Cloud 8-177 to
# IX27, IX28
ixp_connector.IXPConnect(28, 177)

# Digital Ocean 8-178 to 
# IX28
ixp_connector.IXPConnect(28, 178)

# liquidweb 7-163 to
# Tier2: 7-164
# Tier3: 7-165 until 7-169
# IX28
cross_connector.XConnect(163, 164, "peer")
for asn in stub_groupA_isd7:
    cross_connector.XConnect(163, asn, "provider")
ixp_connector.IXPConnect(28, 163)

# lunavi 7-164 to
# Tier3: 7-166 until 7-169
# IX28
for asn in stub_groupA_isd7:
    cross_connector.XConnect(164, asn, "provider")
ixp_connector.IXPConnect(28, 164)

# T-Mobile 7-165 to
# Tier3: 7-170 until 7-175
# IX: IX28
for asn in stub_groupB_isd7:
    cross_connector.XConnect(165, asn, "provider")
ixp_connector.IXPConnect(28, 165)

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