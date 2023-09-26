#!/usr/bin/env python3
# encoding: utf-8

from ipaddress import IPv4Network
import time
from seedemu.layers import ScionBase, ScionRouting, Ebgp, ScionIsd, Scion, PeerRelationship
from seedemu.compiler import Docker, Graphviz
from seedemu.core import Emulator
import examples.scion.utility.utils as utils
import examples.scion.utility.bitcoin as bitcoin
import examples.scion.utility.experiment as experiment
import sys
from seedemu.layers.Scion import LinkType as ScLinkType

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



    class CrossConnectNetAssigner:
        def __init__(self):
            self.subnet_iter = IPv4Network("10.3.0.0/16").subnets(new_prefix=29)
            self.xc_nets = {}

        def _next_addr(self, net):
            if net not in self.xc_nets:
                hosts = next(self.subnet_iter).hosts()
                next(hosts) # Skip first IP (reserved for Docker)
                self.xc_nets[net] = hosts
            return "{}/29".format(next(self.xc_nets[net]))

    xc_nets = CrossConnectNetAssigner()

    def crossNet(asn_a: int, asn_b: int, as_a_router: str="br0", as_b_router: str="br0"):
        # cross connecting AS a <-> AS b
        as_a = base.getAutonomousSystem(asn_a)
        as_b = base.getAutonomousSystem(asn_b)
        br_a = as_a.getRouter(as_a_router)
        br_b = as_b.getRouter(as_b_router)
        br_a.crossConnect(asn_b, as_b_router, xc_nets._next_addr(f'{asn_a}-{asn_b}'))
        br_b.crossConnect(asn_a, as_a_router, xc_nets._next_addr(f'{asn_a}-{asn_b}'))




    as100 = maker.createTier1AS(1, 100)
    as101 = maker.createTier1AS(1, 101)

    as130 = maker.createTier3AS(1, 130, issuer=101)
    as131 = maker.createTier3AS(1, 131, issuer=101)
    # Links
    ###############################################################################
    
    as100.getRouter("br0").joinNetwork("ix20")
    as100.getRouter("br0").joinNetwork("ix21")
    as101.getRouter("br0").joinNetwork("ix20")
    as101.getRouter("br0").joinNetwork("ix21")
    ebgp.addRsPeer(20, 100)
    ebgp.addRsPeer(20, 101)

    ebgp.addRsPeer(21, 100)
    ebgp.addRsPeer(21, 101)

    scion.addIxLink(20, (1, 100), (1, 101), ScLinkType.Core)
    scion.addIxLink(21, (1, 100), (1, 101), ScLinkType.Core)

    crossNet(100,130)
    scion.addXcLink((1,100), (1,130), ScLinkType.Transit)
    ebgp.addCrossConnectPeering(100, 130, PeerRelationship.Provider)


    crossNet(101,131)
    scion.addXcLink((1,101), (1,131), ScLinkType.Transit)
    ebgp.addCrossConnectPeering(101, 131, PeerRelationship.Provider)

    btcd.createMeasuringNode(as130, "1-131,10.131.0.80:8666")
    btcd.createMeasuringServer(as131)

    btcd.createTCPMeasuringNode(as130, "10.131.0.81:8666")
    btcd.createTCPMeasuringServer(as131)

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
    experiment.deploy()

time.sleep(5)



# experiment.down()