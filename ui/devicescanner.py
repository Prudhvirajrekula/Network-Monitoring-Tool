from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt
from core.backend import get_network_devices

class DeviceScanner(QWidget):
    def __init__(self, dark_mode=False):
        super().__init__()
        self.setWindowTitle("Connected Devices")
        self.setMinimumSize(600, 400)
        self.dark_mode = dark_mode
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("<h2>Connected Network Devices (IPv4 Only)</h2>")
        layout.addWidget(header)
        
        # Device table
        self.device_table = QTableWidget()
        self.device_table.setColumnCount(4)
        self.device_table.setHorizontalHeaderLabels([
            "Device Name", "IP Address", "MAC Address", "Network Adapter Company"
        ])
        self.device_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        layout.addWidget(self.device_table)
        
        # Apply theme
        self.apply_theme()
        
        # Initial scan
        self.scan_devices()
    
    def scan_devices(self):
        """Scan the network for connected IPv4 devices and populate the table."""
        devices = get_network_devices()
        # Filter out any entries whose IP contains ':' (i.e. IPv6)
        ipv4_devices = [
            d for d in devices
            if 'ip' in d and isinstance(d['ip'], str) and ':' not in d['ip']
        ]
        
        self.device_table.setRowCount(len(ipv4_devices))
        
        for row, device in enumerate(ipv4_devices):
            # Safely get each field, defaulting to 'Unknown' if missing
            name = device.get('name', 'Unknown')
            ip   = device.get('ip', 'Unknown')
            mac  = device.get('mac', 'Unknown')
            mfr  = device.get('manufacturer', 'Unknown')
            
            self.device_table.setItem(row, 0, QTableWidgetItem(name))
            self.device_table.setItem(row, 1, QTableWidgetItem(ip))
            self.device_table.setItem(row, 2, QTableWidgetItem(mac))
            self.device_table.setItem(row, 3, QTableWidgetItem(mfr))
    
    def set_dark_mode(self, enabled):
        """Enable or disable dark mode theme."""
        self.dark_mode = enabled
        self.apply_theme()
    
    def apply_theme(self):
        """Apply the current light or dark theme to the widget."""
        if self.dark_mode:
            self.setStyleSheet("""
                QWidget {
                    background-color: #2c3e50;
                    color: white;
                }
                QTableWidget {
                    background-color: #34495e;
                    color: white;
                    gridline-color: #3a3f44;
                    border: none;
                }
                QHeaderView::section {
                    background-color: #2c3e50;
                    color: white;
                    border: 1px solid #3a3f44;
                }
                QTableCornerButton::section {
                    background-color: #2c3e50;
                    border: 1px solid #3a3f44;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #ecf0f1;
                    color: black;
                }
                QTableWidget {
                    background-color: white;
                    color: black;
                    gridline-color: #bdc3c7;
                    border: none;
                }
                QHeaderView::section {
                    background-color: #dfe6e9;
                    color: black;
                    border: 1px solid #bdc3c7;
                }
                QTableCornerButton::section {
                    background-color: #dfe6e9;
                    border: 1px solid #bdc3c7;
                }
            """)
