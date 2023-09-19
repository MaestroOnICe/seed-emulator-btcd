#!/usr/bin/env python3
# encoding: utf-8

from seedemu.layers import ScionBase, Routing, Ebgp
from seedemu.compiler import Docker, Graphviz
from seedemu.core import Emulator
from seedemu.utilities import Makers


# Initialize the emulator and layers
###############################################################################
emu     = Emulator()
base    = ScionBase()
routing = Routing()
ebgp    = Ebgp()


as_ = base.createAutonomousSystem(1)
as_.createNetwork("net0")
as_.createRouter("br0").joinNetwork("net0")
host = as_.createHost("host").joinNetwork("net0")
host.importFile("/home/justus/seed-emulator/examples/scion/test/test.txt", "/.btcd/test.txt")

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




# Rendering 
###############################################################################
emu.addLayer(base)
emu.addLayer(routing)
emu.addLayer(ebgp)

emu.render()

# Compilation
###############################################################################
emu.compile(Docker(), './output', override=True)
emu.compile(Graphviz(), "./output/graphs", override=True)