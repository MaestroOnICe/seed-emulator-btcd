import examples.scion.utility.plotdata as plotdata
import os

# ask for log number
log_number = int(input("Which log directory to use: "))

node_1_number = (input("First node: "))
node_2_number = (input("Second node: "))

cwd = os.getcwd()
node_1_dir = f"{cwd}/data/logs_{log_number}/node_{node_1_number}/log.json"
node_2_dir = f"{cwd}/data/logs_{log_number}/node_{node_2_number}/log.json"

if not os.path.exists(node_1_dir):
    node_1_dir = f"./old_logs/logs_{log_number}/node_{node_1_number}/log.json"

if not os.path.exists(node_2_dir):
    node_2_dir = f"./old_logs/logs_{log_number}/node_{node_2_number}/log.json"


plotdata.plotConnectionCount(node_1_dir,node_2_dir, node_1_number, node_2_number, log_number)
plotdata.compareChains(node_1_dir, node_2_dir, log_number)

#plotdata.plotCDF(f"../data/logs_{log_number}/node_101_100/log.json",log_number)