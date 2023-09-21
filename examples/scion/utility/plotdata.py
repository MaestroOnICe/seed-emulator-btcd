
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
    sns.set(style="whitegrid")
    sns.lineplot(x="timeElapsed", y="connectionCount", data=df)
    plt.title("Connection Count Over Time")
    plt.xlabel("Time Elapsed (seconds)")
    plt.ylabel("Connection Count")
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

    print(df_1)
    print(df_2)

    # Merge the dataframes and convert timeElapsed to seconds
    merged_df = df_1.merge(df_2, on='hash', suffixes=('_hash1', '_hash2'))
    merged_df['timeElapsed'] = merged_df['timeElapsed'].str.rstrip('ns').astype(int) / 1e9

    # Set Seaborn style
    sns.set_style("whitegrid")

    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))

    # Loop through unique hashes and plot their block numbers over time
    for hash_value, group in merged_df.groupby('hash'):
        sns.lineplot(x='timeElapsed', y='blockCount_hash1', data=group, label=f'Block Count - {hash_value} (Hash 1)')
        sns.lineplot(x='timeElapsed', y='blockCount_hash2', data=group, label=f'Block Count - {hash_value} (Hash 2)')

    # Set labels and title
    ax.set_xlabel('Time (seconds)')
    ax.set_ylabel('Block Number')
    ax.set_title('Comparison of Hashes Over Time')

    # Add legend outside the plot
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    # Show the plot
    plt.show()