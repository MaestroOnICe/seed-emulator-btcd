#!/usr/bin/env python3
# encoding: utf-8

from seedemu.layers import Base, Routing, Ebgp
from seedemu.services import WebService
from seedemu.compiler import Docker, Graphviz
from seedemu.core import Emulator, Binding, Filter


# Initialize the emulator and layers
###############################################################################
emu     = Emulator()
base    = Base()
routing = Routing()
ebgp    = Ebgp()
web     = WebService()

# Create two Internet Exchange
###############################################################################
base.createInternetExchange(100)
base.createInternetExchange(101)

# Core ASes in ISD 1
###############################################################################
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

# create ASes with btcd node in host
###############################################################################
for asn, ix in asn_ix.items():
    as_ = base.createAutonomousSystem(asn)
    as_.createNetwork("net0")
    as_.createRouter("br0").joinNetwork("net0").joinNetwork(f"ix{ix}")
    host = as_.createHost("host").joinNetwork("net0")
    host.addSharedFolder('/shared/','/home/justus/seed-emulator/examples/scion/S07-btcd-bgp/bin/')
    host.appendStartCommand("cp /shared/btcd /bin/btcd", False)
    host.appendStartCommand("chmod +x /bin/btcd", False)
    
    # import and make script executable, run script is used to spawn btcd 
    host.importFile('/home/justus/seed-emulator/examples/scion/S07-btcd-bgp/scripts/run.sh', '/run.sh')
    host.appendStartCommand("chmod +x /run.sh", False)
    #host.appendStartCommand("./run.sh", True)


###############################################################################
# manually add AS156
as156 = base.getAutonomousSystem(156)
as156.getRouter("br0").joinNetwork("ix100")

# manually add blocksafari
###############################################################################
as156 = base.getAutonomousSystem(156)
host_156 = as156.getHost("host")

# add binary, assets and start script
host_156.addSharedFolder("/blocksafari/", "/home/justus/seed-emulator/examples/scion/S07-btcd-bgp/blocksafari")
host_156.importFile('/home/justus/seed-emulator/examples/scion/S07-btcd-bgp/scripts/blocksafari.sh', "/blocksafari/blocksafari.sh")
#host_156.appendStartCommand("./blocksafari/blocksafari.sh", True)
host_156.addSoftware("net-tools")

#testing
###############################################################################
as157 = base.getAutonomousSystem(157)
host_157 = as157.createHost("web").joinNetwork("net0")
host_157.addSoftware("net-tools")
web.install("web157")

# Bind the virtual node to a physical node 
emu.addBinding(Binding("web157", filter = Filter(nodeName = "web", asn = 157)))


# Peering these ASes at Internet Exchange IX-100
###############################################################################
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

# Rendering 
###############################################################################
emu.addLayer(base)
emu.addLayer(routing)
emu.addLayer(ebgp)
emu.addLayer(web)

emu.render()

# Compilation
###############################################################################
emu.compile(Docker(), './output', override=True)
