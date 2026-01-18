import socket
import platform
import subprocess
import re

def networkstatus():
    """
    Checks the internet connection status and attempts to identify the connection type.
    """
    status = "Disconnected"
    connection_type = "Unknown"

    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        status = "Connected"
    except OSError:
        status = "Disconnected"

    if status == "Connected":
        system = platform.system()
        if system == "Windows":
            try:
                output = subprocess.check_output("ipconfig", shell=True, text=True)
                if re.search(r"Wireless LAN adapter Wi-Fi", output, re.IGNORECASE):
                    connection_type = "WiFi"
                elif re.search(r"Ethernet adapter Ethernet", output, re.IGNORECASE):
                    connection_type = "Ethernet"
                else:
                    if re.search(r"adapter", output, re.IGNORECASE):
                        if "Wireless" in output or "Wi-Fi" in output:
                            connection_type = "WiFi"
                        elif "Ethernet" in output:
                            connection_type = "Ethernet"
            except subprocess.CalledProcessError:
                pass 

        elif system == "Linux" or system == "Darwin": 
            try:
                route_output = subprocess.check_output("ip route | grep default", shell=True, text=True)
                match = re.search(r"dev (\S+)", route_output)
                if match:
                    interface = match.group(1)
                    if "wlan" in interface or "ath" in interface or "en0" == interface: 
                        connection_type = "WiFi"
                    elif "eth" in interface or "enp" in interface or "en1" == interface: 
                        connection_type = "Ethernet"
                    else:
                        if system == "Linux":
                            try:
                                ethtool_output = subprocess.check_output(f"ethtool {interface}", shell=True, text=True)
                                if "Link detected: yes" in ethtool_output and "duplex" in ethtool_output:
                                    connection_type = "Ethernet"
                                if "Wireless" in subprocess.check_output(f"iw dev {interface} info", shell=True, text=True, stderr=subprocess.DEVNULL):
                                    connection_type = "WiFi"
                            except (subprocess.CalledProcessError, FileNotFoundError):
                                pass 
                        elif system == "Darwin": 
                            try:
                                if "Wi-Fi" in subprocess.check_output(f"networksetup -listallhardwareports | grep -A 1 '{interface}'", shell=True, text=True):
                                    connection_type = "WiFi"
                                elif "Ethernet" in subprocess.check_output(f"networksetup -listallhardwareports | grep -A 1 '{interface}'", shell=True, text=True):
                                    connection_type = "Ethernet"
                            except subprocess.CalledProcessError:
                                pass


            except subprocess.CalledProcessError:
                pass 

    print(f"Status: {status}")
    print(f"Type: {connection_type}")

if __name__ == "__main__":
    networkstatus()