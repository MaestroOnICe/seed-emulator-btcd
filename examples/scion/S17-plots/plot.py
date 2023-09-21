import examples.scion.utility.plotdata as plotdata

#plotdata.plotConnectionCount("./logs/node_101_1/log.json")
plotdata.compareChains("./logs/node_101_1/log.json", "./logs/node_130_1/log.json")