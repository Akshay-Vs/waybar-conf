#!/bin/bash

# Kill all existing Waybar instances
pkill -x waybar

# Wait for them to fully exit
sleep 0.05

# Relaunch Waybar in background
waybar & disown
