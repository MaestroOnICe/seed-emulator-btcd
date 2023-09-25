
import seaborn as sns
import matplotlib.pyplot as plt
import json
import pandas as pd
import os
import re


def plotConnectionCount(file_path1: str, file_path2: str, node_1: str, node_2: str, log_number: int, ):
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

    # start after 10 seconds to omit ramp up
    df_1 = df_1.iloc[1:]
    df_2 = df_2.iloc[1:]

    # count unique connections
    df_1["uniqueConCount"] = df_1["connectedPeers"].apply(countUniques)
    df_2["uniqueConCount"] = df_2["connectedPeers"].apply(countUniques)

    # Plot using Seaborn
    sns.set_theme()

    #fig = plt.subplot(figsize=())
    sns.lineplot(x="timeElapsed", y="uniqueConCount", data=df_1, label=node_1, linewidth=2,)
    sns.lineplot(x="timeElapsed", y="uniqueConCount", data=df_2, label=node_2, linewidth=2,)

    plt.axvline(x=100, color='red', linestyle='--', label='Start')
    plt.axvline(x=400, color='blue', linestyle='--', label='End')


    plt.title(f"Connection Count Over Time")
    plt.xlabel("Time Elapsed (seconds)")
    plt.ylabel("Connection Count")



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

    df_1 = df_1.iloc[1:]
    df_2 = df_2.iloc[1:]

    # Plot blockCount over time
    sns.set_style("whitegrid")
    sns.lineplot(x="timeElapsed", y="blockCount", data=df_1, label='Blockchain 1', linewidth=2, marker='o', markersize=6, alpha=1)
    sns.lineplot(x="timeElapsed", y="blockCount", data=df_2, label='Blockchain 2', linewidth=2, marker='s', markersize=6, alpha=0.7)
    plt.axvline(x=100, color='red', linestyle='--', label='Start')
    plt.axvline(x=400, color='blue', linestyle='--', label='End')

    plt.legend(fontsize=12)  # Add a legend
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
    return F"{plot_path}/fig_{next_int}"

###############################################################################
def countUniques(ips):
    unique_entries = set()  # Initialize an empty set to store unique combinations

    for entry in ips:
        ip = entry.split(':')[0]
        if ip not in unique_entries:
            unique_entries.add(ip)  # Add the unique entry to the set
    
    return len(unique_entries)  # Return the count of unique entries