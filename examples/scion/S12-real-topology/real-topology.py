#!/usr/bin/env python3

from ipaddress import IPv4Network
from seedemu.compiler import Docker, Graphviz
from seedemu.core import Emulator
from seedemu.layers import ScionBase, ScionRouting, ScionIsd, Scion, Ospf, Ebgp, PeerRelationship 
from seedemu.layers.Scion import LinkType as ScLinkType
import examples.scion.utility.utils as utils


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
stub_groupA_isd1 = {}
for asn in range(107, 119):
    as_ = maker.createTier3AS(1, asn, issuer=102) # Issuer: Deutsche Telekom
    stub_groupA_isd1[asn] = as_

stub_groupB_isd1 = {}
for asn in range(119, 123):
    as_ = maker.createTier3AS(1, asn, issuer=102) # Issuer: Deutsche Telekom
    stub_groupB_isd1[asn] = as_


###############################################################################
# Cloud - Europe ISD 2 (123 to 125)
ovh_cloud = maker.createTier1AS(2, 123)
contabo_cloud = maker.createTier1AS(2, 124)
hetzner_cloud = maker.createTier1AS(2, 125)


###############################################################################
# Asia ISD 3 (126 to 138)
# Tier 1 ASes
telstra = maker.createTier1AS(3, 126)
singapore_telecommunication = maker.createTier1AS(3, 127)

# Tier 2 ASes
microscan = maker.createTier2AS(3, 128, issuer=126) # Issuer: Telstra
tm_technology = maker.createTier2AS(3, 129, issuer=126) # Issuer: Telstra
kinx = maker.createTier2AS(3, 130, issuer=126) # Issuer: Telstra

# Tier 3 ASes
stub_groupA_isd3 = {}
for asn in range(131, 136):
    as_ = maker.createTier3AS(3, asn, issuer=126) # Issuer: Telstra
    stub_groupA_isd3[asn] = as_

stub_groupB_isd3 = {}
for asn in range(136, 139):
    as_ = maker.createTier3AS(3, asn, issuer=126) # Issuer: Telstra
    stub_groupB_isd3[asn] = as_


###############################################################################
# Cloud - Asia ISD 4 (139)
alibab_cloud = maker.createTier1AS(4, 139)


###############################################################################
# Africa ISD 5 (140 to 149)
# Tier 1 ASes
angola_cables = maker.createTier1AS(5, 140)

# Tier 2 ASes
ecoband = maker.createTier2AS(5, 141, issuer=140) # Issuer: Angola Cables
africom = maker.createTier2AS(5, 142, issuer=140) # Issuer: Angola Cables

# Tier 3 ASes
stub_groupA_isd5 = {}
for asn in range(143, 150):
    as_ = maker.createTier3AS(5, asn, issuer=140) # Issuer: Angola Cables
    stub_groupA_isd5[asn] = as_


###############################################################################
# South America ISD 6 (150 to 159)
# Tier 1 ASes
algar_telecomm = maker.createTier1AS(6, 150)
globe_net = maker.createTier1AS(6, 151)

# Tier 2 ASes
locaweb = maker.createTier2AS(6, 152, issuer=150)

# Tier 3 ASes
stub_groupA_isd6 = {}
for asn in range(153, 156):
    as_ = maker.createTier3AS(6, asn, issuer=150) # Issuer: Algar Telecomm
    stub_groupA_isd6[asn] = as_

stub_groupB_isd6 = {}
for asn in range(156, 160):
    as_ = maker.createTier3AS(6, asn, issuer=150) # Issuer: Algar Telecomm
    stub_groupB_isd6[asn] = as_

###############################################################################
# North America ISD 7 (160 to 175 )
# Tier 1 ASes
level_3 = maker.createTier1AS(7, 160)
cogent = maker.createTier1AS(7, 161)
verizon = maker.createTier1AS(7, 162)

# Tier 2 ASes
liquidweb = maker.createTier2AS(7, 163, issuer=160)
lunavi = maker.createTier2AS(7, 164, issuer=160)

# Tier 3 ASes
stub_groupA_isd7 = {}
for asn in range(165, 170):
    as_ = maker.createTier3AS(7, asn, issuer=160) # Issuer: level3
    stub_groupA_isd7[asn] = as_

stub_groupB_isd7 = {}
for asn in range(170, 176):
    as_ = maker.createTier3AS(7, asn, issuer=160) # Issuer: level3
    stub_groupB_isd7[asn] = as_

###############################################################################
# Cloud - North America ISD 8 (176 to 178)
# Tier 1 ASes
aws_cloud = maker.createTier1AS(8, 176)
google_cloud = maker.createTier1AS(8, 177)
digital_ocean_cloud = maker.createTier1AS(8, 178)


###############################################################################
# Links originating in Tier 1 ASes

# Arelion 1-100 to 
# Tier1: 1-101, 1-102, 7-161, 
# Tier2: 1-104
cross_connector.XConnect(100, 101, "core")
cross_connector.XConnect(100, 102, "core")
cross_connector.XConnect(100, 161, "core")
cross_connector.XConnect(100, 104, "provider")

# Telecom Italia 1-101 to 
# Tier1: 1-102, 1-103, 7-162
# Tier2: 1-105
cross_connector.XConnect(101, 102, "core")
cross_connector.XConnect(101, 103, "core")
cross_connector.XConnect(101, 162, "core")
cross_connector.XConnect(101, 105, "peer")

# Deutsche Telekom 1-102 to 
# Tier1: 5-140
# Tier2: 1-106, 1-104
cross_connector.XConnect(102, 140, "core")
cross_connector.XConnect(102, 106, "provider")
cross_connector.XConnect(102, 164, "provider")

# RETN Limited 1-103 to 
# Tier1: 3-127
cross_connector.XConnect(103, 127, "core")

# Cloud ovh 2-123 to
# IX100, IX101, IX102
ixp_connector.IXPConnect(100, 123)
ixp_connector.IXPConnect(101, 123)
ixp_connector.IXPConnect(102, 123)

# Cloud Contabo 2-124 to
# IX100, IX101, IX102
ixp_connector.IXPConnect(100, 124)
ixp_connector.IXPConnect(101, 124)
ixp_connector.IXPConnect(102, 124)

# Cloud Hetzner 2-125 to
# IX100, IX101, IX102
ixp_connector.IXPConnect(100, 125)
ixp_connector.IXPConnect(101, 125)
ixp_connector.IXPConnect(102, 125)

# Singapore Telecommunication 3-127 to 
# Tier1: 3-126, 5-140
# Tier2: 3-128, 3-129
cross_connector.XConnect(127, 126, "core")
cross_connector.XConnect(127, 140, "core")
cross_connector.XConnect(127, 128, "provider")
cross_connector.XConnect(127, 129, "provider")

# Telstra 3-126 to 
# Tier1: 7-160
# Tier2: 3-129
cross_connector.XConnect(126, 160, "core")
cross_connector.XConnect(126, 129, "provider")

# Cloud Alibaba 3-139 to 
# ix103 and ix104
ixp_connector.IXPConnect(103, 139)
ixp_connector.IXPConnect(104, 139)

# Angola Cable 5-140 to 
# Tier1: 6-150
# Tier2: 1-104, 5-141, 5-142
cross_connector.XConnect(140, 150, "core")
cross_connector.XConnect(140, 104, "peer")
cross_connector.XConnect(140, 141, "provider")
cross_connector.XConnect(140, 142, "provider")

# Algar Telecom 6-150 to 
# Tier1: 6-151, 7-162
cross_connector.XConnect(150, 151, "core")
cross_connector.XConnect(150, 162, "core")

# GlobeNet 6-151 to 
# Tier1: 7-162
# Tier2: 6-152
cross_connector.XConnect(151, 162, "core")
cross_connector.XConnect(151, 152, "provider")

# Level3 7-160 to 
# Tier1: 7-161, 7-162
# Tier2: 1-104, 7-164
cross_connector.XConnect(160, 161, "core")
cross_connector.XConnect(160, 162, "core")
cross_connector.XConnect(160, 104, "provider")
cross_connector.XConnect(160, 164, "provider")

# Cogent 7-161 to 
# Tier1: 7-162
# Tier2: 1-104
cross_connector.XConnect(161, 162, "core")
cross_connector.XConnect(161, 104, "provider")

# Verizon 7-162 to 
# Tier2: 7-163
cross_connector.XConnect(162, 163, "provider")

# AWS Cloud 8-176 to
# IX107, IX108
ixp_connector.IXPConnect(107, 176)
ixp_connector.IXPConnect(108, 176)

# Google Cloud 8-177 to
# IX107, IX108
ixp_connector.IXPConnect(107, 177)
ixp_connector.IXPConnect(108, 177)

# Digital Ocean 8-178 to 
# Tier2:  Liquidweb 7-163
# IX108
cross_connector.XConnect(178, 163, "peer")
ixp_connector.IXPConnect(108, 178)

###############################################################################
# Links originating in Tier 2 ASes

# core-Backbone 1-104 to
# Tier2: 5-141
# IX100, IX101, IX101
cross_connector.XConnect(104, 141, "peer")
ixp_connector.IXPConnect(100, 104)
ixp_connector.IXPConnect(101, 104)
ixp_connector.IXPConnect(102, 104)
ixp_connector.IXPConnect(107, 104)

# Swisscom 1-105 to
# Tier2: 1-104, 1-106
# IX100, IX101, IX101
cross_connector.XConnect(105, 104, "peer")
cross_connector.XConnect(105, 106, "peer")
ixp_connector.IXPConnect(100, 105)
ixp_connector.IXPConnect(101, 105)
ixp_connector.IXPConnect(102, 105)

# Microscan 3-128 to
# Tier2: 3-130
cross_connector.XConnect(128, 130, "peer")

# TM Techbology 3-129 to
# IX103, IX104
ixp_connector.IXPConnect(103, 129)
ixp_connector.IXPConnect(104, 129)

# Kinx 3-130 to
# Tier2: 3-129
cross_connector.XConnect(130, 129, "peer")

# Ecoband 5-141 to
# Tier2: 5-142
# IX 105
cross_connector.XConnect(141, 142, "peer")
ixp_connector.IXPConnect(105, 141)

# Africom 5-142 to
# IX 105
ixp_connector.IXPConnect(105, 142)

# locaweb 6-152 to
# IX106
ixp_connector.IXPConnect(106, 152)

# liquidweb 7-163 to
# Tier2: 7-164
# IX108
cross_connector.XConnect(163, 164, "peer")
ixp_connector.IXPConnect(108, 163)

# lunavi 7-164 to
# IX107, IX108
ixp_connector.IXPConnect(107, 164)
ixp_connector.IXPConnect(108, 164)


###############################################################################
# Rendering
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