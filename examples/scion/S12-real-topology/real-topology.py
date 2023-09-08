#!/usr/bin/env python3

#from ipaddress import IPv4Network
from seedemu.compiler import Docker, Graphviz
from seedemu.core import Emulator
from seedemu.layers import ScionBase, ScionRouting, ScionIsd, Scion, Ospf, Ibgp, Ebgp, PeerRelationship 
from seedemu.layers.Scion import LinkType as ScLinkType


###############################################################################
# AS factory
def create_tier1_as(isd, asn, is_core=False, issuer=None):
    as_ = base.createAutonomousSystem(asn)
    scion_isd.addIsdAs(isd, asn, is_core)
    if not is_core:
        scion_isd.setCertIssuer((isd, asn), issuer)
    as_.createNetwork('net0')
    as_.createControlService('cs1').joinNetwork('net0')
    #as_.setBeaconingIntervals('30s', '30s', '30s')
    # if is_core:
    #     policy = {
    #         'Filter': {
    #             'MaxHopsLength': 4,
    #             'AllowIsdLoop': False
    #         }
    #     }
    #     as_.setBeaconPolicy('propagation', policy).setBeaconPolicy('core_registration', policy)
    br = as_.createRouter('br0')
    br.joinNetwork('net0')
    return as_, br


def create_tier2_as(isd, asn, is_core=False, issuer=None):
    as_ = base.createAutonomousSystem(asn)
    scion_isd.addIsdAs(isd, asn, is_core)
    if not is_core:
        scion_isd.setCertIssuer((isd, asn), issuer)
    as_.createNetwork('net0')
    as_.createControlService('cs1').joinNetwork('net0')
    #as_.setBeaconingIntervals('30s', '30s', '30s')
    # if is_core:
    #     policy = {
    #         'Filter': {
    #             'MaxHopsLength': 4,
    #             'AllowIsdLoop': False
    #         }
    #     }
    #     as_.setBeaconPolicy('propagation', policy).setBeaconPolicy('core_registration', policy)
    br = as_.createRouter('br0')
    br.joinNetwork('net0')
    return as_, br

def create_tier3_as(isd, asn, is_core=False, issuer=None):
    as_ = base.createAutonomousSystem(asn)
    scion_isd.addIsdAs(isd, asn, is_core)
    if not is_core:
        scion_isd.setCertIssuer((isd, asn), issuer)
    as_.createNetwork('net0')
    as_.createControlService('cs1').joinNetwork('net0')
    #as_.setBeaconingIntervals('30s', '30s', '30s')
    # if is_core:
    #     policy = {
    #         'Filter': {
    #             'MaxHopsLength': 4,
    #             'AllowIsdLoop': False
    #         }
    #     }
    #     as_.setBeaconPolicy('propagation', policy).setBeaconPolicy('core_registration', policy)
    br = as_.createRouter('br0')
    br.joinNetwork('net0')
    return as_, br


###############################################################################
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
# Internet Exchanges
isd1 = base.createIsolationDomain(1) # Europe
isd2 = base.createIsolationDomain(2) # Cloud - Europe
isd3 = base.createIsolationDomain(3) # Asia
isd4 = base.createIsolationDomain(4) # Cloud - Asia
isd5 = base.createIsolationDomain(5) # Africa
isd6 = base.createIsolationDomain(6) # South America
isd7 = base.createIsolationDomain(7) # North America
isd8 = base.createIsolationDomain(8) # Cloud - North America

isd1.setLabel('Europe')
isd2.setLabel('Cloud - Europe')
isd3.setLabel('Asia')
isd4.setLabel('Cloud - Asia')
isd5.setLabel('Africa')
isd6.setLabel('South America')
isd7.setLabel('North America')
isd8.setLabel('Cloud - North America')


###############################################################################
# Internet Exchanges
ix100 = base.createInternetExchange(100) # Frankfurt (Europe)
ix101 = base.createInternetExchange(101) # London (Europe)
ix102 = base.createInternetExchange(102) # Amsterdam (Europe)
ix103 = base.createInternetExchange(103) # Hong Kong (Asia)
ix104 = base.createInternetExchange(104) # Singapore (Asia)
ix105 = base.createInternetExchange(105) # Accra (Africa)
ix106 = base.createInternetExchange(106) # Sao Paulo (South America)
ix107 = base.createInternetExchange(107) # Los Angeles (North America)
ix108 = base.createInternetExchange(108) # Miami (North America)


# Customize names (for visualization purpose)
ix100.getPeeringLan().setDisplayName('Frankfurt-100')
ix101.getPeeringLan().setDisplayName('London-101')
ix102.getPeeringLan().setDisplayName('Amsterdam-102')
ix103.getPeeringLan().setDisplayName('Hong Kong-103')
ix104.getPeeringLan().setDisplayName('Singapore-104')
ix105.getPeeringLan().setDisplayName('Accra-105')
ix106.getPeeringLan().setDisplayName('Sao Paulo-106')
ix107.getPeeringLan().setDisplayName('Los Angeles-107')
ix108.getPeeringLan().setDisplayName('Miami-108')


###############################################################################
# Tier 1 ASes

# Europe



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

###############################################################################
# Compilation
emu.compile(Docker(), "./output", override=True)
emu.compile(Graphviz(), "./output/graphs", override=True)