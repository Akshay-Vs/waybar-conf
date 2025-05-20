#!/bin/bash

# Get the latest clipboard entry
latest_entry=$(cliphist list | head -n 1)

# Limit length to avoid breaking the bar
max_length=50
if [[ ${#latest_entry} -gt $max_length ]]; then
    latest_entry="${latest_entry:0:$max_length}..."
fi

# Print the entry to Waybar
echo "{\"text\": \"$latest_entry\", \"tooltip\": \"$latest_entry\"}"
