import os
from seedemu.core import Node, ScionAutonomousSystem

###############################################################################
# btcd
class btcd:
    def __init__(self):
        self.__wd = os.getcwd()
        self.__nodeNames = {}

    def createNode(self, as_: ScionAutonomousSystem):
        asn = as_.getAsn
        if asn not in self.__nodeNames:
            self.__nodeNames[asn] = []
           
        host_number = len(self.__nodeNames[asn]) + 1

        # creates the host in the seed emulator
        host = as_.createHost(f'node_{asn}_{host_number}').joinNetwork("net0")
        self.__addNode(host)
    

    def createBootstrap(self, as_: ScionAutonomousSystem):
        # creates the host in the seed emulator
        host = as_.createHost("bootstrap_node").joinNetwork("net0")
        self.__addBootstrapNode(host)


    # def createScionNode(self, as_: ScionAutonomousSystem):
    #     # creates the host in the seed emulator
    #     host = as_.createHost("scion_node").joinNetwork("net0")
    #     self.__addScionNode(host)


###############################################################################
    # adds IP version of btcd to the host  
    def __addNode(self, host: Node):
        # add logging folder
        name = host.getName()
        log_path = f'{self.__wd}/logs/{name}'
        os.mkdir(log_path)
        host.addSharedFolder('/root/.btcd/logs/', log_path)

        # add binary and config from the shared folder, make it executable
        host.addSharedFolder('/shared/',self.__wd+'/bin/')
        host.appendStartCommand("cp /shared/btcd /bin/btcd", False)
        host.appendStartCommand("chmod +x /bin/btcd", False)

        # import the config file for a default IP client
        host.importFile(self.__wd+'/configs/node_ip.conf', '/root/.btcd/btcd.conf')

        # on start up wait 15 seconds afterwards start the node
        host.appendStartCommand('sleep 15', False)
        host.appendStartCommand('btcd --configfile /root/.btcd/btcd.conf', False)

    # adds IP version of btcd to the host with Bootstrap configuration
    def __addBootstrapNode(self, host: Node):
        # add logging folder
        name = host.getName()
        log_path = f'{self.__wd}/logs/{name}'
        os.mkdir(log_path)
        host.addSharedFolder('/root/.btcd/logs/', log_path)

        # add binary and config from the shared folder, make it executable
        host.addSharedFolder('/shared/',self.__wd+'/bin/')
        host.appendStartCommand("cp /shared/btcd /bin/btcd", False)
        host.appendStartCommand("chmod +x /bin/btcd", False)

        # import the config file for a default IP client
        host.importFile(self.__wd+'/configs/bootstrap_ip.conf', '/root/.btcd/btcd.conf')

        # on start up wait 10 seconds afterwards start the node
        host.appendStartCommand('sleep 10', False)
        host.appendStartCommand('btcd --configfile /root/.btcd/btcd.conf', False)


    # adds SCION/IP version of btcd to the host  
    # def __addScionNode(self, host: Node):
    #     # add logging folder
        
    #     # add binary from the shared folder, make it executable and run startup script
    #     host.addSharedFolder('/shared/','/home/justus/seed-emulator/examples/scion/S14-testing/resources/')
    #     host.appendStartCommand("cp /shared/btcd_scion /bin/btcd", False)
    #     host.appendStartCommand("chmod +x /bin/btcd", False)
    #     # host.importFile('/home/justus/seed-emulator/examples/scion/S07-btcd-bgp/scripts/run.sh', '/run.sh')
    #     # host.appendStartCommand("chmod +x /run.sh", False)
