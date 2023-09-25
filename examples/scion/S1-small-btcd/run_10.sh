#!/bin/bash

# Loop 10 times
for ((i = 1; i <= 10; i++)); do
    # Run the command and capture the output
    output=$(eval "$command")

    # Display the run number and output
    echo "Run #$i"
    python3 small.py

    # Optional: Sleep for a few seconds between runs (adjust as needed)
    sleep 5
done
