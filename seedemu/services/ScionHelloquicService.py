from __future__ import annotations
from typing import Dict

from seedemu.core import Node, Server, Service

ScionHelloquicServerTemplates: Dict[str, str] = {}

ScionHelloquicServerTemplates['command'] = """\
ip=$(hostname --ip-address)
helloquic -listen=$ip:{port} >> /var/log/helloquic.log
echo "helloquicserver started" """


class ScionHelloquicServer(Server):
    """!
    @brief SCION helloquic server.
    """

    __port: int

    def __init__(self):
        """!
        @brief ScionHelloquic constructor.
        """
        super().__init__()
        self.__port = 9000

    def setPort(self, port: int) -> ScionHelloquicServer:
        """!
        @brief Set port the SCION helloquic server listens on.

        @param port
        @returns self, for chaining API calls.
        """
        self.__port = port

        return self

    def install(self, node: Node):
        """!
        @brief Install the service.
        """
        node.appendStartCommand(ScionHelloquicServerTemplates['command'].format(port=str(self.__port)), fork=True)
        node.appendClassName("ScionHelloquicService")

    def print(self, indent: int) -> str:
        out = ' ' * indent
        out += 'SCION helloquic server object.\n'
        return out


class ScionHelloquicService(Service):
    """!
    @brief SCION helloquic server service class.
    """

    def __init__(self):
        """!
        @brief ScionHelloquicService constructor.
        """
        super().__init__()
        self.addDependency('Base', False, False)
        self.addDependency('Scion', False, False)

    def _createServer(self) -> Server:
        return ScionHelloquicServer()

    def getName(self) -> str:
        return 'ScionHelloquicService'

    def print(self, indent: int) -> str:
        out = ' ' * indent
        out += 'ScionHelloquicServiceLayer\n'
        return out
