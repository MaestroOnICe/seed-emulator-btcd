import os
import shutil
from seedemu.core import Node, ScionAutonomousSystem
import re

###############################################################################
# btcd
class btcd:
    def __init__(self):
        self.__wd = os.getcwd()
        self.__nodeNames = {}
        self.log_path = self.creatLoggingDirectory()

    # Nodes begin at .100 and the ascend per ASN
    def createNode(self, as_: ScionAutonomousSystem):
        asn = as_.getAsn()
        node_number = self.createNodeName(asn)

        # creates the host in the seed emulator
        host = as_.createHost(f'node_{asn}_{node_number}').joinNetwork("net0", address=f"10.{asn}.0.{node_number}")
        self.__addNode(host)
    

    # Bootstrap nodes are always .200 ip addresses
    def createBootstrap(self, as_: ScionAutonomousSystem):
        asn = as_.getAsn()
        node_number = self.createNodeName(asn)
    
        # creates the host in the seed emulator
        host = as_.createHost(f'node_{asn}_{node_number}').joinNetwork("net0", address=f"10.{asn}.0.200")
        self.__addBootstrapNode(host)


    def createNodeName(self, asn: int) -> int:
        if asn not in self.__nodeNames:
            self.__nodeNames[asn] = [int]
            self.__nodeNames[asn].append(99)
            
        # get the list of already created nodes in the AS, create the next with ascending number and append
        asn_node_list = self.__nodeNames[asn]
        newest_node_in_as = asn_node_list[len(asn_node_list)-1]

        node_number = newest_node_in_as + 1
        self.__nodeNames[asn].append(node_number)
        return node_number


###############################################################################
    # adds IP version of btcd to the host  
    def __addNode(self, host: Node):
        # add logging folder
        name = host.getName()
        log_path = self.createNodeDirectory(name)
        host.addSharedFolder('/root/.btcd/logs/mainnet', log_path)

        # add binary and config from the shared folder, make it executable
        host.addSharedFolder('/shared/',self.__wd+'/bin/')
        host.appendStartCommand("cp /shared/btcd /bin/btcd", False)
        host.appendStartCommand("chmod +x /bin/btcd", False)

        # import the config file for a default IP client
        host.importFile(self.__wd+'/configs/node_ip.conf', '/root/.btcd/btcd.conf')

        # on start up wait 15 seconds afterwards start the node
        host.appendStartCommand('btcd --configfile /root/.btcd/btcd.conf', True)

    # adds IP version of btcd to the host with Bootstrap configuration
    def __addBootstrapNode(self, host: Node):
        # add logging folder
        name = host.getName()
        log_path = self.createNodeDirectory(name)
        host.addSharedFolder('/root/.btcd/logs/mainnet', log_path)
        
        # add binary and config from the shared folder, make it executable
        host.addSharedFolder('/shared/',self.__wd+'/bin/')
        host.appendStartCommand("cp /shared/btcd /bin/btcd", False)
        host.appendStartCommand("chmod +x /bin/btcd", False)

        # import the config file for a default IP client
        host.importFile(self.__wd+'/configs/bootstrap_ip.conf', '/root/.btcd/btcd.conf')

        # on start up wait 10 seconds afterwards start the node
        host.appendStartCommand('btcd --configfile /root/.btcd/btcd.conf', True)

    def creatLoggingDirectory(self) -> str:
        base_path = '/home/justus/seed-emulator/examples/scion/data'
        
        # Get a list of all folders in the base directory
        folder_names = os.listdir(base_path)

        # Create a regular expression pattern to match folder names like "log_(int)"
        pattern = r"logs_(\d+)"
        # Extract the integers from folder names that match the pattern
        integers = [int(re.search(pattern, folder).group(1)) for folder in folder_names if re.match(pattern, folder)]
        
        # Find the maximum integer in the list (or start from 0 if no matches found)
        next_int = max(integers) + 1 if integers else 1

        # Path for log dir and nodes sub dirs
        log_path = f"{base_path}/logs_{next_int}"

        # Create log dir
        if os.path.exists(log_path):
            shutil.rmtree(log_path)
        os.mkdir(log_path)
        return log_path


    def createNodeDirectory(self, name: str) -> str:
        full_path = os.path.join(self.log_path, name)
        if os.path.exists(full_path):
            shutil.rmtree(full_path)
        os.mkdir(full_path)
        return full_path


        


