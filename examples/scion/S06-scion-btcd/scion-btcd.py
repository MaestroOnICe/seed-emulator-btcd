#!/usr/bin/env python3

from seedemu.compiler import Docker, Graphviz
from seedemu.core import Emulator
from seedemu.layers import ScionBase, ScionRouting, ScionIsd, Scion
from seedemu.layers.Scion import LinkType as ScLinkType

# Initialize
emu = Emulator()
base = ScionBase()
routing = ScionRouting()
scion_isd = ScionIsd()
scion = Scion()

###############################################################################
# SCION ISDs
base.createIsolationDomain(1)

###############################################################################
# Internet Exchange
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
with open("/home/justus/seed-emulator/examples/scion/S06-btcd/scripts/permissions.sh", 'r') as file:
         permissions = file.read()

###############################################################################
# create ASes with btcd node in host
for asn, ix in asn_ix.items():
    as_ = base.createAutonomousSystem(asn)
    scion_isd.addIsdAs(1, asn, is_core=True)
    as_.createNetwork("net0")
    as_.createControlService("cs1").joinNetwork("net0")
    as_.createRouter("br0").joinNetwork("net0").joinNetwork(f"ix{ix}")
    host = as_.createHost("host").joinNetwork("net0")
    host.addSharedFolder('/shared/','/home/justus/seed-emulator/examples/scion/S06-btcd/bin/')
    host.importFile('/home/justus/seed-emulator/examples/scion/S06-btcd/scripts/run.sh', '/run.sh')
    host.appendStartCommand(permissions, False)

###############################################################################
# add ix connections
as156 = base.getAutonomousSystem(156)
as156.getRouter("br0").joinNetwork("ix100")

###############################################################################
# Inter-AS routing IX 100
scion.addIxLink(100, (1, 150), (1, 151), ScLinkType.Core)
scion.addIxLink(100, (1, 150), (1, 152), ScLinkType.Core)
scion.addIxLink(100, (1, 150), (1, 153), ScLinkType.Core)
scion.addIxLink(100, (1, 150), (1, 154), ScLinkType.Core)
scion.addIxLink(100, (1, 150), (1, 155), ScLinkType.Core)
scion.addIxLink(100, (1, 151), (1, 152), ScLinkType.Core)
scion.addIxLink(100, (1, 151), (1, 153), ScLinkType.Core)
scion.addIxLink(100, (1, 151), (1, 154), ScLinkType.Core)
scion.addIxLink(100, (1, 151), (1, 155), ScLinkType.Core)
scion.addIxLink(100, (1, 152), (1, 153), ScLinkType.Core)
scion.addIxLink(100, (1, 152), (1, 154), ScLinkType.Core)
scion.addIxLink(100, (1, 152), (1, 155), ScLinkType.Core)
scion.addIxLink(100, (1, 153), (1, 154), ScLinkType.Core)
scion.addIxLink(100, (1, 153), (1, 155), ScLinkType.Core)
scion.addIxLink(100, (1, 154), (1, 155), ScLinkType.Core)

# Inter-AS routing IX 101
scion.addIxLink(101, (1, 156), (1, 157), ScLinkType.Core)
scion.addIxLink(101, (1, 156), (1, 158), ScLinkType.Core)
scion.addIxLink(101, (1, 156), (1, 159), ScLinkType.Core)
scion.addIxLink(101, (1, 156), (1, 160), ScLinkType.Core)
scion.addIxLink(101, (1, 157), (1, 158), ScLinkType.Core)
scion.addIxLink(101, (1, 157), (1, 159), ScLinkType.Core)
scion.addIxLink(101, (1, 157), (1, 160), ScLinkType.Core)
scion.addIxLink(101, (1, 158), (1, 159), ScLinkType.Core)
scion.addIxLink(101, (1, 158), (1, 160), ScLinkType.Core)
scion.addIxLink(101, (1, 159), (1, 160), ScLinkType.Core)
scion.addIxLink(100, (1, 150), (1, 156), ScLinkType.Core)


###############################################################################
# Rendering
emu.addLayer(base)
emu.addLayer(routing)
emu.addLayer(scion_isd)
emu.addLayer(scion)

emu.render()

# Compilation
emu.compile(Docker(), "./output", override=True)
emu.compile(Graphviz(), "./output/graphs", override=True)