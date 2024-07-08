#!/bin/bash

# An example of how ilyas-recon can be used to automate DNS validation
# Run this script overnight since

iterations=50

for (( i=1; i<=$iterations; i++ ))
do
    python3 /path/to/ilyas-recon.py verify --unverified
    echo "Run $i completed. Waiting a bit before next run ..."
    sleep 30
done

# Schedule system shutdown in 5 minutes
sudo shutdown -h +5