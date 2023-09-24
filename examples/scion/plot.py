import examples.scion.utility.plotdata as plotdata

# ask for log number
log_number = int(input("Which log directory to use: "))

node_1 = int(input("First node: "))
node_2 = int(input("Second node: "))

plotdata.plotConnectionCount(f"./data/logs_{log_number}/node_{node_1}_100/log.json",log_number)
#plotdata.plotConnectionCount(f"./data/logs_{log_number}/node_{node_2}_100/log.json", log_number)
#plotdata.compareChains(f"./data/logs_{log_number}/node_{node_1}_100/log.json", f"./data/logs_{log_number}/node_{node_2}_100/log.json", log_number)

#plotdata.plotCDF(f"../data/logs_{log_number}/node_101_100/log.json",log_number)