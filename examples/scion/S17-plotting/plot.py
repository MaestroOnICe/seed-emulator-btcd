import examples.scion.utility.plotdata as plotdata

# ask for log number
log_number = int(input("Which log directory to use: "))

plotdata.plotConnectionCount(f"../data/logs_{log_number}/node_101_100/log.json",log_number)
plotdata.plotConnectionCount(f"../data/logs_{log_number}/node_130_100/log.json", log_number)
plotdata.compareChains(f"../data/logs_{log_number}/node_101_100/log.json", f"../data/logs_{log_number}/node_130_100/log.json", log_number)