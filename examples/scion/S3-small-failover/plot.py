import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt



###############################################################################
def readLogFile(path: str, protocol: str):
    # Initialize a list to store sequence numbers
    sequence_numbers = []

    # Open the log file and extract sequence numbers
    with open(path, 'r') as file:
        for line in file:
            if "Sequence Number" in line:
                sequence_number = int(line.split('=')[1].strip().split(',')[0])
                sequence_numbers.append(sequence_number)


    current_sequence = None
    missing_sequences = []
    missing_sequence_groups = []

    for sequence in sequence_numbers:
        if current_sequence is None:
            current_sequence = sequence
        if sequence == current_sequence:
            current_sequence += 1
        elif sequence > current_sequence:
            missing_sequences.extend(range(current_sequence, sequence))
            current_sequence = sequence + 1

    missing_sequences.sort()
    current_group = []

    for num in missing_sequences:
        if not current_group or num == current_group[-1] + 1:
            current_group.append(num)
        else:
            missing_sequence_groups.append(current_group.copy())
            current_group = [num]

    if current_group:
        missing_sequence_groups.append(current_group)

    group_counts = [len(group) for group in missing_sequence_groups]
    
    # packets are currently measured in 0.1ms = 100us per sequence number
    # figure scale should be in ms

    # for index in range(len(group_counts)):
    #     group_counts[index] =  group_counts[index] / 10 

    df = pd.DataFrame({
    'Protocol': protocol,
    'Failover Time (ms)': group_counts,
    })
    return df

log_file_scion = './logs/failover_server.log'
log_file_bgp = './logs/failover_tcp_server.log'

df_scion = readLogFile(log_file_scion, "SCION")
df_bgp = readLogFile(log_file_bgp, "BGP")
print(df_scion)

print(df_bgp)
df = pd.merge(df_scion, df_bgp, how="outer")
print(df)


sns.set_theme()
# Plot CDFs
sns.ecdfplot(x='Failover Time (ms)', data=df, hue="Protocol")
#sns.ecdfplot(x='Failover Time (ms)', data=df_bgp)
# Customize the plot
plt.xlabel("Failover time in ms")
plt.ylabel("Cumulative Probability")
plt.title("CDF of Failover Times")
plt.tight_layout()
plt.savefig("./fig2.pdf")
plt.clf()
