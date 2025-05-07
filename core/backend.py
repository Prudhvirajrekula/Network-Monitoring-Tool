import psutil
from collections import defaultdict
import time
import logging
import socket
import requests
import json
import subprocess
import re

# Configure logging to CSV
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s,%(levelname)s,%(message)s",
    handlers=[
        logging.FileHandler("network_monitor_logs.csv"),
        logging.StreamHandler()
    ]
)

# Simulated port states (in-memory storage)
port_states = {}

# Track port activity over time
port_activity = defaultdict(list)

def get_open_ports():
    open_ports = []
    for conn in psutil.net_connections(kind='inet'):
        if conn.status == psutil.CONN_LISTEN:
            port = conn.laddr.port
            try:
                process = psutil.Process(conn.pid)
                process_name = process.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                process_name = "N/A"
            
            open_ports.append({
                'port': port,
                'pid': conn.pid,
                'process_name': process_name,
                'enabled': port_states.get(port, True)  # Default to enabled
            })
            # Track activity for the graph
            port_activity[port].append((time.time(), 1))  # 1 indicates activity
    return open_ports

def get_process_info(pid):
    try:
        process = psutil.Process(pid)
        return {
            'pid': pid,
            'name': process.name(),
            'status': process.status(),
            'create_time': process.create_time(),
            'cpu_percent': process.cpu_percent(),
            'memory_info': process.memory_info().rss
        }
    except psutil.NoSuchProcess:
        return None

def toggle_port_state(port):
    """Toggle the state of a port (enabled/disabled)."""
    if port in port_states:
        port_states[port] = not port_states[port]
    else:
        port_states[port] = False  # Disable the port if it's not in the dictionary
    logging.info(f"Port {port} toggled to {'Enabled' if port_states[port] else 'Disabled'}")
    return port_states[port]

def get_port_activity(port):
    """Get activity data for a specific port."""
    return port_activity.get(port, [])

def get_local_ip():
    """Get the local IP address of the machine."""
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip
    except Exception as e:
        logging.error(f"Error getting local IP: {e}")
        return "N/A"

def get_public_ip_info():
    """Get public IP address information."""
    try:
        response = requests.get('https://ipinfo.io/json', timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Failed to get public IP info: {response.status_code}")
            return {'ip': 'N/A', 'region': 'N/A', 'country': 'N/A', 'org': 'N/A'}
    except Exception as e:
        logging.error(f"Error getting public IP info: {e}")
        return {'ip': 'N/A', 'region': 'N/A', 'country': 'N/A', 'org': 'N/A'}

def get_public_ipv6():
    """Get public IPv6 address."""
    try:
        response = requests.get('https://api6.ipify.org', timeout=5)
        if response.status_code == 200:
            return response.text
        else:
            logging.error(f"Failed to get public IPv6: {response.status_code}")
            return 'N/A'
    except Exception as e:
        logging.error(f"Error getting public IPv6: {e}")
        return 'N/A'

def get_network_devices():
    """Get a list of devices connected to the network."""
    devices = []
    try:
        # Get the local IP to determine the network subnet
        local_ip = get_local_ip()
        if local_ip == "N/A":
            return devices
            
        # Extract the subnet from the IP (e.g., 192.168.1)
        subnet = ".".join(local_ip.split(".")[:3])
        
        # Get ARP table for device discovery
        arp_output = subprocess.check_output("arp -a", shell=True).decode()
        
        # Parse ARP output to extract devices
        for line in arp_output.splitlines():
            match = re.search(r"(\d+\.\d+\.\d+\.\d+)\s+([a-fA-F0-9\-]+)", line)
            if match:
                ip, mac = match.groups()
                # Filter devices in the same subnet
                if ip.startswith(subnet):
                    try:
                        hostname = socket.gethostbyaddr(ip)[0]
                    except socket.herror:
                        hostname = "Unknown"
                    devices.append({
                        'ip': ip,
                        'mac': mac,
                        'hostname': hostname
                    })
        
        return devices
    except Exception as e:
        logging.error(f"Error discovering network devices: {e}")
        return devices