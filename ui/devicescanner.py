from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView
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
        header = QLabel("<h2>Connected Network Devices</h2>")
        layout.addWidget(header)
        
        # Device table
        self.device_table = QTableWidget()
        self.device_table.setColumnCount(4)
        self.device_table.setHorizontalHeaderLabels(["Device Name", "IP Address", "MAC Address", "Network Adapter Company"])
        self.device_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.device_table)
        
        # Controls
        control_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.scan_devices)
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        
        control_layout.addWidget(self.refresh_button)
        control_layout.addWidget(self.close_button)
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        
        # Set the theme
        self.apply_theme()
        
        # Scan for devices
        self.scan_devices()
    
    def scan_devices(self):
        """Scan the network for connected devices."""
        # Get devices from backend
        devices = get_network_devices()
        
        # Update the table
        self.device_table.setRowCount(len(devices))
        
        for row, device in enumerate(devices):
            self.device_table.setItem(row, 0, QTableWidgetItem(device['name']))
            self.device_table.setItem(row, 1, QTableWidgetItem(device['ip']))
            self.device_table.setItem(row, 2, QTableWidgetItem(device['mac']))
            self.device_table.setItem(row, 3, QTableWidgetItem(device['manufacturer']))
    
    def set_dark_mode(self, enabled):
        """Set dark mode on or off."""
        self.dark_mode = enabled
        self.apply_theme()
    
    def apply_theme(self):
        """Apply the current theme."""
        if self.dark_mode:
            self.setStyleSheet("""
                QWidget {
                    background-color: #2c3e50;
                    color: white;
                }
                QPushButton {
                    background-color: #1abc9c;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                }
                QPushButton:hover {
                    background-color: #16a085;
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
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
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
            """)