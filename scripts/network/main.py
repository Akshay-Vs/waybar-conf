#!/usr/bin/env python3

import subprocess
import json
import psutil
import socket
from typing import Optional
from dataclasses import dataclass
import resolvers


@dataclass
class NetworkInfo:
    interface: str = ""
    ip: str = ""
    type: str = ""
    icon: str = ""
    ssid: Optional[str] = None
    strength: Optional[int] = None


class NetworkInterface:
    def __init__(self):
        self.interface = self.get_default_interface()
        self.details = NetworkInfo(interface=self.interface)

    def get_default_interface(self):
        try:
            route = subprocess.check_output(["ip", "route", "get", "1.1.1.1"]).decode()
            parts = route.strip().split()
            if "dev" in parts:
                return parts[parts.index("dev") + 1]
        except Exception:
            return None

    def get_interface_details(self):
        # Get IP address
        addrs = psutil.net_if_addrs().get(self.interface, [])
        for addr in addrs:
            if addr.family == socket.AF_INET:
                self.details.ip = addr.address

        # Determine interface type
        try:
            uevent_path = f"/sys/class/net/{self.interface}/uevent"
            with open(uevent_path) as f:
                uevent = f.read()
                if "DEVTYPE=wlan" in uevent or (
                    "INTERFACE=" in uevent and "wl" in self.interface
                ):
                    self.details.type = "wifi"
        except Exception:
            pass

        # If not WiFi, fall back to pattern-based detection
        if self.details.type == "":
            if self.interface.startswith("enx") or self.interface.startswith("usb"):
                self.details.type = "usb"
            elif self.interface.startswith("en"):
                self.details.type = "ethernet"
            else:
                self.details.type = "unknown"

        # If WiFi, enrich with SSID and strength
        if self.details.type == "wifi":
            wifi_data = resolvers.wifi_resolver(self.interface)
            self.details.ssid = wifi_data["ssid"]
            self.details.strength = wifi_data["strength"]
            self.details.icon = wifi_data["icon"]

        # Other interfaces
        elif self.details.type == "usb":
            self.details.icon = "󰕓"
            self.details.ssid = "USB"
        elif self.details.type == "ethernet":
            self.details.icon = "󰈀"
            self.details.ssid = "ETHR"

        else:
            self.details.icon = ""  # unknown interface

        return self.details


if __name__ == "__main__":
    my_network = NetworkInterface()
    details = my_network.get_interface_details()

    output = {
        "text": f"{details.icon}  {details.ssid or details.interface}",
        "tooltip": f"IP: {details.ip}, Type: {details.type}, Signal: {details.strength or 'N/A'}%",
        "class": details.type,
        "percentage": details.strength or 0,
    }

    print(json.dumps(output))
