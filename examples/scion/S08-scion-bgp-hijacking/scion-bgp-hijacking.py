#!/usr/bin/env python3

from seedemu.compiler import Docker, Graphviz
from seedemu.core import Emulator
from seedemu.layers import ScionBase, ScionRouting, ScionIsd, Scion, Ospf, Ibgp, Ebgp, PeerRelationship
from seedemu.layers.Scion import LinkType as ScLinkType

# Initialize
emu = Emulator()
base = ScionBase()
routing = ScionRouting()
ospf = Ospf()
scion_isd = ScionIsd()
scion = Scion()
ibgp = Ibgp()
ebgp = Ebgp()

###############################################################################
# SCION ISDs
base.createIsolationDomain(1)
base.createIsolationDomain(2)

###############################################################################
# Internet Exchanges
base.createInternetExchange(100)
base.createInternetExchange(101)
base.createInternetExchange(102)

###############################################################################
# Core AS 1-150
as150 = base.createAutonomousSystem(150)
scion_isd.addIsdAs(1, 150, is_core=True)
as150.createNetwork('net0')
as150.createControlService('cs1').joinNetwork('net0')
as150_br0 = as150.createRouter('br0')
as150_br1 = as150.createRouter('br1')
as150_br0.joinNetwork('net0').joinNetwork('ix100')
as150_br1.joinNetwork('net0').joinNetwork('ix102')

###############################################################################
# Core AS 2-160
as160 = base.createAutonomousSystem(160)
scion_isd.addIsdAs(2, 160, is_core=True)
as160.createNetwork('net0')
as160.createControlService('cs1').joinNetwork('net0')
as160_br0 = as160.createRouter('br0')
as160_br1 = as160.createRouter('br1')
as160_br0.joinNetwork('net0').joinNetwork('ix101')
as160_br1.joinNetwork('net0').joinNetwork('ix102')

###############################################################################
# Non-core ASes in ISD 1
isd1_asn_ix = {
    151: 100,
    152: 100,
}

for asn, ix in isd1_asn_ix.items():
    as_ = base.createAutonomousSystem(asn)
    scion_isd.addIsdAs(1, asn, is_core=False)
    scion_isd.setCertIssuer((1, asn), issuer=150)
    as_.createNetwork('net0')
    as_.createControlService('cs1').joinNetwork('net0')
    as_.createRouter('br0').joinNetwork('net0').joinNetwork(f'ix{ix}')


###############################################################################
# Non-core ASes in ISD 2
isd2_asn_ix = {
    161: 101,
    162: 101,
}

for asn, ix in isd2_asn_ix.items():
    as_ = base.createAutonomousSystem(asn)
    scion_isd.addIsdAs(2, asn, is_core=False)
    scion_isd.setCertIssuer((2, asn), issuer=160)
    as_.createNetwork('net0')
    as_.createControlService('cs1').joinNetwork('net0')
    as_.createRouter('br0').joinNetwork('net0').joinNetwork(f'ix{ix}')


###############################################################################
# SCION links
scion.addIxLink(102, (1, 150), (2, 160), ScLinkType.Core)
scion.addIxLink(100, (1, 150), (1, 151), ScLinkType.Transit)
scion.addIxLink(100, (1, 150), (1, 152), ScLinkType.Transit)
scion.addIxLink(101, (2, 160), (2, 161), ScLinkType.Transit)
scion.addIxLink(101, (2, 160), (2, 161), ScLinkType.Transit)


###############################################################################
# BGP peering
ebgp.addPrivatePeering(102, 150, 160, abRelationship=PeerRelationship.Peer)
ebgp.addPrivatePeering(100, 150, 151, abRelationship=PeerRelationship.Provider)
ebgp.addPrivatePeering(100, 150, 152, abRelationship=PeerRelationship.Provider)
ebgp.addPrivatePeering(101, 160, 161, abRelationship=PeerRelationship.Provider)
ebgp.addPrivatePeering(101, 160, 162, abRelationship=PeerRelationship.Provider)


###############################################################################
# Rendering
emu.addLayer(base)
emu.addLayer(routing)
emu.addLayer(ospf)
emu.addLayer(scion_isd)
emu.addLayer(scion)
emu.addLayer(ibgp)
emu.addLayer(ebgp)

emu.render()


# Compilation
emu.compile(Docker(), "./output", override=True)
emu.compile(Graphviz(), "./output/graphs", override=True)