from enum import Enum
from ipaddress import IPv4Network
import python_on_whales
import docker
import time
from seedemu.layers import ScionBase, ScionIsd, Ebgp, Scion, PeerRelationship
from seedemu.layers.Scion import LinkType as ScLinkType

###############################################################################
# Path Checker
class PathType(Enum):
    """!
    @brief Type of a path between two ASes, BGP or SCION.
    """

    ## BGP path between two ASes.
    BGP = "BGP"

    ## SCION path between two ASes.
    SCION = "SCION"


class PathChecker:
    def __init__(self):
        """!
        @brief Path checker, for scion and bgp mixed topology.
        """
        self.paths = []
        self.txt_file_path = 'paths.txt'
        with open(self.txt_file_path, mode='w', newline='') as file:
            pass  # Do nothing, just open and close to clear the file
        self.results_file = file

    def log(self, connection_type: PathType, source_asn: int, destination: str):
        """!
        @brief log a path to the internal list, to be checked later.

        @param connection_type identifies if SCION or BGP path
        @param source_asn ASN of the source for the path to be checked
        @param destination address of the host in the destination of the path in form of IP or full SCION address
        """
        path = [connection_type, source_asn, destination]
        self.paths.append(path)

    def deployAndCheck(self):
        print(self.paths)
        whales = python_on_whales.DockerClient(compose_files=["./output/docker-compose.yml"])
        whales.compose.build()
        whales.compose.up(detach=True)    

        # Use Docker SDK to interact with the containers
        client: docker.DockerClient = docker.from_env()
        ctrs = {ctr.name: client.containers.get(ctr.id) for ctr in whales.compose.ps()}

        # Sleep for 15 seconds to up the paths
        time.sleep(15)

        # all containers
        containers = ctrs.items()

        # check each path for connectivity
        for connection_type, source_asn, destination in self.paths:
            if(connection_type == PathType.BGP):
                cmd = f'ping {destination}'
            if(connection_type == PathType.SCION):
                cmd = f'scion ping {destination}'
            else:
                print("Error, not BGP or SCION for path from: ",source_asn, "to: ", destination)
                return
            
            host = f"csnode_{source_asn}_cs1"
            container = containers[host]
            print("Run path check in", host, end="")
            ec, output = container.exec_run(cmd)
            for line in output.decode('utf8').splitlines():
                self.results_file.write(line)

###############################################################################
# AS factory

# Tier 1 ASes have 4 border routers
def createTier1AS(base: ScionBase, scion_isd: ScionIsd, isdn: int, asn: int):
    """!
    @brief create a Tier 1 AS with 4 border routers.

    @param base reference to the scion base layer.
    @param scion_isd reference to teh scion isd layer
    @param isdn number of the isd in which the AS is in
    @param asn ASN of the newly created AS.

    @returns Tier 1 AS object.
    """

    as_ = base.createAutonomousSystem(asn)
    scion_isd.addIsdAs(isdn, asn, is_core=True)
    as_.setBeaconingIntervals('30s', '30s', '30s')

    as_.createNetwork('net0')
    as_.createNetwork('net1')
    as_.createNetwork('net2')    
    as_.createNetwork('net3')
    as_.createControlService('cs1').joinNetwork('net0')

    br0 = as_.createRouter('br0')
    br1 = as_.createRouter('br1')
    br2 = as_.createRouter('br2')
    br3 = as_.createRouter('br3')

    br0.joinNetwork('net0').joinNetwork('net1')
    br1.joinNetwork('net1').joinNetwork('net2')
    br2.joinNetwork('net2').joinNetwork('net3')
    br3.joinNetwork('net3').joinNetwork('net0')
    return as_

# Tier 2 ASes have 2 border routers
def createTier2AS(base: ScionBase, scion_isd: ScionIsd, isdn: int, asn: int, issuer=None):
    """!
    @brief create a Tier 2 AS with 4 border routers.

    @param base reference to the scion base layer.
    @param scion_isd reference to teh scion isd layer
    @param isdn number of the isd in which the AS is in
    @param asn ASN of the newly created AS.
    @param issuer ASN of the certificte issuer

    @returns Tier 2 AS object.
    """

    as_ = base.createAutonomousSystem(asn)
    scion_isd.addIsdAs(isdn, asn, False)
    scion_isd.setCertIssuer((isdn, asn), issuer)
    as_.setBeaconingIntervals('30s', '30s', '30s')

    as_.createNetwork('net0')
    as_.createNetwork('net1')
    as_.createControlService('cs1').joinNetwork('net0')

    br0 = as_.createRouter('br0')
    br1 = as_.createRouter('br1')
    
    br0.joinNetwork('net0').joinNetwork('net1')
    br1.joinNetwork('net0').joinNetwork('net1')
    return as_

# Tier 3 ASes have 1 border router
def createTier3AS(base: ScionBase, scion_isd: ScionIsd, isdn: int, asn: int, issuer=None):
    """!
    @brief create a Tier 3 AS with 4 border routers.

    @param base reference to the scion base layer.
    @param scion_isd reference to teh scion isd layer
    @param isdn number of the isd in which the AS is in
    @param asn ASN of the newly created AS.
    @param issuer ASN of the certificte issuer

    @returns Tier 3 AS object.
    """

    as_ = base.createAutonomousSystem(asn)
    scion_isd.addIsdAs(isdn, asn, False)
    scion_isd.setCertIssuer((isdn, asn), issuer)
    as_.setBeaconingIntervals('30s', '30s', '30s')

    as_.createNetwork('net0')
    as_.createControlService('cs1').joinNetwork('net0')

    br0 = as_.createRouter('br0')
    br0.joinNetwork('net0')
    return as_

###############################################################################
# Link factory

class CrossConnectNetAssigner:
    def __init__(self):
        self.subnet_iter = IPv4Network("10.3.0.0/16").subnets(new_prefix=29)
        self.xc_nets = {}

    def next_addr(self, net):
        if net not in self.xc_nets:
            hosts = next(self.subnet_iter).hosts()
            next(hosts) # Skip first IP (reserved for Docker)
            self.xc_nets[net] = hosts
        return "{}/29".format(next(self.xc_nets[net]))

xc_nets = CrossConnectNetAssigner()


ebgp_types = {
    "peer": PeerRelationship.Peer,
    "provider": PeerRelationship.Provider,
    "core": PeerRelationship.Peer
}

sclink_type = {
    "peer": ScLinkType.Peer,
    "provider": ScLinkType.Transit,
    "core": ScLinkType.Core   
}

class xConnector:
    def __init__(self, base: ScionBase, scion_isd: ScionIsd, ebgp: Ebgp, scion: Scion, path_checker: PathChecker = None):
        self.base = base
        self.scion_isd = scion_isd
        self.ebgp = ebgp
        self.scion = scion
        self.checker = path_checker

    # SCION and BGP cross connect two ASes
    def XConnect(self, asn_a: int, asn_b: int, type: str):
        # cross connecting AS a <-> AS b
        as_a = self.base.getAutonomousSystem(asn_a)
        as_b = self.base.getAutonomousSystem(asn_b)
        br_a = as_a.getRouter('br0')
        br_b = as_b.getRouter('br0')
        br_a.crossConnect(asn_b, 'br0', xc_nets.next_addr(f'{asn_a}-{asn_b}'))
        br_b.crossConnect(asn_a, 'br0', xc_nets.next_addr(f'{asn_a}-{asn_b}'))

        # lookup ISD AS a and ISD b are in, at this time, one AS is only in one ISD
        as_a_isd = self.scion_isd.getAsIsds(asn_a)[0]
        as_b_isd = self.scion_isd.getAsIsds(asn_b)[0]

        # log each connection (BGP and SCION) to be checked later after deployment
        if hasattr(self, "checker"):
            bgp_destination = f'10.{asn_b}.0.71'
            scion_destination = f'{as_b_isd[0]}-{asn_b},10.{asn_b}.0.71'
            self.checker.log(PathType.BGP, asn_a, bgp_destination)
            self.checker.log(PathType.SCION, asn_a, scion_destination)

        # will throw error if link type does not match
        self.scion.addXcLink((as_a_isd[0],asn_a), (as_b_isd[0],asn_b), sclink_type.get(type, "null"))
        
        # will throw error if link type does not match
        self.ebgp.addCrossConnectPeering(asn_a, asn_b, ebgp_types.get(type, "null"))

# Connect an AS to an IXP, with SCION and BGP
# SCION connections are saved, because they will be added in the end
# due to the need to specify each connection like 
# scion.addIxLink(IXn, (ISD, ASn), (ISD, ASn), Linktype)

class ixpConnector:
    def __init__(self, base: ScionBase, scion_isd: ScionIsd, ebgp: Ebgp, scion: Scion, path_checker: PathChecker = None):
        self.base = base
        self.scion_isd = scion_isd
        self.ebgp = ebgp
        self.scion = scion
        self.checker = path_checker
        # create a dict of lists, entries are ASes that connect to the respective IXP
        self.ixs = {}
        ixn_list = base.getInternetExchangeIds()
        for ixn in ixn_list:
            self.ixs[ixn] = []


    def IXPConnect(self, ixn: int, asn: int):
        # AS has to join the network of IXP 
        br = self.base.getAutonomousSystem(asn).getRouter('br0')
        br.joinNetwork(f'ix{ixn}')
        self.ebgp.addRsPeer(ixn, asn)
        self.ixs[ixn].append(asn)

    def AddScionIXPConnections(self):
        addedIXConnections = []
        for ixn, ixn_list in self.ixs.items():
            for asn_a in ixn_list:
                for asn_b in ixn_list:
                    if asn_a != asn_b:
                        # skip this pair, when both endpoints have already an IX link between them
                        if([ixn, asn_a, asn_b ] in addedIXConnections or [ixn, asn_b, asn_a ]in addedIXConnections):
                            continue

                        # lookup ISD AS a and ISD b are in, at this time, one AS is only in one ISD
                        as_a_isd = self.scion_isd.getAsIsds(asn_a)[0]
                        as_b_isd = self.scion_isd.getAsIsds(asn_b)[0]

                        # log each connection (BGP and SCION) to be checked later after deployment
                        if hasattr(self, "checker"):
                            bgp_destination = f'10.{asn_b}.0.71'
                            scion_destination = f'{as_b_isd[0]}-{asn_b},10.{asn_b}.0.71'
                            self.checker.log(PathType.BGP, asn_a, bgp_destination)
                            self.checker.log(PathType.SCION, asn_a, scion_destination)

                        # A link of an IX should only be scripted once, otherwise the link would be created twice in both directions
                        addedIXConnections.append([ixn, asn_a, asn_b]) 
                        #print(ixn, "connect ",as_a_isd[0], asn_a," to ",as_b_isd[0], asn_b, "as peer")            
                        self.scion.addIxLink(ixn, (as_a_isd[0], asn_a), (as_b_isd[0], asn_b), ScLinkType.Peer)



        