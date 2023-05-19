#!/usr/bin/env python3

from seedemu.compiler import Docker
from seedemu.core import Emulator, Binding, Filter
from seedemu.layers import ScionBase, ScionRouting, ScionIsd, Scion
from seedemu.layers.Scion import LinkType as ScLinkType

# Initialize
emu = Emulator()
base = ScionBase()
routing = ScionRouting()
scion_isd = ScionIsd()
scion = Scion()

# SCION ISDs
base.createIsolationDomain(1)

# Internet Exchange
base.createInternetExchange(100)

# AS-150
as150 = base.createAutonomousSystem(150)
scion_isd.addIsdAs(1, 150, is_core=True)
as150.createNetwork('net0')
as150.createControlService('cs1').joinNetwork('net0')
as150_router = as150.createRouter('br0')
as150_router.joinNetwork('net0').joinNetwork('ix100')
as150_router.crossConnect(153, 'br0', '10.50.0.2/29')

# AS-150 - create h01 with btcd installed
as150.createHost('h01').joinNetwork('net0')
h01 = as150.getHost('h01')
h01.importFile('/home/justus/seed-emulator/examples/scion/S06-btcd/bin/btcd','/bin/btcd')
h01.importFile('/home/justus/seed-emulator/examples/scion/S06-btcd/bin/btcwallet','/bin/btcwallet')
h01.appendStartCommand('chmod +x /bin/btcd', False)
h01.appendStartCommand('chmod +x /bin/btcwallet', False)

# AS-151
as151 = base.createAutonomousSystem(151)
scion_isd.addIsdAs(1, 151, is_core=True)
as151.createNetwork('net0')
as151.createControlService('cs1').joinNetwork('net0')
as151.createRouter('br0').joinNetwork('net0').joinNetwork('ix100')

# AS-151 - create h02 with btcd installed
h02 = as151.createHost('h02').joinNetwork('net0')
h02.importFile('/home/justus/seed-emulator/examples/scion/S06-btcd/bin/btcd','/bin/btcd')
h02.importFile('/home/justus/seed-emulator/examples/scion/S06-btcd/bin/btcwallet','/bin/btcwallet')
h02.appendStartCommand('chmod +x /bin/btcd', False)
h02.appendStartCommand('chmod +x /bin/btcwallet', False)


# AS-152
as152 = base.createAutonomousSystem(152)
scion_isd.addIsdAs(1, 152, is_core=True)
as152.createNetwork('net0')
as152.createControlService('cs1').joinNetwork('net0')
as152.createRouter('br0').joinNetwork('net0').joinNetwork('ix100')

# AS-153
as153 = base.createAutonomousSystem(153)
scion_isd.addIsdAs(1, 153, is_core=False)
scion_isd.setCertIssuer((1, 153), issuer=150)
as153.createNetwork('net0')
as153.createControlService('cs1').joinNetwork('net0')
as153_router = as153.createRouter('br0')
as153_router.joinNetwork('net0')
as153_router.crossConnect(150, 'br0', '10.50.0.3/29')

# AS-153 - create h03 with btcd installed
h03 = as153.createHost('h03').joinNetwork('net0')
h03.importFile('/home/justus/seed-emulator/examples/scion/S06-btcd/bin/btcd','/bin/btcd')
h03.importFile('/home/justus/seed-emulator/examples/scion/S06-btcd/bin/btcwallet','/bin/btcwallet')
h03.appendStartCommand('chmod +x /bin/btcd', False)
h03.appendStartCommand('chmod +x /bin/btcwallet', False)


# Inter-AS routing
scion.addIxLink(100, (1, 150), (1, 151), ScLinkType.Core)
scion.addIxLink(100, (1, 151), (1, 152), ScLinkType.Core)
scion.addIxLink(100, (1, 152), (1, 150), ScLinkType.Core)
scion.addXcLink((1, 150), (1, 153), ScLinkType.Transit)

# Rendering
emu.addLayer(base)
emu.addLayer(routing)
emu.addLayer(scion_isd)
emu.addLayer(scion)

emu.render()

# Compilation
emu.compile(Docker(), './output', override=True)