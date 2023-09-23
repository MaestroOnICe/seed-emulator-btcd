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
    as102 = maker.createTier1AS(1, 102)

    # Bootstrap
    btcd.createBootstrap(as100)
    btcd.createBootstrap(as101)
    btcd.createBootstrap(as102)

    stub_100 = []
    for asn in range(110, 114):
        as_ = maker.createTier3AS(1, asn, issuer=100)
        stub_100.append(asn)
        btcd.createNode(as_)

    stub_101 = []
    for asn in range(120, 124):
        as_ = maker.createTier3AS(1, asn, issuer=101)
        stub_101.append(asn)
        btcd.createNode(as_)

    stub_102 = []
    for asn in range(130, 134):
        as_ = maker.createTier3AS(1, asn, issuer=102)
        stub_102.append(asn)
        btcd.createNode(as_)


    as130 = base.getAutonomousSystem(130)
    btcd.createNode(as130)
    btcd.createNode(as130)
    btcd.createNode(as130)
    btcd.createNode(as130)

    # Links
    ###############################################################################
    ixp_connector.IXPConnect(20, 100)
    ixp_connector.IXPConnect(20, 101)
    ixp_connector.IXPConnect(20, 102)

    ixp_connector.IXPConnect(21, 100)
    ixp_connector.IXPConnect(21, 101)
    ixp_connector.IXPConnect(21, 102)

    for asn in stub_100:
        cross_connector.XConnect(100, asn, "provider")

    for asn in stub_101:
        cross_connector.XConnect(101, asn, "provider")

    for asn in stub_102:
        cross_connector.XConnect(102, asn, "provider")


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
    experiment.moveLogs()
    time.sleep(2)
    experiment.up()

print("Sleeping for 120 seconds until hijack")
time.sleep(120)

print("Hijacking AS, sleeping for 5 minutes")
experiment.hijackAS(100, 130)
time.sleep(300)

experiment.endHijack(100)
print("Hijack ended, sleep for another 120 seconds")
time.sleep(120)

experiment.down()