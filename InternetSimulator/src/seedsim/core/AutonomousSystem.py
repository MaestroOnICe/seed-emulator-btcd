from .Printable import Printable
from .Network import Network
from .AddressAssignmentConstraint import AddressAssignmentConstraint
from .enums import NetworkType
from ipaddress import IPv4Network
from typing import Generator, Dict

class AutonomousSystem(Printable):
    """!
    @brief AutonomousSystem class. 

    This class represents an autonomous system.
    """

    __asn: int
    __nets: Dict[str, Network]
    __subnet_generator: Generator[IPv4Network, None, None]

    def __init__(self, asn: int):
        """!
        @brief AutonomousSystem constructor.

        @param asn ASN for this system.
        """
        self.__nets = {}
        self.__asn = asn
        self.__subnet_generator = none if asn > 255 else IPv4Network("10.{}.0.0/16".format(asn)).subnets(new_prefix = 24)
    
    def createNetwork(self, name: str, prefix: str = "auto", aac: AddressAssignmentConstraint = None) -> Network:
        """!
        @brief Create a new network.

        @param name name of the new network.
        @param prefix optional. Network prefix of this network. If not set, a
        /24 subnet of "10.{asn}.{id}.0/24" will be used, where asn is ASN of
        this AS, and id is a self-incremental value starts from 0.
        @throws AssertionError if name exists, or, if auto prefix is set but asn > 255
        @throws StopIteration if subnet exhausted.
        """
    
        assert name not in self.__nets, "network {} already exist on as{}".format(name, self.__asn)
        assert prefix != "auto" or self.__asn <= 255, "can't use auto: asn > 255"

        network = IPv4Network(prefix) if prefix != "auto" else next(self.__subnet_generator)
        self.__nets[name] = Network(name, NetworkType.Local, network, aac)
        return self.__nets[name]
        
    def print(self, indent: int) -> str:
        out = ' ' * indent
        out += 'AutonomousSystem as{}:\n'.format(self.__asn)

        indent += 4
        out += ' ' * indent
        out += 'Networks:\n'

        for net in self.__nets.values():
            out += net.print(indent + 4)

        return out