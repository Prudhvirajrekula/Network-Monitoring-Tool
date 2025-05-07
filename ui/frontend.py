from PyQt5.QtCore import Qt, QTimer, QSize, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget, QPushButton, QHeaderView, QHBoxLayout, QLabel,
    QTextEdit, QGridLayout, QStackedWidget, QMenuBar, QLineEdit, QListWidget,
    QFrame
)
from PyQt5.QtGui import QColor, QBrush, QFont, QPalette
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import logging
import sys
import threading
import time
import psutil
from datetime import datetime

from core.backend import get_open_ports, get_process_info, toggle_port_state, get_local_ip
from core.backend import get_public_ip_info, get_public_ipv6, get_network_devices
from core.dataanalysis import DataAnalysis
from core.reports import ReportGenerator
from ui.networkscanner import NetworkScannerWidget
from ui.portblocker import PortBlocker
from ui.tracevisualizer import TraceVisualizer
from ui.navigation_panel import create_navigation_panel
from ui.toolbar import create_toolbar
from ui.settings import setup_settings_page
from ui.info import setup_info_page, update_info_theme
from ui.help import setup_help_page
from ui.devicescanner import DeviceScanner

pages_order = [
    "🏠 Home", "📊 Data Analysis", "📑 Reports", "🔍 Network Scanner",
    "🔒 Port Blocker", "🌐 Trace Visualizer", "⚙ Settings", " ℹ Information", "❓ Help"
]

class NetworkMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Network Monitoring & Port Scanning Tool")
        self.setGeometry(100, 100, 1280, 720)
        self.dark_mode = False
        self.data_analysis = DataAnalysis()
        self.report_generator = ReportGenerator()
        self.public_ip_info = {'ip': 'Loading...', 'region': 'Loading...', 'country': 'Loading...', 'org': 'Loading...', 'city': 'Loading...'}
        self.public_ipv6 = 'Loading...'
        self.device_scanner_window = None

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        # Sidebar
        self.sidebar_container = create_navigation_panel(pages_order, self.switch_page, self.dark_mode)
        self.main_layout.addWidget(self.sidebar_container)


        # Content area
        self.content_area = QStackedWidget()
        self.main_layout.addWidget(self.content_area)
        self.pages = {}

        for page_name in [
            "Home", "Data Analysis", "Reports", "Network Scanner",
            "Port Blocker", "Trace Visualizer", "Settings", "Information", "Help"
        ]:
            page = QWidget()
            layout = QGridLayout() if page_name == "Data Analysis" else QVBoxLayout()
            page.setLayout(layout)
            self.content_area.addWidget(page)
            self.pages[page_name] = page

        self.setup_home_page()
        self.setup_data_analysis_page()
        self.setup_reports_page()
        self.setup_network_scanner_page()
        self.setup_port_blocker_page()
        self.setup_trace_visualizer_page()

        self.dark_mode_button, self.refresh_rate_button = setup_settings_page(
            self.pages["Settings"].layout(), self.toggle_dark_mode, self.change_refresh_rate
        )

        setup_info_page(self.pages["Information"].layout(), self.dark_mode)
        setup_help_page(self.pages["Help"].layout())

        # Ensure the page header titles inherit the text color properly
        self.content_area.currentChanged.connect(self.update_page_title_colors)

        self.report_generator.report_generated.connect(self.display_report)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_monitoring)
        self.timer.start(3000)

        self.menu_bar = create_toolbar(self, self.update_monitoring, self.menu_action)
        self.setMenuBar(self.menu_bar)
        
        # Start fetching IP information in a separate thread
        threading.Thread(target=self.fetch_ip_info, daemon=True).start()

    def setup_home_page(self):
        """Sets up the Home page with network traffic and port monitoring tables."""
        home_layout = self.pages["Home"].layout()
        
        # Network Traffic Section
        home_layout.addWidget(QLabel("<h2>Network Traffic</h2>"))
        
        # IP Information Panel
        ip_info_frame = QFrame()
        ip_info_frame.setFrameShape(QFrame.StyledPanel)
        ip_info_frame.setFrameShadow(QFrame.Raised)
        ip_info_layout = QGridLayout(ip_info_frame)
        
        # My IP Address header
        ip_header = QLabel("My IP Address is:")
        ip_header.setStyleSheet("font-weight: bold; font-size: 14px;")
        ip_info_layout.addWidget(ip_header, 0, 0, 1, 2)
        
        # IPv6 information
        ipv6_label = QLabel("IPv6:")
        self.ipv6_value = QLabel(self.public_ipv6)
        ip_info_layout.addWidget(ipv6_label, 1, 0)
        ip_info_layout.addWidget(self.ipv6_value, 1, 1)
        
        # IPv4 information
        ipv4_label = QLabel("IPv4:")
        self.ipv4_value = QLabel(self.public_ip_info['ip'])
        ip_info_layout.addWidget(ipv4_label, 2, 0)
        ip_info_layout.addWidget(self.ipv4_value, 2, 1)
        
        # ISP information
        isp_label = QLabel("ISP:")
        self.isp_label = QLabel(self.public_ip_info['org'])
        ip_info_layout.addWidget(isp_label, 3, 0)
        ip_info_layout.addWidget(self.isp_label, 3, 1)
        
        # City information
        city_label = QLabel("City:")
        self.city_label = QLabel(self.public_ip_info.get('city', 'N/A'))
        ip_info_layout.addWidget(city_label, 4, 0)
        ip_info_layout.addWidget(self.city_label, 4, 1)
        
        # Region information
        region_label = QLabel("Region:")
        self.region_label = QLabel(self.public_ip_info['region'])
        ip_info_layout.addWidget(region_label, 5, 0)
        ip_info_layout.addWidget(self.region_label, 5, 1)
        
        # Country information
        country_label = QLabel("Country:")
        self.country_label = QLabel(self.public_ip_info['country'])
        ip_info_layout.addWidget(country_label, 6, 0)
        ip_info_layout.addWidget(self.country_label, 6, 1)
        
        # Button to scan for network devices
        devices_button = QPushButton("See Connected Devices")
        devices_button.clicked.connect(self.show_connected_devices)
        ip_info_layout.addWidget(devices_button, 7, 0, 1, 2)
        
        home_layout.addWidget(ip_info_frame)

        # Port Monitoring Table
        home_layout.addWidget(QLabel("<h2>Port Monitoring</h2>"))
        self.ports_table = QTableWidget()
        self.ports_table.setColumnCount(6)
        self.ports_table.setHorizontalHeaderLabels(["Port", "PID", "Protocol", "Process Name", "CPU Usage", "Status"])
        self.ports_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        home_layout.addWidget(self.ports_table)

        # Buttons
        button_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh", self)
        self.refresh_button.clicked.connect(self.update_monitoring)
        self.toggle_button = QPushButton("Toggle Port", self)
        self.toggle_button.clicked.connect(self.toggle_selected_port)
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.toggle_button)
        home_layout.addLayout(button_layout)
        
        # Initialize the ports table
        self.update_ports_table()

    def setup_data_analysis_page(self):
        """Sets up the Data Analysis page with various visualization options."""
        data_layout = self.pages["Data Analysis"].layout()
        
        # Clear any existing widgets
        for i in reversed(range(data_layout.count())): 
            data_layout.itemAt(i).widget().setParent(None)
        
        # Add header
        header_label = QLabel("<h2>Network Data Analysis Dashboard</h2>")
        data_layout.addWidget(header_label, 0, 0, 1, 2)  # Span across 2 columns
        
        # Create buttons for different visualizations
        button_grid = QGridLayout()
        
        self.bandwidth_btn = QPushButton("Bandwidth Usage")
        self.bandwidth_btn.clicked.connect(lambda: self.show_graph(self.data_analysis.generate_bandwidth_usage()))
        button_grid.addWidget(self.bandwidth_btn, 0, 0)
        
        self.talkers_btn = QPushButton("Top Talkers")
        self.talkers_btn.clicked.connect(lambda: self.show_graph(self.data_analysis.generate_top_talkers()))
        button_grid.addWidget(self.talkers_btn, 0, 1)
        
        self.protocol_btn = QPushButton("Protocol Distribution")
        self.protocol_btn.clicked.connect(lambda: self.show_graph(self.data_analysis.generate_protocol_distribution()))
        button_grid.addWidget(self.protocol_btn, 1, 0)
        
        self.packet_loss_btn = QPushButton("Packet Loss")
        self.packet_loss_btn.clicked.connect(lambda: self.show_graph(self.data_analysis.generate_packet_loss()))
        button_grid.addWidget(self.packet_loss_btn, 1, 1)
        
        self.latency_btn = QPushButton("Connection Latency")
        self.latency_btn.clicked.connect(lambda: self.show_graph(self.data_analysis.generate_latency_histogram()))
        button_grid.addWidget(self.latency_btn, 2, 0)
        
        # Add the button grid to the main layout
        data_layout.addLayout(button_grid, 1, 0, 1, 2)  # Add at row 1, span 1 row and 2 columns
        
        # Canvas for displaying graphs
        self.graph_canvas = FigureCanvas(Figure())
        self.graph_canvas.setMinimumSize(800, 500)
        data_layout.addWidget(self.graph_canvas, 2, 0, 1, 2)  # Add at row 2, span 1 row and 2 columns
        
        # Initialize with bandwidth usage graph
        self.show_graph(self.data_analysis.generate_bandwidth_usage())

    def setup_network_scanner_page(self):
        """Sets up the Network Scanner page."""
        scanner_layout = self.pages["Network Scanner"].layout()
        self.network_scanner = NetworkScannerWidget()
        scanner_layout.addWidget(self.network_scanner)

    def setup_reports_page(self):
        """Sets up the Reports page with various report options."""
        reports_layout = self.pages["Reports"].layout()
        
        # Clear any existing widgets
        for i in reversed(range(reports_layout.count())): 
            reports_layout.itemAt(i).widget().setParent(None)
        
        # Add header
        reports_layout.addWidget(QLabel("<h2>Network Monitoring Reports</h2>"))
        
        # Create buttons for different reports
        button_grid = QGridLayout()
        
        # Daily Traffic Summary Report
        self.daily_traffic_btn = QPushButton("Daily Traffic Summary")
        self.daily_traffic_btn.clicked.connect(self.report_generator.generate_daily_traffic_report)
        button_grid.addWidget(self.daily_traffic_btn, 0, 0)
        
        # Bandwidth Consumers Report
        self.bandwidth_btn = QPushButton("Top Bandwidth Consumers")
        self.bandwidth_btn.clicked.connect(self.report_generator.generate_bandwidth_report)
        button_grid.addWidget(self.bandwidth_btn, 0, 1)
        
        # Protocol Analysis Report
        self.protocol_btn = QPushButton("Protocol Analysis")
        self.protocol_btn.clicked.connect(self.report_generator.generate_protocol_report)
        button_grid.addWidget(self.protocol_btn, 1, 0)
        
        # Security Alert Report
        self.security_btn = QPushButton("Security Alerts")
        self.security_btn.clicked.connect(self.report_generator.generate_security_report)
        button_grid.addWidget(self.security_btn, 1, 1)
        
        # Peak Usage Report
        self.peak_usage_btn = QPushButton("Peak Usage Hours")
        self.peak_usage_btn.clicked.connect(self.report_generator.generate_peak_usage_report)
        button_grid.addWidget(self.peak_usage_btn, 2, 0)
        
        reports_layout.addLayout(button_grid)
        
        # Add report display area
        self.report_display = QTextEdit()
        self.report_display.setReadOnly(True)
        self.report_display.setMinimumHeight(400)
        reports_layout.addWidget(self.report_display)
        
        # Initialize with a default report
        self.report_generator.generate_daily_traffic_report()

    def setup_settings_page(self):
        """Sets up the Settings page with dark mode toggle."""
        settings_layout = self.pages["Settings"].layout()
        
        # Add header
        settings_layout.addWidget(QLabel("<h2>Application Settings</h2>"))
        
        # Create a horizontal layout for the dark mode option
        dark_mode_layout = QHBoxLayout()
        dark_mode_label = QLabel("Dark Mode:")
        dark_mode_layout.addWidget(dark_mode_label)
        
        # Add on/off button for dark mode
        self.dark_mode_button = QPushButton("OFF")
        self.dark_mode_button.setCheckable(True)
        self.dark_mode_button.setFixedWidth(80)
        self.dark_mode_button.clicked.connect(self.toggle_dark_mode)
        dark_mode_layout.addWidget(self.dark_mode_button)
        dark_mode_layout.addStretch()
        settings_layout.addLayout(dark_mode_layout)
        
        # Refresh rate settings
        refresh_rate_layout = QHBoxLayout()
        refresh_rate_label = QLabel("Refresh Rate (seconds):")
        refresh_rate_layout.addWidget(refresh_rate_label)
        
        self.refresh_rate_button = QPushButton("3")
        self.refresh_rate_button.setFixedWidth(80)
        self.refresh_rate_button.clicked.connect(self.change_refresh_rate)
        refresh_rate_layout.addWidget(self.refresh_rate_button)
        refresh_rate_layout.addStretch()
        settings_layout.addLayout(refresh_rate_layout)
        
        # Add spacing
        settings_layout.addStretch()

    def setup_port_blocker_page(self):
        layout = self.pages["Port Blocker"].layout()
        self.port_blocker_widget = PortBlocker()
        layout.addWidget(self.port_blocker_widget)

    def setup_trace_visualizer_page(self):
        layout = self.pages["Trace Visualizer"].layout()
        self.trace_widget = TraceVisualizer()
        layout.addWidget(self.trace_widget)
    
    def setup_other_pages(self):
        """Sets up other pages with placeholder content."""
        # Information page
        info_layout = self.pages["Information"].layout()
        info_layout.addWidget(QLabel("<h2>Information</h2>"))
        info_layout.addWidget(QLabel("This application monitors network traffic and manages ports."))
        info_layout.addWidget(QLabel("Version: 1.0"))
        info_layout.addStretch()
        
        # Help page
        help_layout = self.pages["Help"].layout()
        help_layout.addWidget(QLabel("<h2>Help</h2>"))
        help_layout.addWidget(QLabel("For assistance with using this application:"))
        help_layout.addWidget(QLabel("1. Navigate using the sidebar on the left"))
        help_layout.addWidget(QLabel("2. Home page shows network traffic and port monitoring"))
        help_layout.addWidget(QLabel("3. Data Analysis page provides network insights"))
        help_layout.addWidget(QLabel("4. Reports page generates detailed network reports"))
        help_layout.addWidget(QLabel("5. Settings page allows customization"))
        help_layout.addStretch()


    def switch_page(self, index):
        self.content_area.setCurrentIndex(index)


    def toggle_dark_mode(self):
        """Toggles the dark mode theme."""
        self.dark_mode = self.dark_mode_button.isChecked()
        self.dark_mode_button.setText("ON" if self.dark_mode else "OFF")
        self.apply_theme()

    def change_refresh_rate(self):
        """Changes the refresh rate of network monitoring."""
        current_rate = int(self.refresh_rate_button.text())
        # Cycle through 3, 5, 10 seconds
        if current_rate == 3:
            new_rate = 5
        elif current_rate == 5:
            new_rate = 10
        else:
            new_rate = 3
        
        self.refresh_rate_button.setText(str(new_rate))
        self.timer.stop()
        self.timer.start(new_rate * 1000)

    def apply_theme(self):
        """Applies dark or light mode based on the dark_mode flag."""
        dark = self.dark_mode

        if dark:
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

                QScrollBar:vertical {
                    background: #2c3e50;
                    width: 10px;
                }
                QScrollBar::handle:vertical {
                    background: #1abc9c;
                    min-height: 20px;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    background: none;
                    height: 0px;
                }

                QMenu {
                    background-color: #2c3e50;
                    color: white;
                    border: 1px solid #1abc9c;
                }
                QMenuBar {
                    background-color: #2c3e50;
                    color: white;
                }
                QMenuBar::item {
                    background: transparent;
                    padding: 4px 10px;
                }
                QMenuBar::item:selected {
                    background: #1abc9c;
                }
                QMenuBar::item:disabled {
                    background: transparent;
                    color: #777;
                }
                QLineEdit, QTextEdit {
                    background-color: #34495e;
                    color: white;
                    border: 1px solid #1abc9c;
                }

                QTabWidget::pane {
                    background-color: #2c3e50;
                    border: 1px solid #1abc9c;
                }
                QTabBar::tab {
                    background: #2c3e50;
                    color: white;
                    padding: 6px;
                    border: 1px solid #1abc9c;
                    border-bottom: none;
                }
                QTabBar::tab:selected {
                    background: #1abc9c;
                    color: white;
                }
            """)
            self.sidebar_container.setStyleSheet("background-color: #2c3e50;")
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
                QTableCornerButton::section {
                    background-color: #dfe6e9;
                    border: 1px solid #bdc3c7;
                }

                QScrollBar:vertical {
                    background: #ecf0f1;
                    width: 10px;
                }
                QScrollBar::handle:vertical {
                    background: #3498db;
                    min-height: 20px;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    background: none;
                    height: 0px;
                }

                QMenu {
                    background-color: #ffffff;
                    color: black;
                    border: 1px solid #bdc3c7;
                }
                QMenu::item:selected {
                    background-color: #3498db;
                    color: white;
                }

                QLineEdit, QTextEdit {
                    background-color: white;
                    color: black;
                    border: 1px solid #3498db;
                }

                QTabWidget::pane {
                    background-color: #ecf0f1;
                    border: 1px solid #3498db;
                }
                QTabBar::tab {
                    background: #dfe6e9;
                    color: black;
                    padding: 6px;
                    border: 1px solid #bdc3c7;
                    border-bottom: none;
                }
                QTabBar::tab:selected {
                    background: #3498db;
                    color: white;
                }
            """)
            self.sidebar_container.setStyleSheet("background-color: #ecf0f1;")
            self.sidebar_container.apply_theme(self.dark_mode)

        # Update navigation button styles - fix the property name to use "buttons" instead of "nav_buttons"
        if hasattr(self.sidebar_container, 'buttons'):
            from ui.navigation_panel import button_style  # import here to avoid circular
            for btn in self.sidebar_container.buttons:
                btn.setStyleSheet(button_style(dark))
                
        # Update the Information page with the current theme
        if "Information" in self.pages:
            update_info_theme(self.pages["Information"], self.dark_mode)
            
        # Update the Help page with the current theme
        if "Help" in self.pages:
            from ui.help import update_help_theme
            update_help_theme(self.pages["Help"], self.dark_mode)

    def update_monitoring(self):
        """Updates the network traffic and port monitoring tables periodically."""
        # Throttle updates - don't update if the last update was less than 1 second ago
        current_time = time.time()
        if hasattr(self, 'last_update_time') and current_time - self.last_update_time < 1:
            return
            
        self.last_update_time = current_time
            
        # Only update if the application window is visible and this tab is active
        if not self.isVisible() or self.content_area.currentIndex() != 0:
            return
            
        # Only update the ports table now
        self.update_ports_table()

    def update_ports_table(self):
        """Update the ports table with the latest open ports and their states."""
        open_ports = get_open_ports()
        self.ports_table.setRowCount(len(open_ports))
        for row, port_info in enumerate(open_ports):
            self.ports_table.setItem(row, 0, QTableWidgetItem(str(port_info['port'])))
            self.ports_table.setItem(row, 1, QTableWidgetItem(str(port_info['pid'])))
            self.ports_table.setItem(row, 2, QTableWidgetItem("TCP"))  # Protocol (placeholder)
            self.ports_table.setItem(row, 3, QTableWidgetItem(port_info['process_name']))
            details = get_process_info(port_info['pid'])
            if details:
                self.ports_table.setItem(row, 4, QTableWidgetItem(f"{details['cpu_percent']}%"))
            else:
                self.ports_table.setItem(row, 4, QTableWidgetItem("N/A"))
            status_item = QTableWidgetItem("Enabled" if port_info['enabled'] else "Disabled")
            self.ports_table.setItem(row, 5, status_item)
            self.color_row(row, port_info['enabled'])
        
        # Log the details of open ports
        logging.info(f"Port table refreshed. Open ports: {open_ports}")

    def toggle_selected_port(self):
        """Toggle the state of the selected port."""
        selected_row = self.ports_table.currentRow()
        if selected_row >= 0:
            port = int(self.ports_table.item(selected_row, 0).text())
            toggle_port_state(port)
            self.update_ports_table()  # Refresh the table to reflect the new state
    
    def menu_action(self, action_name):
        """Handles menu actions."""
        print(f"Menu option selected: {action_name}")

    def color_row(self, row, enabled):
        """Color the row based on the port's state."""
        if self.dark_mode:
            color = QColor(50, 100, 50) if enabled else QColor(100, 50, 50)
        else:
            color = QColor(200, 255, 200) if enabled else QColor(255, 200, 200)
        
        for col in range(self.ports_table.columnCount()):
            item = self.ports_table.item(row, col)
            if item:
                item.setBackground(color)
                text_color = Qt.white if self.dark_mode else Qt.black  # Changed this line
                item.setForeground(QBrush(text_color))

    def show_graph(self, fig):
        """Display the selected graph."""
        self.graph_canvas.figure = fig
        self.graph_canvas.draw()

    def display_report(self, report_html):
        """Display the generated report in the text edit."""
        self.report_display.setHtml(report_html)

    def update_page_title_colors(self):
        """Updates the page title colors to match the current theme."""
        current_page = self.content_area.currentWidget()
        if current_page:
            for label in current_page.findChildren(QLabel):
                label.setStyleSheet(f"color: {'white' if self.dark_mode else 'black'};")

    def show_connected_devices(self):
        """Show the connected devices window."""
        if not self.device_scanner_window or not self.device_scanner_window.isVisible():
            self.device_scanner_window = DeviceScanner(self.dark_mode)
            self.device_scanner_window.show()
        else:
            self.device_scanner_window.activateWindow()
            self.device_scanner_window.scan_devices()  # Refresh the devices

    def fetch_ip_info(self):
        """Fetch public IP information in a background thread."""
        # Fetch IPv4 info
        ip_info = get_public_ip_info()
        if ip_info['ip'] != 'N/A':
            self.public_ip_info = ip_info
        
        # Fetch IPv6
        ipv6 = get_public_ipv6()
        if ipv6 != 'N/A':
            self.public_ipv6 = ipv6
            
        # Update the UI
        self.update_ip_display()
    
    def update_ip_display(self):
        """Update the IP information display."""
        self.ipv4_value.setText(self.public_ip_info['ip'])
        self.ipv6_value.setText(self.public_ipv6)
        self.isp_label.setText(self.public_ip_info['org'])
        self.city_label.setText(self.public_ip_info.get('city', 'N/A'))
        self.region_label.setText(self.public_ip_info['region'])
        self.country_label.setText(self.public_ip_info['country'])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NetworkMonitor()
    window.show()
    sys.exit(app.exec())