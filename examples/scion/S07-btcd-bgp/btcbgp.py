#!/usr/bin/env python3
# encoding: utf-8

from seedemu.layers import Base, Routing, Ebgp
from seedemu.services import WebService
from seedemu.compiler import Docker, Graphviz
from seedemu.core import Emulator


# Initialize the emulator and layers
emu     = Emulator()
base    = Base()
routing = Routing()
ebgp    = Ebgp()
web     = WebService()

###############################################################################
# Create two Internet Exchange
base.createInternetExchange(100)
base.createInternetExchange(101)

###############################################################################
# Core ASes in ISD 1
asn_ix = {
    150: 100,
    151: 100,
    152: 100,
    153: 100,
    154: 100,
    155: 100,
    156: 101,
    157: 101,
    158: 101,
    159: 101,
    160: 101
}

###############################################################################
# import permission commands
with open("/home/justus/seed-emulator/examples/scion/S07-btcd-bgp/scripts/permissions.sh", 'r') as file:
         permissions = file.read()

###############################################################################
# create ASes with btcd node in host
for asn, ix in asn_ix.items():
    as_ = base.createAutonomousSystem(asn)
    as_.createNetwork("net0")
    as_.createRouter("br0").joinNetwork("net0").joinNetwork(f"ix{ix}")
    host = as_.createHost("host").joinNetwork("net0")
    host.addSharedFolder('/shared/','/home/justus/seed-emulator/examples/scion/S07-btcd-bgp/bin/')
    host.importFile('/home/justus/seed-emulator/examples/scion/S07-btcd-bgp/scripts/run.sh', '/run.sh')
    host.appendStartCommand(permissions, False)

###############################################################################
# manually add AS156
as156 = base.getAutonomousSystem(156)
as156.getRouter("br0").joinNetwork("ix100")

###############################################################################
# Peering these ASes at Internet Exchange IX-100

ebgp.addRsPeer(100, 150)
ebgp.addRsPeer(100, 151)
ebgp.addRsPeer(100, 152)
ebgp.addRsPeer(100, 153)
ebgp.addRsPeer(100, 154)
ebgp.addRsPeer(100, 155)
ebgp.addRsPeer(100, 156)
ebgp.addRsPeer(101, 156)
ebgp.addRsPeer(101, 157)
ebgp.addRsPeer(101, 158)
ebgp.addRsPeer(101, 159)
ebgp.addRsPeer(101, 160)

###############################################################################
# Rendering 

emu.addLayer(base)
emu.addLayer(routing)
emu.addLayer(ebgp)
emu.addLayer(web)

emu.render()

###############################################################################
# Compilation

emu.compile(Docker(), './output', override=True)
