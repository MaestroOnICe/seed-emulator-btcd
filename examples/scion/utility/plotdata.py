
import seaborn as sns
import matplotlib.pyplot as plt
import json
import pandas as pd
import os
import re


def plotConnectionCount(file_path: str, log_number: int):
    # Read and parse the JSON data from the file
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)["data"]
    
    # Create a DataFrame
    df = pd.DataFrame(data)

    # Plot using Seaborn
    sns.set_theme()
    sns.lineplot(x="timeElapsed", y="connectionCount", data=df, label='Data Series', linewidth=2)
    plt.title("Connection Count Over Time")
    plt.xlabel("Time Elapsed (seconds)")
    plt.ylabel("Connection Count")

    sns.despine(left=True, bottom=True)  # Remove top and right spines
    plt.legend(fontsize=12)  # Add a legend


    fig_path = saveFigurePath(log_number)
    plt.savefig(fig_path)
    plt.clf()

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

    # Plot blockCount over time
    sns.set_theme()
    sns.lineplot(x="timeElapsed", y="blockCount", data=df_1, label='Blockchain 1', linewidth=2, marker='o', markersize=6, alpha=1)
    sns.lineplot(x="timeElapsed", y="blockCount", data=df_2, label='Blockchain 2', linewidth=2, marker='s', markersize=6, alpha=0.7)
    sns.despine(left=True, bottom=True)  # Remove top and right spines
    plt.legend(fontsize=12)  # Add a legend
    plt.xlabel('Time Elapsed (seconds)')
    plt.ylabel('Block Count')
    plt.title('Block Count Over Time')
    plt.tight_layout()  # Ensure the plot fits nicely in the figure

    fig_path = saveFigurePath(log_number)
    plt.savefig(fig_path)
    plt.clf()


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