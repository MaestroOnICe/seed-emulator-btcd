#!/usr/bin/env python3

from seedemu.compiler import Docker, Graphviz
from seedemu.core import Emulator
from seedemu.layers import ScionBase, ScionRouting, ScionIsd, Scion, Ebgp
from seedemu.layers.Scion import LinkType as ScLinkType
import examples.scion.utility.utils as utils
import examples.scion.utility.bitcoin as bitcoin
import examples.scion.utility.experiment as experiment
import time

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
ix23 = base.createInternetExchange(23) # Frankfurt2 (Europe)
ix24 = base.createInternetExchange(24) # Singapore (Asia)
ix25 = base.createInternetExchange(25) # Accra (Africa)
ix26 = base.createInternetExchange(26) # Sao Paulo (South America)
#ix27 = base.createInternetExchange(27) # Los Angeles (North America)
ix28 = base.createInternetExchange(28) # Miami (North America)
ix29 = base.createInternetExchange(29) # EU Cloud
ix30 = base.createInternetExchange(30) # NA Cloud


# Customize names (for visualization purpose)
ix20.getPeeringLan().setDisplayName('Frankfurt-20')
ix21.getPeeringLan().setDisplayName('London-21')
ix22.getPeeringLan().setDisplayName('Amsterdam-22')
ix23.getPeeringLan().setDisplayName('Frankfurt2-23')
ix24.getPeeringLan().setDisplayName('Singapore-24')
ix25.getPeeringLan().setDisplayName('Accra-25')
ix26.getPeeringLan().setDisplayName('Sao Paulo-26')
#ix27.getPeeringLan().setDisplayName('Los Angeles-27')
ix28.getPeeringLan().setDisplayName('Miami-28')
ix29.getPeeringLan().setDisplayName('EU Cloud-29')
ix30.getPeeringLan().setDisplayName('NA Cloud-30')


###############################################################################
# Helper
path_checker = utils.PathChecker()
cross_connector = utils.CrossConnector(base, scion_isd, ebgp, scion, path_checker)
ixp_connector = utils.IXPConnector(base, scion_isd, ebgp, scion, path_checker)
maker = utils.AutonomousSystemMaker(base, scion_isd)
btcd = bitcoin.btcd(scion_isd)

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
# Asia ISD 3 (126 to 138)
# Tier 1 ASes
telstra = maker.createTier1AS(3, 126)
singapore_telecommunication = maker.createTier1AS(3, 127)

# Tier 2 ASes
microscan = maker.createTier2AS(3, 128, issuer=126) # Issuer: Telstra
tm_technology = maker.createTier2AS(3, 129, issuer=126) # Issuer: Telstra
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
# 143 - 149
stub_groupA_isd5 = []
for asn in range(143, 150):
    as_ = maker.createTier3AS(5, asn, issuer=140) # Issuer: Angola Cables
    stub_groupA_isd5.append(asn)


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
# Tier2: 1-106
# IX20, IX21, IX22
#cross_connector.XConnect(105, 104, "peer")
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
# Intra-ISD Links


# EUROPE ISD 1 and EU CLOUD ISD 2
#############

# ASIA, ISD 3 and ASIA CLOUD ISD 4
#############

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
# Tier3: 3-131 to 3-135
cross_connector.XConnect(128, 130, "provider")
for asn in stub_groupA_isd3:
    ixp_connector.addIXLink(24, 128, asn, ScLinkType.Transit)

# Kinx 3-130 to
# Tier2: 3-129
# IX: IX24
cross_connector.XConnect(130, 129, "peer")
ixp_connector.IXPConnect(24, 130)

# TM Technology 3-129 to
# Tier3: 3-136 to 3-138
# IX: IX24
ixp_connector.IXPConnect(24, 129)
for asn in stub_groupB_isd3:
    cross_connector.XConnect(129, asn, "provider")

# Alibaba 4-139 to
# Tier2: 3-129
cross_connector.XConnect(139, 129, "provider")

# Stub Group A
# IX: IX24
for asn in stub_groupA_isd3:
    ixp_connector.IXPConnect(24, asn)


# AFRICA ISD 5
#############

# Angola Cables 5-140
# Tier2: 5-142, 5-141
cross_connector.XConnect(140, 141, "provider")
cross_connector.XConnect(140, 142, "provider")

# Ecoband 5-141
# IX: IX25
ixp_connector.IXPConnect(25, 141)

# Africom 5-142
# IX: IX25
#ixp_connector.IXPConnect(25, 142)
for asn in stub_groupA_isd5:
    ixp_connector.addIXLink(25, 142, asn, ScLinkType.Transit)

# Tier3 ASes in ISD 5
# IX: IX2025
for asn in stub_groupA_isd5:
    ixp_connector.IXPConnect(25, asn)


# SOUTH AMERICA ISD 6
#############

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

# Tier 3 ASes Group A
#IX: IX26
for asn in stub_groupA_isd6:
    ixp_connector.IXPConnect(26, asn)


# NORTH AMERICA ISD 7 and NA CLOUD ISD 8
#############

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
# Inter ISD Links


# Arelion 1-100 to
# Tier1: 7-161
cross_connector.XConnect(100, 161, "core")

# Telecom Italia 1-101 to
# Tier1: 7-162
cross_connector.XConnect(101, 162, "core")

# RETN 1-103 to
# Tier1: 3-127
cross_connector.XConnect(103, 127, "core")

# Telstra 3-126 to
# Tier1: 7-160
cross_connector.XConnect(126, 160, "core")

# Singapore Communication 3-127 to
# Tier1: 5-140
cross_connector.XConnect(127, 140, "core")

# Angola Cables 5-140 to
# Tier1: 1-102, 6-150
# IX: IX26
cross_connector.XConnect(140, 102, "core")
cross_connector.XConnect(140, 150, "core")
#ixp_connector.IXPConnect(26, 140)

# GlobeNet 6-151 to
# Tier1: 7-162
cross_connector.XConnect(151, 162, "core")

# GlobeNet 6-150 to
# Tier1: 7-162
cross_connector.XConnect(150, 162, "core")



###############################################################################
# Bitcoin node Placement
# 48 Nodes in total
# 24 in Stub ASes and 24 in the Cloud

# Bootstrap Nodes
# EU Node 10.124.0.200
btcd.createBootstrap(contabo_cloud) #124-103

# Asia Node 10.139.0.200
btcd.createBootstrap(alibab_cloud) #139-101

# NA Node 10.177.0.200
btcd.createBootstrap(google_cloud) #177-103

# Cloud EU
btcd.createNode(ovh_cloud) #123-100
btcd.createNode(ovh_cloud) #123-101
btcd.createNode(ovh_cloud) #123-102
btcd.createNode(ovh_cloud) #123-103

btcd.createNode(contabo_cloud) #124-100
btcd.createNode(contabo_cloud) #124-101
btcd.createNode(contabo_cloud) #124-102

btcd.createNode(hetzner_cloud) #125-100
btcd.createNode(hetzner_cloud) #125-101
btcd.createNode(hetzner_cloud) #125-102
btcd.createNode(hetzner_cloud) #125-103
btcd.createNode(hetzner_cloud) #125-104

# Cloud Asia
btcd.createNode(alibab_cloud) # 139-100

# Cloud NA
btcd.createNode(aws_cloud) # 176-100
btcd.createNode(aws_cloud) # 176-101
btcd.createNode(aws_cloud) # 176-102

btcd.createNode(google_cloud) # 177-100
btcd.createNode(google_cloud) # 177-101
btcd.createNode(google_cloud) # 177-102

btcd.createNode(digital_ocean_cloud) # 178-100
btcd.createNode(digital_ocean_cloud) # 178-101


# In the stubs, every seconds AS has a node
# Stub EU
counter = 1
for asn in stub_groupA_isd1:
    if counter % 2 == 0:
        as_ = base.getAutonomousSystem(asn)
        btcd.createNode(as_)
        counter += 1
    else:
        counter += 1

for asn in stub_groupB_isd1:
    if counter % 2 == 0:
        as_ = base.getAutonomousSystem(asn)
        btcd.createNode(as_)
        counter += 1
    else:
        counter += 1

# Stub Asia
for asn in stub_groupA_isd3:
    if counter % 2 == 0:
        as_ = base.getAutonomousSystem(asn)
        btcd.createNode(as_)
        counter += 1
    else:
        counter += 1

for asn in stub_groupB_isd3:
    if counter % 2 == 0:
        as_ = base.getAutonomousSystem(asn)
        btcd.createNode(as_)
        counter += 1
    else:
        counter += 1

# Stub Africa
for asn in stub_groupA_isd5:
    if counter % 2 == 0:
        as_ = base.getAutonomousSystem(asn)
        btcd.createNode(as_)
        counter += 1
    else:
        counter += 1

# Stub South America
for asn in stub_groupA_isd6:
    if counter % 2 == 0:
        as_ = base.getAutonomousSystem(asn)
        btcd.createNode(as_)
        counter += 1
    else:
        counter += 1

for asn in stub_groupB_isd6:
    if counter % 2 == 0:
        as_ = base.getAutonomousSystem(asn)
        btcd.createNode(as_)
        counter += 1
    else:
        counter += 1

# Stub North America
for asn in stub_groupA_isd7:
    if counter % 2 == 0:
        as_ = base.getAutonomousSystem(asn)
        btcd.createNode(as_)
        counter += 1
    else:
        counter += 1

for asn in stub_groupB_isd7:
    if counter % 2 == 0:
        as_ = base.getAutonomousSystem(asn)
        btcd.createNode(as_)
        counter += 1
    else:
        counter += 1


###############################################################################
# Rendering
ixp_connector.addScionIXPConnections()
emu.addLayer(base)
emu.addLayer(routing)
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
path_checker.deploy()

###############################################################################
# Experiment

print("Sleeping for 120 seconds until hijack")
time.sleep(120)

print("Hijacking AS, sleeping for 5 minutes")
# attacker, victim
experiment.hijackAS(139, 125)
time.sleep(300)

experiment.endHijack(139)
print("Hijack ended, sleep for another 120 seconds")
time.sleep(120)

experiment.down()