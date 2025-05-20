import subprocess
import bisect


def wifi_resolver(interface):
    ssid = None
    strength = None
    min_strength = 0
    max_strength = 100
    icons = ["󰤯", "󰤟", "󰤢", "󰤥", "󰤨"]

    try:
        # Get SSID connected on the interface
        ssid_result = subprocess.run(
            ["nmcli", "-t", "-f", "DEVICE,ACTIVE,SSID", "device", "wifi"],
            capture_output=True,
            text=True,
            check=True,
        )
        for line in ssid_result.stdout.strip().split("\n"):
            parts = line.split(":", 2)
            if len(parts) < 3:
                continue
            device, active, current_ssid = parts
            if device == interface and active == "yes":
                ssid = current_ssid
                break

        # Get signal strength (%)
        strength_result = subprocess.run(
            ["nmcli", "-t", "-f", "DEVICE,ACTIVE,SIGNAL", "device", "wifi"],
            capture_output=True,
            text=True,
            check=True,
        )
        for line in strength_result.stdout.strip().split("\n"):
            parts = line.split(":", 2)
            if len(parts) < 3:
                continue
            device, active, signal = parts
            if device == interface and active == "yes":
                strength = int(signal)
                break

    except Exception as e:
        print(f"wifi_resolver: something went wrong: {e}")
        ssid = None
        strength = None

    boundaries = list(
        range(
            min_strength + (max_strength - min_strength + 1) // len(icons),
            max_strength,
            (max_strength - min_strength + 1) // len(icons),
        )
    )
    index = bisect.bisect_right(boundaries, strength if strength is not None else 0)
    return {"ssid": ssid, "strength": strength, "icon": icons[index]}
