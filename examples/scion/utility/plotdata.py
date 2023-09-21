
import seaborn as sns
import matplotlib.pyplot as plt
import json
import pandas as pd


def plotConnectionCount(file_path: str):
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
    plt.savefig("./plots/", dpi=1000)
    plt.show()

def compareChains(file_path1: str, file_path2: str):
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
    sns.lineplot(x="timeElapsed", y="blockCount", data=df_1, label='Line 1', linewidth=2, marker='o', markersize=8, alpha=0.7)
    sns.lineplot(x="timeElapsed", y="blockCount", data=df_2, label='Line 2', linewidth=2, marker='s', markersize=8, alpha=0.7)
    sns.despine(left=True, bottom=True)  # Remove top and right spines
    plt.legend(fontsize=12)  # Add a legend
    plt.xlabel('Time Elapsed (seconds)')
    plt.ylabel('Block Count')
    plt.title('Block Count Over Time')
    plt.tight_layout()  # Ensure the plot fits nicely in the figure
    # plt.grid(True)
    plt.show()
