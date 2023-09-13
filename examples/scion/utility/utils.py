from ipaddress import IPv4Network
from sys import stderr
import python_on_whales
import docker
import time
from seedemu.layers import ScionBase, ScionIsd, Ebgp, Scion, PeerRelationship
from seedemu.layers.Scion import LinkType as ScLinkType

###############################################################################
# Path Checker
class PathChecker:
    def __init__(self):
        """!
        @brief Path checker, for scion and bgp mixed topology.
        """
        self.paths = []
        # self.txt_file_path = 'paths.txt'
        # with open(self.txt_file_path, mode='w', newline='') as file:
        #     pass  # Do nothing, just open and close to clear the file
        # self.results_file = file
    
    def getName(self) -> str:
        return "Path Checker"

    def _log(self, message: str) -> None:
        """!
        @brief Log to stderr.
        """
        print("==== {}: {}".format(self.getName(), message), file=stderr)

    def _savePath(self, connection_type: int, source_asn: int, destination: str, policy: str):
        """!
        @brief log a path to the internal list, to be checked later.

        @param connection_type identifies if SCION or BGP path
        @param source_asn ASN of the source for the path to be checked
        @param destination address of the host in the destination of the path in form of IP or full SCION address
        """
        path = [connection_type, source_asn, destination, policy]
        self.paths.append(path)

    def deployAndCheck(self):
        index = 1
        for path in self.paths:
            self._log(f"Path {index} from AS: {path[1]} to destination address: {path[2]}")
            index = index +1
            
        try:
            whales = python_on_whales.DockerClient(compose_files=["./output/docker-compose.yml"])
            whales.compose.build()
            whales.compose.up(build=True, detach=True)    

            # Use Docker SDK to interact with the containers
            client: docker.DockerClient = docker.from_env()
            ctrs = {ctr.name: client.containers.get(ctr.id) for ctr in whales.compose.ps()}

            # Sleep for 15 seconds to up the paths
            self._log("Sleeping 15 seconds, waiting for the topology and links to come up")
            time.sleep(15)
            
            # check each path for connectivity
            connection_type_str = ""
            for connection_type, source_asn, destination, policy in self.paths:
                if connection_type == 1:
                    cmd = f'ping {destination} -c 1'
                    connection_type_str = "BGP  "
                if connection_type == 2:
                    cmd = f'scion ping {destination} -c 1'
                    connection_type_str = "SCION"
                if connection_type != 1 and connection_type != 2:
                    self._log(f'Error, not BGP or SCION for path from: {source_asn}to: {destination}\n')
                    whales.compose.down()
                    return
                
                host = f'as{source_asn}h-cs1-10.{source_asn}.0.71'
                container = ctrs[host]
                
                _, output = container.exec_run(cmd)
                if "Error" in output.decode('utf8'):
                    self._log(f'\u2718 Error, in path from AS {source_asn} to {destination} {connection_type_str}, {policy}')
                else:
                    self._log(f'\u2714 No Er, in path from AS {source_asn} to {destination} {connection_type_str}, {policy}')
            
            user_input = input("Do you want to want to bring all containers and networks down? (yes/no): ")
            # Check the user's input
            if user_input.lower() == "yes":
                print("Okay, brining all containers and networks down...")
                whales.compose.down()
            elif user_input.lower() == "no":
                print("Okay goodbye...")
                return
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")

        except KeyboardInterrupt:
            print("Keyboard interrupt received. Cleaning up...")
            whales.compose.down()
        except Exception:
            print("Keyboard interrupt received. Cleaning up...")
            whales.compose.down()
###############################################################################
# AS factory

class AutonomousSystemMaker:
    def __init__(self, base: ScionBase, scion_isd: ScionIsd):
        self.base = base
        self.scion_isd = scion_isd

    # Tier 1 ASes have 4 border routers
    def createTier1AS(self, isdn: int, asn: int):
        """!
        @brief create a Tier 1 AS with 4 border routers.

        @param base reference to the scion base layer.
        @param scion_isd reference to teh scion isd layer
        @param isdn number of the isd in which the AS is in
        @param asn ASN of the newly created AS.

        @returns Tier 1 AS object.
        """

        as_ = self.base.createAutonomousSystem(asn)
        self.scion_isd.addIsdAs(isdn, asn, is_core=True)
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
    def createTier2AS(self, isdn: int, asn: int, issuer=None):
        """!
        @brief create a Tier 2 AS with 4 border routers.

        @param base reference to the scion base layer.
        @param scion_isd reference to teh scion isd layer
        @param isdn number of the isd in which the AS is in
        @param asn ASN of the newly created AS.
        @param issuer ASN of the certificte issuer

        @returns Tier 2 AS object.
        """

        as_ = self.base.createAutonomousSystem(asn)
        self.scion_isd.addIsdAs(isdn, asn, False)
        self.scion_isd.setCertIssuer((isdn, asn), issuer)
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
    def createTier3AS(self, isdn: int, asn: int, issuer=None):
        """!
        @brief create a Tier 3 AS with 4 border routers.

        @param base reference to the scion base layer.
        @param scion_isd reference to teh scion isd layer
        @param isdn number of the isd in which the AS is in
        @param asn ASN of the newly created AS.
        @param issuer ASN of the certificte issuer

        @returns Tier 3 AS object.
        """

        as_ = self.base.createAutonomousSystem(asn)
        self.scion_isd.addIsdAs(isdn, asn, False)
        self.scion_isd.setCertIssuer((isdn, asn), issuer)
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

    def _next_addr(self, net):
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

class CrossConnector:
    def __init__(self, base: ScionBase, scion_isd: ScionIsd, ebgp: Ebgp, scion: Scion, path_checker: PathChecker = None):
        self.base = base
        self.scion_isd = scion_isd
        self.ebgp = ebgp
        self.scion = scion
        self.checker = path_checker

    # SCION and BGP cross connect two ASes
    def XConnect(self, asn_a: int, asn_b: int, policy: str, as_a_router: str="br0", as_b_router: str="br0"):
        # cross connecting AS a <-> AS b
        as_a = self.base.getAutonomousSystem(asn_a)
        as_b = self.base.getAutonomousSystem(asn_b)
        br_a = as_a.getRouter(as_a_router)
        br_b = as_b.getRouter(as_b_router)
        br_a.crossConnect(asn_b, as_b_router, xc_nets._next_addr(f'{asn_a}-{asn_b}'))
        br_b.crossConnect(asn_a, as_a_router, xc_nets._next_addr(f'{asn_a}-{asn_b}'))

        # lookup ISD AS a and ISD b are in, at this time, one AS is only in one ISD
        as_a_isd = self.scion_isd.getAsIsds(asn_a)[0]
        as_b_isd = self.scion_isd.getAsIsds(asn_b)[0]

        # log each connection (BGP and SCION) to be checked later after deployment
        if hasattr(self, "checker"):
            bgp_destination = f'      10.{asn_b}.0.71'
            scion_destination = f'{as_b_isd[0]}-{asn_b},10.{asn_b}.0.71'
            self.checker._savePath(1, asn_a, bgp_destination, policy)
            self.checker._savePath(2, asn_a, scion_destination, policy)

        # will throw error if link type does not match
        self.scion.addXcLink((as_a_isd[0],asn_a), (as_b_isd[0],asn_b), sclink_type.get(policy, "null"))
        
        # will throw error if link type does not match
        self.ebgp.addCrossConnectPeering(asn_a, asn_b, ebgp_types.get(policy, "null"))


class IXPConnector:
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


    def IXPConnect(self, ixn: int, asn: int, router: str="br0"):
        # AS has to join the network of IXP 
        br = self.base.getAutonomousSystem(asn).getRouter(router)
        br.joinNetwork(f'ix{ixn}')
        self.ebgp.addRsPeer(ixn, asn)
        self.ixs[ixn].append(asn)

    def addScionIXPConnections(self):
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

                        # if two core ASes are connected through an IXP, they should have the core type
                        link_policy = ScLinkType.Peer
                        if self.scion_isd.isCoreAs(as_a_isd[0], asn_a) and self.scion_isd.isCoreAs(as_b_isd[0], asn_b):
                             link_policy = ScLinkType.Core

                        # log each connection (BGP and SCION) to be checked later after deployment
                        if hasattr(self, "checker"):
                            # from A -> B
                            bgp_destination = f'      10.{asn_b}.0.71'
                            scion_destination = f'{as_b_isd[0]}-{asn_b},10.{asn_b}.0.71'
                            self.checker._savePath(1, asn_a, bgp_destination, "Peering")
                            self.checker._savePath(2, asn_a, scion_destination, "Peering" if link_policy == ScLinkType.Peer else "Core")

                            # from B -> A
                            bgp_destination = f'      10.{asn_a}.0.71'
                            scion_destination = f'{as_a_isd[0]}-{asn_a},10.{asn_a}.0.71'
                            self.checker._savePath(1, asn_b, bgp_destination, "Peering")
                            self.checker._savePath(2, asn_b, scion_destination, "Peering" if link_policy == ScLinkType.Peer else "Core")     

                        print(f'checcking if AS {asn_a} is a Core in {as_a_isd[0]}: {self.scion_isd.isCoreAs(as_a_isd[0], asn_a)}')
                        print(f'checcking if AS {asn_b} is a Core in {as_b_isd[0]}: {self.scion_isd.isCoreAs(as_b_isd[0], asn_b)}')

                        # A link of an IX should only be scripted once, otherwise the link would be created twice in both directions
                        addedIXConnections.append([ixn, asn_a, asn_b])     
                        self.scion.addIxLink(ixn, (as_a_isd[0], asn_a), (as_b_isd[0], asn_b), link_policy)



        