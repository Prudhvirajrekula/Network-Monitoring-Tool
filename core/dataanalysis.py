import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import random
from collections import defaultdict
import time
import psutil
import socket
from datetime import datetime

class DataAnalysis:
    def __init__(self):
        self.port_activity = defaultdict(list)
        self.connection_data = []
        self.bandwidth_data = []
        self.protocol_data = {'TCP': 0, 'UDP': 0, 'ICMP': 0, 'Other': 0}
        self.ip_activity = defaultdict(int)
        self.packet_loss_data = []
        
        # Initialize with some historical data
        self._initialize_sample_data()

    def _initialize_sample_data(self):
        """Initialize with some sample data for demonstration."""
        # Generate 24 hours of bandwidth data
        now = time.time()
        for i in range(24):
            timestamp = now - (24 - i) * 3600
            self.bandwidth_data.append((timestamp, random.randint(100, 1000)))
        
        # Generate protocol distribution
        self.protocol_data = {
            'TCP': random.randint(500, 1000),
            'UDP': random.randint(200, 500),
            'ICMP': random.randint(50, 200),
            'Other': random.randint(10, 100)
        }
        
        # Generate IP activity
        for i in range(10):
            ip = f"192.168.1.{i+1}"
            self.ip_activity[ip] = random.randint(100, 1000)
        
        # Generate packet loss data
        for i in range(24):
            timestamp = now - (24 - i) * 3600
            self.packet_loss_data.append((timestamp, random.random() * 5))
    
    def generate_bandwidth_usage(self):
        """Generate a line chart for bandwidth usage over time."""
        fig = Figure()
        ax = fig.add_subplot(111)
        
        timestamps = [datetime.fromtimestamp(ts) for ts, _ in self.bandwidth_data]
        values = [val for _, val in self.bandwidth_data]
        
        ax.plot(timestamps, values, 'b-')
        ax.set_title("Bandwidth Usage Over Time")
        ax.set_xlabel("Time")
        ax.set_ylabel("Bandwidth (Mbps)")
        ax.grid(True)
        fig.autofmt_xdate()
        return fig

    def generate_top_talkers(self):
        """Generate a bar chart for most active IPs."""
        fig = Figure()
        ax = fig.add_subplot(111)
        
        ips = list(self.ip_activity.keys())
        counts = list(self.ip_activity.values())
        
        ax.bar(ips, counts)
        ax.set_title("Top Talkers (Most Active IPs)")
        ax.set_xlabel("IP Address")
        ax.set_ylabel("Packets Sent/Received")
        ax.tick_params(axis='x', rotation=45)
        return fig

    def generate_protocol_distribution(self):
        """Generate a pie chart for protocol distribution (TCP and UDP only)."""
        fig = Figure()
        ax = fig.add_subplot(111)
        
        # Only TCP and UDP data
        protocols = ["TCP", "UDP"]
        usage = [random.randint(500, 1000), random.randint(200, 500)]  # TCP always higher than UDP
        
        ax.pie(usage, labels=protocols, autopct="%1.1f%%", startangle=90)
        ax.set_title("Protocol Distribution (TCP vs UDP)")
        return fig

    def generate_packet_loss(self):
        """Generate a line chart for packet drop rate over time."""
        fig = Figure()
        ax = fig.add_subplot(111)
        
        timestamps = [datetime.fromtimestamp(ts) for ts, _ in self.packet_loss_data]
        rates = [rate for _, rate in self.packet_loss_data]
        
        ax.plot(timestamps, rates, 'r-')
        ax.set_title("Packet Drop Rate Over Time")
        ax.set_xlabel("Time")
        ax.set_ylabel("Drop Rate (%)")
        ax.grid(True)
        fig.autofmt_xdate()
        return fig

    def generate_latency_histogram(self):
        """Generate a histogram for connection durations."""
        fig = Figure()
        ax = fig.add_subplot(111)
        
        # Simulate latency data (in milliseconds)
        latencies = np.random.normal(50, 15, 1000)
        
        ax.hist(latencies, bins=30, edgecolor='black')
        ax.set_title("Connection Latency Distribution")
        ax.set_xlabel("Latency (ms)")
        ax.set_ylabel("Frequency")
        return fig