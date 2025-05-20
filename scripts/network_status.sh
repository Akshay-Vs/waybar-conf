#!/bin/bash

# Custom network script for Waybar
# Shows WiFi icon according to strength
# Shows USB icon for USB networking
# No Ethernet support (device has no Ethernet port)

# Interface names - modify these if your interfaces have different names
WIFI_INTERFACE="wlp0s20f3" # WiFi interface
USB_INTERFACE="enp0s20f0u2"  # USB network interface

# Check WiFi status and signal strength
check_wifi() {
    # Check if the interface exists and is up
    if [[ -d "/sys/class/net/$WIFI_INTERFACE" && "$(cat /sys/class/net/$WIFI_INTERFACE/operstate)" != "down" ]]; then
        # Get WiFi information using iw
        SIGNAL=$(iw dev $WIFI_INTERFACE link | grep 'signal' | awk '{print $2}')
        SSID=$(iw dev $WIFI_INTERFACE link | grep 'SSID' | awk '{print $2}')
        
        # If we have a signal strength value, connection is active
        if [[ -n "$SIGNAL" ]]; then
            # Convert dBm to percentage (rough approximation)
            # -50 dBm or higher is ~100%, -100 dBm or lower is ~0%
            SIGNAL_NUM=${SIGNAL%% *}
            SIGNAL_PERCENT=$(( (SIGNAL_NUM + 100) * 2 ))
            
            # Clamp percentage between 0 and 100
            if [[ $SIGNAL_PERCENT -gt 100 ]]; then
                SIGNAL_PERCENT=100
            elif [[ $SIGNAL_PERCENT -lt 0 ]]; then
                SIGNAL_PERCENT=0
            fi
            
            # Select icon based on signal strength
            if [[ $SIGNAL_PERCENT -ge 80 ]]; then
                ICON="󰤨"  # High signal
            elif [[ $SIGNAL_PERCENT -ge 60 ]]; then
                ICON="󰤥"  # Good signal
            elif [[ $SIGNAL_PERCENT -ge 40 ]]; then
                ICON="󰤢"  # Medium signal
            elif [[ $SIGNAL_PERCENT -ge 20 ]]; then
                ICON="󰤟"  # Low signal
            else
                ICON="󰤯"  # Very low signal
            fi
            
            # Get IP address
            IP=$(ip addr show $WIFI_INTERFACE | grep -oP 'inet \K[\d.]+')
            
            # Output JSON for Waybar
            echo "{\"text\": \"$ICON  $SSID\", \"tooltip\": \"WiFi: $SSID\\nSignal: $SIGNAL_PERCENT%\\nIP: $IP\", \"class\": \"wifi\", \"percentage\": $SIGNAL_PERCENT}"
            exit 0
        fi
    fi
    
    # Not connected to WiFi
    return 1
}

# Check USB network status
check_usb_network() {
    # Check if the USB network interface exists and is up
    if [[ -d "/sys/class/net/$USB_INTERFACE" && "$(cat /sys/class/net/$USB_INTERFACE/operstate)" == "up" ]]; then
        # Get IP address
        IP=$(ip addr show $USB_INTERFACE | grep -oP 'inet \K[\d.]+')
        
        if [[ -n "$IP" ]]; then
            # Output JSON for Waybar
            echo "{\"text\": \"󰈀  USB\", \"tooltip\": \"USB Network\\nIP: $IP\", \"class\": \"usb\"}"
            exit 0
        fi
    fi
    
    # Not connected to USB network
    return 1
}

# Try WiFi first, then USB network
check_wifi || check_usb_network || echo "{\"text\": \"\", \"tooltip\": \"Disconnected\", \"class\": \"disconnected\"}"