#!/usr/bin/env python3

from ipaddress import IPv4Network
from seedemu.compiler import Docker, Graphviz
from seedemu.core import Emulator
from seedemu.layers import ScionBase, ScionRouting, ScionIsd, Scion, Ospf, Ibgp, Ebgp, PeerRelationship 
from seedemu.layers.Scion import LinkType as ScLinkType
import examples.scion.utility.utils as utils
import examples.scion.utility.btcd as btcd
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
isd1 = base.createIsolationDomain(1) # NA
isd2 = base.createIsolationDomain(2) # NA Cloud

# Customize names (for visualization purpose)
isd1.setLabel('EU')
isd2.setLabel('EU Cloud')


###############################################################################
# Internet Exchanges
ix20 = base.createInternetExchange(20)
ix21 = base.createInternetExchange(21)
ix22 = base.createInternetExchange(22)
ix23 = base.createInternetExchange(23)
ix29 = base.createInternetExchange(29)

# # Customize names (for visualization purpose)
ix20.getPeeringLan().setDisplayName('Frankfurt-20')
ix21.getPeeringLan().setDisplayName('London-21')
ix22.getPeeringLan().setDisplayName('Amsterdam-22')
ix23.getPeeringLan().setDisplayName('Frankfurt-23')
ix29.getPeeringLan().setDisplayName('EU Cloud-22')



###############################################################################
# Helper
path_checker = utils.PathChecker()
cross_connector = utils.CrossConnector(base, scion_isd, ebgp, scion, path_checker)
ixp_connector = utils.IXPConnector(base, scion_isd, ebgp, scion, path_checker)
maker = utils.AutonomousSystemMaker(base, scion_isd)


###############################################################################
# Europe ISD 1 (100 to 122)
# Tier 1 ASes
arelion = maker.createTier1AS(1, 100)
telecom_italia = maker.createTier1AS(1, 101)
deutsche_telekom = maker.createTier1AS(1, 102)
retn_limited= maker.createTier1AS(1,103)

# Tier 2 ASes
core_backbone = maker.createTier2AS(1, 104, issuer=102) # Issuer: Deutsche Telekom
swisscom = maker.createTier2AS(1, 105, issuer=102) # Issuer: Deutsche Telekom
tele_2 = maker.createTier2AS(1, 106, issuer=102) # Issuer: Deutsche Telekom

# Tier 3 ASes
# 107 - 118
stub_groupA_isd1 = []
for asn in range(107, 119):
    as_ = maker.createTier3AS(1, asn, issuer=102) # Issuer: Deutsche Telekom
    stub_groupA_isd1.append(asn)

# 119 - 122
stub_groupB_isd1 = []
for asn in range(119, 123):
    as_ = maker.createTier3AS(1, asn, issuer=102) # Issuer: Deutsche Telekom
    stub_groupB_isd1.append(asn)


###############################################################################
# Cloud - Europe ISD 2 (123 to 125)
ovh_cloud = maker.createTier1AS(2, 123)
contabo_cloud = maker.createTier1AS(2, 124)
hetzner_cloud = maker.createTier1AS(2, 125)


###############################################################################
# Links
# Arelion 1-100 to 
# Tier1: 1-101, 1-102
# Tier2: 1-104
cross_connector.XConnect(100, 101, "core")
cross_connector.XConnect(100, 102, "core")
cross_connector.XConnect(100, 104, "provider")

# Telecom Italia 1-101 to
# Tier1: 1-102, 1-103
# Tier2: 1-105
cross_connector.XConnect(101, 102, "core")
cross_connector.XConnect(101, 103, "core")
cross_connector.XConnect(101, 105, "provider")

# Deutsche Telekom 1-102 to
# Tier2: 1-106, 1-104
cross_connector.XConnect(102, 106, "provider")
cross_connector.XConnect(102, 104, "provider")

#CLOUD IX
ixp_connector.IXPConnect(29, 123)
ixp_connector.IXPConnect(29, 124)
ixp_connector.IXPConnect(29, 125)
cross_connector.XConnect(123, 100, "core")

# Cloud ovh 2-123 to
# IX20, IX21, IX22
ixp_connector.IXPConnect(20, 123)
ixp_connector.IXPConnect(21, 123)
ixp_connector.IXPConnect(22, 123)

# Cloud Contabo 2-124 to
# IX20, IX21, IX22
ixp_connector.IXPConnect(20, 124)
ixp_connector.IXPConnect(21, 124)
ixp_connector.IXPConnect(22, 124)

# Cloud Hetzner 2-125 to
# IX20, IX21, IX22
ixp_connector.IXPConnect(20, 125)
ixp_connector.IXPConnect(21, 125)
ixp_connector.IXPConnect(22, 125)

# core-Backbone 1-104 to
# IX20, IX21, IX22
ixp_connector.IXPConnect(20, 104)
ixp_connector.IXPConnect(21, 104)
ixp_connector.IXPConnect(22, 104)

# Swisscom 1-105 to
# Tier2: 1-104, 1-106
# IX20, IX21, IX22
cross_connector.XConnect(105, 104, "peer")
cross_connector.XConnect(105, 106, "peer")
ixp_connector.IXPConnect(20, 105)
ixp_connector.IXPConnect(21, 105)
ixp_connector.IXPConnect(22, 105)

# Tele2 1-106 to
# 1-119 until 1-122 (Group B)
for asn in stub_groupB_isd1:
    ixp_connector.addIXLink(23, 106, asn, ScLinkType.Transit)
    ixp_connector.IXPConnect(23, asn)

# Tele2 1-106 to
# 1-107 until 1-118 (Group A)
for asn in stub_groupA_isd1:
    ixp_connector.addIXLink(23, 106, asn, ScLinkType.Transit)
    ixp_connector.IXPConnect(23, asn)


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
#path_checker.deployAndCheck()
path_checker.deploy()