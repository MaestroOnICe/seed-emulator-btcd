#!/usr/bin/env python3
# encoding: utf-8

from seedemu.layers import ScionBase, ScionRouting, Ebgp, ScionIsd, Scion
from seedemu.compiler import Docker, Graphviz
from seedemu.core import Emulator
import examples.scion.utility.utils as utils
import examples.scion.utility.bitcoin as bitcoin
from seedemu.layers.Scion import LinkType as ScLinkType

# Initialize the emulator and layers
###############################################################################
emu     = Emulator()
base    = ScionBase()
routing = ScionRouting()
ebgp    = Ebgp()
scion_isd = ScionIsd()
scion = Scion()

isd1 = base.createIsolationDomain(1) # NA
ix20 = base.createInternetExchange(20)


path_checker = utils.PathChecker()
cross_connector = utils.CrossConnector(base, scion_isd, ebgp, scion, path_checker)
ixp_connector = utils.IXPConnector(base, scion_isd, ebgp, scion, path_checker)
maker = utils.AutonomousSystemMaker(base, scion_isd)
btcd = bitcoin.btcd()


as100 = maker.createTier1AS(1, 100)
as101 = maker.createTier1AS(1, 101)
as102 = maker.createTier1AS(1, 102)

# ixp_connector.addIXLink(20, 2, 3, ScLinkType.Core)
# ixp_connector.addIXLink(20, 2, 4, ScLinkType.Core)
# ixp_connector.addIXLink(20, 4, 3, ScLinkType.Core)
ixp_connector.IXPConnect(20, 100)
ixp_connector.IXPConnect(20, 101)
ixp_connector.IXPConnect(20, 102)

# ebgp.addRsPeer(20, 2)
# ebgp.addRsPeer(20, 3)
# ebgp.addRsPeer(20, 4)


btcd.createNode(as100)
btcd.createNode(as101)
btcd.createBootstrap(as102)

# Rendering 
###############################################################################
ixp_connector.addScionIXPConnections()
emu.addLayer(base)
emu.addLayer(routing)
emu.addLayer(scion_isd)
emu.addLayer(scion)
emu.addLayer(ebgp)

emu.render()

# Compilation
###############################################################################
emu.compile(Docker(), './output', override=True)
emu.compile(Graphviz(), "./output/graphs", override=True)

#path_checker.deployAndCheck()
path_checker.deploy()