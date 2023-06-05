#!/usr/bin/env python3
# encoding: utf-8

from seedemu.layers import Base, Routing, Ebgp
from seedemu.services import WebService
from seedemu.compiler import Docker
from seedemu.core import Emulator, Binding, Filter


# Initialize the emulator and layers
emu     = Emulator()
base    = Base()
routing = Routing()
ebgp    = Ebgp()
web     = WebService()

###############################################################################
# Create an Internet Exchange
base.createInternetExchange(100)

###############################################################################
# Create and set up AS-150

as150 = base.createAutonomousSystem(150)
as150.createNetwork('net0')
as150.createRouter('router0').joinNetwork('net0').joinNetwork('ix100')
h01 = as150.createHost('h01').joinNetwork('net0')
h01.addSoftware("screen")
h01.importFile('/home/justus/seed-emulator/examples/scion/S07-btcd-bgp/binary/btcd','/bin/btcd')
h01.importFile('/home/justus/seed-emulator/examples/scion/S07-btcd-bgp/binary/btcwallet','/bin/btcwallet')
h01.importFile('/home/justus/seed-emulator/examples/scion/S07-btcd-bgp/binary/btcctl','/bin/btcctl')
h01.appendStartCommand('chmod +x /bin/btcd', False)
h01.appendStartCommand('chmod +x /bin/btcwallet', False)
h01.appendStartCommand('chmod +x /bin/btcctl', False)

###############################################################################
# Create and set up AS-151

as151 = base.createAutonomousSystem(151)
as151.createNetwork('net0')
as151.createRouter('router0').joinNetwork('net0').joinNetwork('ix100')
h02 = as151.createHost('h02').joinNetwork('net0')
h02.addSoftware("screen")
h02.importFile('/home/justus/seed-emulator/examples/scion/S07-btcd-bgp/binary/btcd','/bin/btcd')
h02.importFile('/home/justus/seed-emulator/examples/scion/S07-btcd-bgp/binary/btcwallet','/bin/btcwallet')
h02.importFile('/home/justus/seed-emulator/examples/scion/S07-btcd-bgp/binary/btcctl','/bin/btcctl')
h02.appendStartCommand('chmod +x /bin/btcd', False)
h02.appendStartCommand('chmod +x /bin/btcwallet', False)
h02.appendStartCommand('chmod +x /bin/btcctl', False)

###############################################################################
# Create and set up AS-152

as152 = base.createAutonomousSystem(152)
as152.createNetwork('net0')
as152.createRouter('router0').joinNetwork('net0').joinNetwork('ix100')
h03 = as152.createHost('h01').joinNetwork('net0')
h03.addSoftware("screen")
h03.importFile('/home/justus/seed-emulator/examples/scion/S07-btcd-bgp/binary/btcd','/bin/btcd')
h03.importFile('/home/justus/seed-emulator/examples/scion/S07-btcd-bgp/binary/btcwallet','/bin/btcwallet')
h03.importFile('/home/justus/seed-emulator/examples/scion/S07-btcd-bgp/binary/btcctl','/bin/btcctl')
h03.appendStartCommand('chmod +x /bin/btcd', False)
h03.appendStartCommand('chmod +x /bin/btcwallet', False)
h03.appendStartCommand('chmod +x /bin/btcctl', False)

###############################################################################
# Peering these ASes at Internet Exchange IX-100

ebgp.addRsPeer(100, 150)
ebgp.addRsPeer(100, 151)
ebgp.addRsPeer(100, 152)


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
