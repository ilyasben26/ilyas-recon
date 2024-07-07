#!/bin/bash

# An example of how ilyas-recon can be used to automate dns validation
# Run the second command 20 times with a 2-minute interval
for i in {1..85}
do
    python3 ilyas-recon.py verify --unverified --date 2024-07-03
    echo "Run $i completed. Waiting a bit before next run ..."
    sleep 30
done

# Schedule system shutdown in 5 minutes
sudo shutdown -h +5
