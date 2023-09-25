
import seaborn as sns
import matplotlib.pyplot as plt
import json
import pandas as pd
import os
import re


def plotConnectionCount(file_path1: str, file_path2: str, node_1: str, node_2: str, log_number: int):
    # Read and parse the JSON data from the file
    with open(file_path1, 'r') as json_file:
        data_1 = json.load(json_file)["data"]
    # Create a DataFrame
    df_1 = pd.DataFrame(data_1)

    # Read and parse the JSON data from the file
    with open(file_path2, 'r') as json_file:
        data_2 = json.load(json_file)["data"]
    # Create a DataFrame
    df_2 = pd.DataFrame(data_2)


    datapoint_offset = 1
    # start after x seconds to omit ramp up
    df_1 = df_1.iloc[datapoint_offset:]
    df_2 = df_2.iloc[datapoint_offset:]

    # count unique connections
    df_1["uniqueConCount"] = df_1["connectedPeers"].apply(countUniques)
    df_2["uniqueConCount"] = df_2["connectedPeers"].apply(countUniques)

    # Plot using Seaborn
    sns.set(rc={"figure.dpi":300, 'savefig.dpi':300})
    sns.set_theme()
    #fig = plt.subplot(figsize=())
    sns.lineplot(x="timeElapsed", y="uniqueConCount", data=df_1, label=node_1, linewidth=2,)
    sns.lineplot(x="timeElapsed", y="uniqueConCount", data=df_2, label=node_2, linewidth=2,)

    time_Offset = datapoint_offset*10

    plt.axvline(x=120-time_Offset, color='red', linestyle='--', label='Start')
    plt.axvline(x=600-time_Offset, color='blue', linestyle='--', label='End')

    # Customize the y-axis to display only integers
    plt.yticks(range(0, max(df_1['uniqueConCount']) + 1, 1))
    # Set the x-axis limits to start at 10 seconds
    plt.xlim(time_Offset-10, max(df_1["timeElapsed"]))

    plt.legend(fontsize=8)  # Add a legend
    plt.title(f"Connection Count Over Time")
    plt.xlabel("Time Elapsed (seconds)")
    plt.ylabel("Connection Count")
    plt.tight_layout()  # Ensure the plot fits nicely in the figure


    fig_path = saveFigurePath(log_number)
    plt.savefig(fig_path)
    plt.clf()


def plotVictimConnectionCount(log_path: str,  log_number: int):

    victim_ases = ["node_130_100/log.json", "node_130_101/log.json","node_130_102/log.json", "node_130_103/log.json", "node_130_104/log.json"]
    
    df_dict = {}
    for victim in victim_ases:
        # Read and parse the JSON data from the file
        with open(os.path.join(log_path, victim), 'r') as json_file:
            data = json.load(json_file)["data"]
        # Create a DataFrame
        df = pd.DataFrame(data)
        df["uniqueConCount"] = df["connectedPeers"].apply(countUniques)
        df = df[["uniqueConCount", "timeElapsed"]]
        df["victim"] = victim
        df_dict[victim] = df 


    # Plot using Seaborn
    sns.set(rc={"figure.dpi":300, 'savefig.dpi':300})
    sns.set_theme()

    datapoint_offset = 1
    # start after x seconds to omit ramp up

    for key in df_dict:
        df = df_dict[key]
        df = df.iloc[datapoint_offset:]
        sns.lineplot(x="timeElapsed", y="uniqueConCount", data=df, label=df["victim"], linewidth=1,legend=False)


    time_Offset = datapoint_offset*10

    plt.axvline(x=120-time_Offset, color='red', linestyle='--', label='Start')
    plt.axvline(x=600-time_Offset, color='blue', linestyle='--', label='End')

    # Customize the y-axis to display only integers
    plt.yticks(range(0, max(df['uniqueConCount']) + 1, 1))
    # Set the x-axis limits to start at 10 seconds
    plt.xlim(time_Offset-10, max(df["timeElapsed"]))

    plt.title(f"Connection Count Over Time")
    plt.xlabel("Time Elapsed (seconds)")
    plt.ylabel("Connection Count")
    #plt.tight_layout()  # Ensure the plot fits nicely in the figure


    fig_path = saveFigurePath(log_number)
    plt.savefig(fig_path)
    plt.clf()


###############################################################################
def compareChains(file_path1: str, file_path2: str, log_number: int):
    # Read and parse the JSON data from the file
    with open(file_path1, 'r') as json_file:
        data_1 = json.load(json_file)["data"]
    # Create a DataFrame
    df_1 = pd.DataFrame(data_1)

    # Read and parse the JSON data from the file
    with open(file_path2, 'r') as json_file:
        data_2 = json.load(json_file)["data"]
    # Create a DataFrame
    df_2 = pd.DataFrame(data_2)

    # compute 

    # 10 by default, beause sleep 10 for measure
    datapoint_offset = 1
    # start after x seconds to omit ramp up
    df_1 = df_1.iloc[datapoint_offset:]
    df_2 = df_2.iloc[datapoint_offset:]

    # Plot blockCount over time
    sns.set(rc={"figure.dpi":300, 'savefig.dpi':300})
    sns.set_theme()
    sns.lineplot(x="timeElapsed", y="blockCount", data=df_1, label='Blockchain 1', linewidth=2, marker='o', markersize=6, alpha=1)
    sns.lineplot(x="timeElapsed", y="blockCount", data=df_2, label='Blockchain 2', linewidth=2, marker='s', markersize=6, alpha=0.7)
    
    time_Offset = datapoint_offset*10

    plt.axvline(x=120-time_Offset, color='red', linestyle='--', label='Start')
    plt.axvline(x=600-time_Offset, color='blue', linestyle='--', label='End')
    plt.legend(fontsize=8)  # Add a legend
    plt.xlabel('Time Elapsed (seconds)')
    plt.ylabel('Block Count')
    plt.title('Block Count Over Time')
    plt.tight_layout()  # Ensure the plot fits nicely in the figure

    fig_path = saveFigurePath(log_number)
    plt.savefig(fig_path,dpi=300)
    plt.clf()


###############################################################################
def plotCDF(file_path: str, log_number: int):
    # Read and parse the JSON data from the file
    with open(file_path, 'r') as json_file:
        data_1 = json.load(json_file)["data"]
    # Create a DataFrame
    df = pd.DataFrame(data_1)

    connection_count = []

    for value in df["connectionCount"]:
        connection_count.append(value)


    # Create CDF plot
    sns.ecdfplot(connection_count)

    # Customize the plot
    plt.xlabel("Connection Count")
    plt.ylabel("Cumulative Probability")
    plt.title("CDF Plot of Data")
    plt.show()
    # fig_path = saveFigurePath(log_number)
    # plt.savefig(fig_path)
    # plt.clf()

###############################################################################
def saveFigurePath(log_number: int)->str:
    base_path = '/home/justus/seed-emulator/examples/scion/plots'
    plot_path = f'{base_path}/plot_{log_number}'

    # Create log dir
    if not (os.path.exists(plot_path)):
        os.mkdir(plot_path)
        
    # Get a list of all folders in the base directory
    all_figs = os.listdir(plot_path)

    # Create a regular expression pattern to match folder names like "log_(int)"
    pattern = r"fig_(\d+)"
    # Extract the integers from folder names that match the pattern
    integers = [int(re.search(pattern, folder).group(1)) for folder in all_figs if re.match(pattern, folder)]
    
    # Find the maximum integer in the list (or start from 0 if no matches found)
    next_int = max(integers) + 1 if integers else 1

    # Path for next fig is
    return F"{plot_path}/fig_{next_int}.pdf"

###############################################################################
def countUniques(ips):
    unique_entries = set()  # Initialize an empty set to store unique combinations

    for entry in ips:
        ip = entry.split(':')[0]
        if ip not in unique_entries:
            unique_entries.add(ip)  # Add the unique entry to the set
    
    return len(unique_entries)  # Return the count of unique entries