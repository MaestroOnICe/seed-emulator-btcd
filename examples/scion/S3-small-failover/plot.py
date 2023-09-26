import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Step 1: Read and parse the log file
log_file = './logs/failover_server.log'

# Initialize a list to store sequence numbers
sequence_numbers = []

# Open the log file and extract sequence numbers
with open(log_file, 'r') as file:
    for line in file:
        if "Sequence Number" in line:
            sequence_number = int(line.split('=')[1].strip().split(',')[0])
            sequence_numbers.append(sequence_number)

# Step 2: Identify missing sequence numbers and calculate failover times
failover_times = []
prev_sequence_number = sequence_numbers[0]

for sequence_number in sequence_numbers[1:]:
    if sequence_number != prev_sequence_number + 1:
        print(prev_sequence_number + 1)
        # A missing sequence number indicates a failover
        failover_time = (sequence_number - prev_sequence_number - 1) * 10  # Multiply by 10 milliseconds
        failover_times.append(failover_time)
    prev_sequence_number = sequence_number

# Step 3: Create a DataFrame for failover times
failover_df = pd.DataFrame({'Failover Time (ms)': failover_times})
print(failover_df)

# # Step 4: Plot a CDF of the failover times
# sns.set_style("whitegrid")
# plt.figure(figsize=(10, 6))
# sns.ecdfplot(data=failover_df, x='Failover Time (ms)', complementary=True)
# plt.title('Cumulative Distribution Function of Failover Times')
# plt.xlabel('Failover Time (ms)')
# plt.ylabel('CDF')
# plt.savefig("./plot/fig_3")
