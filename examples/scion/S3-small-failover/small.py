#!/usr/bin/env python3
# encoding: utf-8

import time
from seedemu.layers import ScionBase, ScionRouting, Ebgp, ScionIsd, Scion
from seedemu.compiler import Docker, Graphviz
from seedemu.core import Emulator
import examples.scion.utility.utils as utils
import examples.scion.utility.bitcoin as bitcoin
import examples.scion.utility.experiment as experiment
import sys

if len(sys.argv) > 1 and sys.argv[1] == str(1):
    # Initialize the emulator and layers
    ###############################################################################
    emu     = Emulator()
    base    = ScionBase()
    routing = ScionRouting()
    ebgp    = Ebgp()
    scion_isd = ScionIsd()
    scion = Scion()

    isd1 = base.createIsolationDomain(1)
    ix20 = base.createInternetExchange(20)
    ix21 = base.createInternetExchange(21)


    path_checker = utils.PathChecker()
    cross_connector = utils.CrossConnector(base, scion_isd, ebgp, scion, path_checker)
    ixp_connector = utils.IXPConnector(base, scion_isd, ebgp, scion, path_checker)
    maker = utils.AutonomousSystemMaker(base, scion_isd)
    btcd = bitcoin.btcd(scion_isd)


    as100 = maker.createTier1AS(1, 100)
    as101 = maker.createTier1AS(1, 101)

    as130 = maker.createTier3AS(1, 130, issuer=101)
    as131 = maker.createTier3AS(1, 131, issuer=101)
    # Links
    ###############################################################################
    ixp_connector.IXPConnect(20, 100)
    ixp_connector.IXPConnect(20, 101)

    cross_connector.XConnect(100,130, "provider")
    cross_connector.XConnect(101,131, "provider")


    # Rendering s
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
    experiment.deploy()

else:
    time.sleep(2)
    experiment.up()


experiment.down()