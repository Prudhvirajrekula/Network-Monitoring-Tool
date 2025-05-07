import subprocess
import socket
import ipaddress
import threading
import re
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QTabWidget, QLabel, QSizePolicy
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import networkx as nx

class NetworkScannerThread(QThread):
    result_signal = pyqtSignal(list)

    def run(self):
        results = get_arp_table()
        self.result_signal.emit(results)

class GraphCanvas(FigureCanvas):
    def __init__(self, data, parent=None):
        fig = Figure()
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.plot_topology(data)

    def plot_topology(self, data):
        G = nx.Graph()
        for ip, mac, host in data:
            label = f"{host}\n{ip}"
            G.add_node(label)
        for i in range(1, len(G.nodes)):
            G.add_edge(list(G.nodes)[0], list(G.nodes)[i])
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color='skyblue', ax=self.axes, font_size=8)

class NetworkScannerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.tabs = QTabWidget()
        self.list_widget = QTableWidget()
        self.graph_label = QLabel("Click 'Scan' to view network graph")
        self.graph_label.setAlignment(Qt.AlignCenter)

        self.tabs.addTab(self.list_widget, "List View")
        self.tabs.addTab(self.graph_label, "Graph View")

        self.scan_button = QPushButton("Scan Network")
        self.scan_button.clicked.connect(self.start_scan)

        layout = QVBoxLayout()
        layout.addWidget(self.scan_button)
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def start_scan(self):
        self.scan_button.setEnabled(False)
        self.scanner = NetworkScannerThread()
        self.scanner.result_signal.connect(self.display_results)
        self.scanner.start()

    def display_results(self, data):
        self.list_widget.setRowCount(len(data))
        self.list_widget.setColumnCount(3)
        self.list_widget.setHorizontalHeaderLabels(["IP Address", "MAC Address", "Hostname"])
        for row, (ip, mac, host) in enumerate(data):
            self.list_widget.setItem(row, 0, QTableWidgetItem(ip))
            self.list_widget.setItem(row, 1, QTableWidgetItem(mac))
            self.list_widget.setItem(row, 2, QTableWidgetItem(host))
        self.graph_canvas = GraphCanvas(data)
        self.tabs.removeTab(1)
        self.tabs.addTab(self.graph_canvas, "Graph View")
        self.scan_button.setEnabled(True)

def get_local_ip_and_subnet():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip

def get_arp_table():
    arp_output = subprocess.check_output("arp -a", shell=True).decode()
    arp_entries = []
    for line in arp_output.splitlines():
        match = re.search(r"(\d+\.\d+\.\d+\.\d+)\s+([a-fA-F0-9\-]+)", line)
        if match:
            ip, mac = match.groups()
            try:
                hostname = socket.gethostbyaddr(ip)[0]
            except socket.herror:
                hostname = "Unknown"
            arp_entries.append((ip, mac, hostname))
    return arp_entries