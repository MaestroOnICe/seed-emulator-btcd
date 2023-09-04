#!/usr/bin/env python3
# encoding: utf-8

from seedemu.layers import Base, Routing, Ebgp, PeerRelationship, Ibgp, Ospf
from seedemu.compiler import Docker, Graphviz
from seedemu.core import Emulator
from seedemu.utilities import Makers


# Initialize the emulator and layers
###############################################################################
emu     = Emulator()
base    = Base()
routing = Routing()
ebgp    = Ebgp()
ibgp    = Ibgp()
ospf    = Ospf()

# Create two Internet Exchange
###############################################################################
base.createInternetExchange(100)
base.createInternetExchange(101)
base.createInternetExchange(102)
base.createInternetExchange(103)
base.createInternetExchange(104)
base.createInternetExchange(105)

###############################################################################
# Create Transit Autonomous Systems 

## Tier 1 ASes
Makers.makeTransitAs(base, 2, [100, 101], [(100, 101)])

Makers.makeTransitAs(base, 3, [101, 102], [(101, 102)])

Makers.makeTransitAs(base, 4, [102, 103], [(102, 103)])

Makers.makeTransitAs(base, 5, [103, 100], [(103, 100)])

## Tier 2 ASes
Makers.makeTransitAs(base, 10, [102, 104], [(102, 104)])
Makers.makeTransitAs(base, 11, [100, 105], [(100, 105)])


###############################################################################
# Create single-homed stub ASes. "None" means create a host only 

Makers.makeStubAs(emu, base, 150, 104, [None])
Makers.makeStubAs(emu, base, 151, 104, [None])
Makers.makeStubAs(emu, base, 152, 104, [None])
Makers.makeStubAs(emu, base, 153, 104, [None])


Makers.makeStubAs(emu, base, 160, 105, [None])
Makers.makeStubAs(emu, base, 161, 105, [None])
Makers.makeStubAs(emu, base, 162, 105, [None])
Makers.makeStubAs(emu, base, 163, 105, [None])



# create ASes with btcd node in host
###############################################################################
# for asn, ix in asn_ix.items():
#     as_ = base.createAutonomousSystem(asn)
#     as_.createNetwork("net0")
#     as_.createRouter("br0").joinNetwork("net0").joinNetwork(f"ix{ix}")
#     host = as_.createHost("host").joinNetwork("net0")
#     host.addSharedFolder('/shared/','/home/justus/seed-emulator/examples/scion/S07-btcd-bgp/bin/')
#     host.appendStartCommand("cp /shared/btcd /bin/btcd", False)
#     host.appendStartCommand("chmod +x /bin/btcd", False)
    
#     # import and make script executable, run script is used to spawn btcd 
#     host.importFile('/home/justus/seed-emulator/examples/scion/S07-btcd-bgp/scripts/run.sh', '/run.sh')
#     host.appendStartCommand("chmod +x /run.sh", False)
#     #host.appendStartCommand("./run.sh", True)


###############################################################################
# manually add AS156
# as156 = base.getAutonomousSystem(156)
# as156.getRouter("br0").joinNetwork("ix100")

# manually add blocksafari
###############################################################################
# as156 = base.getAutonomousSystem(156)
# host_156 = as156.getHost("host")
# # add binary, assets and start script
# host_156.addSharedFolder("/blocksafari/", "/home/justus/seed-emulator/examples/scion/S07-btcd-bgp/blocksafari")
# host_156.importFile('/home/justus/seed-emulator/examples/scion/S07-btcd-bgp/scripts/blocksafari.sh', "/blocksafari/blocksafari.sh")
# #host_156.appendStartCommand("./blocksafari/blocksafari.sh", True)
# host_156.addSoftware("net-tools")

# Peering
###############################################################################
# Peering via RS (route server). 
# which means each AS will only export its customers and their own prefixes. 
# We will use this peering relationship to peer all the ASes in an IX.
# None of them will provide transit service for others. 

# Tier 1 peering
ebgp.addRsPeers(100, [2, 5])
ebgp.addRsPeers(101, [2, 3])
ebgp.addRsPeers(102, [3, 4])
ebgp.addRsPeers(103, [4, 5])

# To buy transit services from another autonomous system, 
# we will use private peering
#Tier 1 to Tier 2
ebgp.addPrivatePeerings(102, [3, 4],  [10], PeerRelationship.Provider)
ebgp.addPrivatePeerings(100, [2, 5],  [11], PeerRelationship.Provider)


# Tier 2 to Tier 3 
ebgp.addPrivatePeerings(104, [10],  [150, 151, 152, 153], PeerRelationship.Provider)
ebgp.addPrivatePeerings(105, [11],  [160, 161, 162, 163], PeerRelationship.Provider)


# Rendering 
###############################################################################
emu.addLayer(base)
emu.addLayer(routing)
emu.addLayer(ebgp)
emu.addLayer(ibgp)
emu.addLayer(ospf)

emu.render()

# Compilation
###############################################################################
emu.compile(Docker(), './output', override=True)
emu.compile(Graphviz(), "./output/graphs", override=True)