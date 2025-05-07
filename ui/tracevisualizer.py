import socket
import subprocess
import requests
import folium
import os
import platform
import time
import re
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QLabel, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QSplitter, QGroupBox,
    QGridLayout, QFrame
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QColor


class TraceWorker(QThread):
    result_ready = pyqtSignal(list)
    hop_ready = pyqtSignal(dict)
    progress = pyqtSignal(str)
    error = pyqtSignal(str)
    finished_trace = pyqtSignal()

    def __init__(self, target):
        super().__init__()
        self.target = target
        self.running = True
        self.hops = []

    def stop(self):
        self.running = False

    def run(self):
        try:
            # Resolve domain to IP
            self.progress.emit("Resolving domain...")
            if not self.target.replace('.', '').isdigit():
                self.target = socket.gethostbyname(self.target)
            
            self.progress.emit(f"Starting trace to {self.target}...")
            
            # Use subprocess.Popen for real-time output processing
            if platform.system() == "Windows":
                process = subprocess.Popen(
                    ['tracert', '-h', '20', '-w', '1000', self.target],
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    text=True, 
                    bufsize=1,
                    universal_newlines=True
                )
            else:
                process = subprocess.Popen(
                    ['traceroute', '-m', '20', '-w', '1', self.target],
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    text=True, 
                    bufsize=1,
                    universal_newlines=True
                )
            
            # Process output in real time
            line_buffer = []
            current_hop = 0
            
            while self.running:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                
                if not line.strip():
                    continue
                    
                line_buffer.append(line)
                self.progress.emit(f"Processing: {line.strip()}")
                
                # Windows tracert parsing
                if platform.system() == "Windows":
                    # Skip header lines
                    if "Tracing route" in line or "over a maximum" in line:
                        continue
                        
                    # Parse hop line
                    hop_match = re.search(r'^(\s*)(\d+)', line)
                    if hop_match:
                        hop_num = int(hop_match.group(2))
                        current_hop = hop_num
                        
                        # Extract response times - Windows may show "*" for timeouts
                        times = re.findall(r'(\d+)\s*ms|(\*)', line)
                        avg_time = 0
                        valid_times = [int(t[0]) for t in times if t[0]]
                        if valid_times:
                            avg_time = sum(valid_times) / len(valid_times)
                        
                        # Extract IP address and hostname
                        ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                        ip = ip_match.group(1) if ip_match else "Timeout"
                        
                        # Extract hostname if available
                        host = "Unknown"
                        if ip != "Timeout":
                            host_match = re.search(r'\d+\.\d+\.\d+\.\d+\s+(\S+)', line)
                            if host_match and host_match.group(1) != ip:
                                host = host_match.group(1)
                            else:
                                try:
                                    host = socket.gethostbyaddr(ip)[0]
                                except (socket.herror, socket.gaierror):
                                    pass
                        
                        hop_data = {
                            'hop': hop_num,
                            'host': host,
                            'ip': ip,
                            'time_ms': round(avg_time, 2)
                        }
                        
                        self.hops.append(hop_data)
                        self.hop_ready.emit(hop_data)
                
                # Linux/macOS traceroute parsing
                else:
                    if "traceroute to" in line:
                        continue
                        
                    hop_match = re.match(r'^\s*(\d+)\s+([\w\.-]+|\*)\s+\(?([\d\.]+)?\)?(?:\s+(\d+\.\d+)\s*ms)?', line)
                    if hop_match:
                        groups = hop_match.groups()
                        hop_num = int(groups[0])
                        current_hop = hop_num
                        host = groups[1] if groups[1] != '*' else "Timeout"
                        ip = groups[2] if groups[2] else "Timeout"
                        time_ms = float(groups[3]) if groups[3] else 0
                        
                        hop_data = {
                            'hop': hop_num,
                            'host': host,
                            'ip': ip,
                            'time_ms': round(time_ms, 2)
                        }
                        
                        self.hops.append(hop_data)
                        self.hop_ready.emit(hop_data)
            
            self.progress.emit("Trace completed!")
            self.finished_trace.emit()
            self.result_ready.emit(self.hops)

        except Exception as e:
            self.error.emit(f"Error during trace: {str(e)}")
            import traceback
            traceback.print_exc()


class LocationLookupThread(QThread):
    """Thread for looking up location data for IP addresses"""
    result_ready = pyqtSignal(int, dict, str, str, str)
    
    def __init__(self, row_idx, hop_data):
        super().__init__()
        self.row_idx = row_idx
        self.hop_data = hop_data
        
    def run(self):
        try:
            ip = self.hop_data['ip']
            response = requests.get(f"http://ip-api.com/json/{ip}").json()
            
            if response['status'] == 'success':
                country = response['countryCode']
                country_name = response['country']
                city = response['city']
                
                self.result_ready.emit(self.row_idx, response, country, country_name, city)
            else:
                self.result_ready.emit(self.row_idx, {}, "Unknown", "Unknown", "Unknown")
                
        except Exception as e:
            print(f"Error looking up location for hop {self.hop_data['hop']}: {str(e)}")
            self.result_ready.emit(self.row_idx, {}, "Error", "Error", "Error")


class TraceVisualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.lookup_threads = []  # Store references to prevent premature garbage collection

    def init_ui(self):
        layout = QVBoxLayout()

        # ==== DNS LOOKUP SECTION ====
        dns_group = QGroupBox("Website to IP Lookup")
        dns_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        dns_layout = QGridLayout()
        
        dns_info = QLabel("Please enter website to get its IP")
        dns_info.setStyleSheet("font-size: 14px;")
        dns_layout.addWidget(dns_info, 0, 0, 1, 3)
        
        url_label = QLabel("Enter website URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("e.g., www.google.com")
        dns_layout.addWidget(url_label, 1, 0)
        dns_layout.addWidget(self.url_input, 1, 1)
        
        self.dns_lookup_btn = QPushButton("Lookup")
        self.dns_lookup_btn.clicked.connect(self.perform_dns_lookup)
        dns_layout.addWidget(self.dns_lookup_btn, 1, 2)
        
        ip_label = QLabel("IP Address:")
        self.ip_result = QLineEdit()
        self.ip_result.setReadOnly(True)
        self.ip_result.setPlaceholderText("IP will appear here")
        dns_layout.addWidget(ip_label, 2, 0)
        dns_layout.addWidget(self.ip_result, 2, 1, 1, 2)
        
        # Add "Use for Trace" button
        self.use_ip_btn = QPushButton("Use for Trace")
        self.use_ip_btn.clicked.connect(self.use_ip_for_trace)
        self.use_ip_btn.setEnabled(False)
        dns_layout.addWidget(self.use_ip_btn, 3, 1, 1, 2)
        
        dns_group.setLayout(dns_layout)
        layout.addWidget(dns_group)
        
        # Add a separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # ==== TRACE ROUTE SECTION ====
        trace_group = QGroupBox("Trace Route")
        trace_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        trace_layout = QVBoxLayout()
        
        title = QLabel("Network Trace Visualizer")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        trace_layout.addWidget(title)

        input_layout = QHBoxLayout()
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Enter IP or domain (e.g., 8.8.8.8 or google.com)")
        input_layout.addWidget(self.ip_input)

        self.trace_btn = QPushButton("Trace Route")
        self.trace_btn.clicked.connect(self.start_trace)
        input_layout.addWidget(self.trace_btn)
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #3186cc;")
        input_layout.addWidget(self.status_label)
        
        trace_layout.addLayout(input_layout)
        trace_group.setLayout(trace_layout)
        layout.addWidget(trace_group)
        
        # Create a splitter to divide map and table
        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(2)
        
        # Add map view
        self.web_view = QWebEngineView()
        self.web_view.setMinimumHeight(300)
        splitter.addWidget(self.web_view)
        
        # Add trace results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(["Hop", "Host", "IP", "Time (ms)", "Country"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results_table.setMinimumHeight(150)
        self.results_table.setVisible(False)  # Hide until we have results
        splitter.addWidget(self.results_table)
        
        # Set initial splitter sizes
        splitter.setSizes([700, 300])
        
        layout.addWidget(splitter)
        self.setLayout(layout)
        self.show_world_map()
        
        # For real-time visualization
        self.hop_locations = []
        self.incremental_hops = []

    def show_world_map(self):
        m = folium.Map(location=[20, 0], zoom_start=2)
        data = os.path.join(os.path.dirname(__file__), 'world_map.html')
        m.save(data)
        self.web_view.setUrl(QUrl.fromLocalFile(data))

    def perform_dns_lookup(self):
        """Resolve a website URL to its IP address"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a website URL")
            return
            
        # Remove protocol prefix if present
        if url.startswith(("http://", "https://")):
            url = url.split("//")[1]
            
        # Remove path if present
        if "/" in url:
            url = url.split("/")[0]
            
        try:
            # Show status while resolving
            self.ip_result.setText("Resolving...")
            self.ip_result.repaint()  # Force update
            
            # Perform DNS lookup
            ip = socket.gethostbyname(url)
            self.ip_result.setText(ip)
            
            # Enable the "Use for Trace" button
            self.use_ip_btn.setEnabled(True)
        except socket.gaierror:
            self.ip_result.setText("Could not resolve host")
            self.use_ip_btn.setEnabled(False)
        except Exception as e:
            self.ip_result.setText(f"Error: {str(e)}")
            self.use_ip_btn.setEnabled(False)
            
    def use_ip_for_trace(self):
        """Copy the resolved IP to the trace input field"""
        ip = self.ip_result.text()
        if ip and ip != "Could not resolve host" and not ip.startswith("Error"):
            self.ip_input.setText(ip)
            # Optionally flash the trace section to draw attention
            self.status_label.setText("IP copied from lookup - Ready to trace")
            # Focus on the trace button
            self.trace_btn.setFocus()

    def start_trace(self):
        target = self.ip_input.text().strip()
        if not target:
            QMessageBox.warning(self, "Warning", "Please enter an IP or domain")
            return

        # Resolve to IP if it's a domain
        try:
            display_name = target
            if not target.replace('.', '').isdigit():
                self.status_label.setText("Resolving domain...")
            
            # Check for local/private IPs
            if (target.startswith("127.") or
                target.startswith("192.168.") or
                target.startswith("10.") or
                target.startswith("172.16.") or
                target == socket.gethostbyname(socket.gethostname())):
                QMessageBox.information(self, "Info", f"Tracing local/private IPs like {target} is not supported.\nThese do not produce usable route information.")
                return
            
            # Terminate old thread if needed
            if hasattr(self, 'worker') and self.worker.isRunning():
                self.worker.stop()
                self.worker.wait(500)  # Give it time to stop cleanly
            
            # Reset for new trace
            self.trace_btn.setEnabled(False)
            self.trace_btn.setText("Tracing...")
            self.results_table.setRowCount(0)
            self.results_table.setVisible(True)
            self.incremental_hops = []
            self.hop_locations = []
            
            # Create a basic map to show progress
            self.show_initial_map(f"Tracing route to {display_name}...")
            
            # Start the worker
            self.worker = TraceWorker(target)
            self.worker.result_ready.connect(self.on_trace_complete)
            self.worker.error.connect(self.on_trace_failed)
            self.worker.progress.connect(self.update_status)
            self.worker.hop_ready.connect(self.on_hop_ready)
            self.worker.finished_trace.connect(self.on_trace_finished)
            self.worker.start()
            
        except socket.gaierror:
            QMessageBox.warning(self, "Warning", f"Could not resolve domain: {target}")
            return
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unexpected error: {str(e)}")
            return

    def update_status(self, status):
        self.status_label.setText(status)

    def update_hop(self, hop_data):
        self.incremental_hops.append(hop_data)
        self.plot_trace(self.incremental_hops)

    def on_trace_complete(self, hops):
        self.trace_btn.setEnabled(True)
        if not hops:
            QMessageBox.information(self, "Info", "No route information found — target may be unreachable.")
            self.show_world_map()
            self.results_table.setVisible(False)
            return
        self.plot_trace(hops)

    def on_trace_failed(self, error_msg):
        self.trace_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", f"Trace failed: {error_msg}")

    def plot_trace(self, hops):
        # Create a new map centered on a neutral position
        m = folium.Map(location=[20, 0], zoom_start=2)
        locations = []
        hop_info = []
        
        # Clear the results table and prepare for new data
        self.results_table.setRowCount(0)
        self.results_table.setRowCount(len(hops))
        self.results_table.setVisible(True)
        
        for index, hop in enumerate(hops):
            ip = hop['ip']
            hop_num = hop['hop']
            host = hop['host']
            time_ms = hop['time_ms']
            
            # Skip adding markers for timeouts or reserved IPs
            if ip == "Timeout" or is_reserved_ip(ip):
                # Add to table but skip mapping
                self.add_hop_to_table(index, hop_num, host, ip, time_ms, "Unknown")
                continue
                
            try:
                response = requests.get(f"http://ip-api.com/json/{ip}").json()
                if response['status'] == 'success':
                    lat, lon = response['lat'], response['lon']
                    country = response['countryCode']
                    country_name = response['country']
                    city = response['city']
                    flag_url = f"https://flagcdn.com/w40/{country.lower()}.png"
                    
                    # Create popup with hop number prominently displayed
                    popup_html = f"""
                    <div style="font-family: Arial, sans-serif;">
                        <div style="font-size: 16px; font-weight: bold; text-align: center; margin-bottom: 8px;">
                            Hop #{hop_num}
                        </div>
                        <div>
                            <b>IP:</b> {ip}<br>
                            <b>Host:</b> {host}<br>
                            <b>Location:</b> {city}, {country}<br>
                            <b>Response time:</b> {time_ms} ms<br>
                            <img src="{flag_url}" width="40">
                        </div>
                    </div>
                    """
                    
                    popup = folium.Popup(popup_html, max_width=300)
                    
                    # Create custom icon with hop number
                    icon_html = f'''
                    <div style="background-color: #3186cc; color: white; border-radius: 50%; 
                         width: 25px; height: 25px; line-height: 25px; text-align: center; 
                         font-weight: bold; font-size: 14px; border: 2px solid white;">
                        {hop_num}
                    </div>
                    '''
                    
                    # Add the marker with custom icon
                    folium.Marker(
                        [lat, lon],
                        popup=popup,
                        icon=folium.DivIcon(html=icon_html, icon_size=(30, 30))
                    ).add_to(m)
                    
                    # Also add country flag as a separate marker
                    folium.Marker(
                        [lat, lon],
                        icon=folium.features.CustomIcon(flag_url, icon_size=(20, 15)),
                        popup=f"Country: {country_name}"
                    ).add_to(m)
                    
                    locations.append([lat, lon])
                    
                    # Add hop to results table
                    self.add_hop_to_table(index, hop_num, host, ip, time_ms, country)
                else:
                    # API response not successful, add to table with limited info
                    self.add_hop_to_table(index, hop_num, host, ip, time_ms, "Unknown")
            except Exception as e:
                # Error looking up location, add to table with limited info
                self.add_hop_to_table(index, hop_num, host, ip, time_ms, "Unknown")
                
        # Draw path line connecting all locations if we have more than one
        if len(locations) > 1:
            folium.PolyLine(locations, color="blue", weight=2.5, opacity=0.8, 
                           dash_array='5').add_to(m)
            
            # Try to zoom to fit the route
            if len(locations) > 0:
                southwest = [min(loc[0] for loc in locations), min(loc[1] for loc in locations)]
                northeast = [max(loc[0] for loc in locations), max(loc[1] for loc in locations)]
                m.fit_bounds([southwest, northeast], padding=(50, 50))
        
        # Add title and destination information
        target_ip = hops[-1]['ip'] if hops and hops[-1]['ip'] != "Timeout" else "Unknown"
        target_host = hops[-1]['host'] if hops and hops[-1]['host'] != "Unknown" else target_ip
        
        title_html = f'''
            <div style="position: fixed; top: 10px; left: 50px; width: 300px; 
                       background-color: white; padding: 10px; z-index: 9999; 
                       border: 2px solid #3186cc; border-radius: 5px;">
                <h4 style="margin: 0;">Traceroute to {target_host} ({target_ip})</h4>
                <p style="margin: 5px 0 0 0;">{len(hops)} hops max, 60 byte packets</p>
            </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Save the map and display it
        data = os.path.join(os.path.dirname(__file__), 'trace_map.html')
        m.save(data)
        self.web_view.setUrl(QUrl.fromLocalFile(data))
        
    def add_hop_to_table(self, row_idx, hop_num, host, ip, time_ms, country):
        """Helper method to add a hop to the results table"""
        # Hop number
        hop_item = QTableWidgetItem(str(hop_num))
        hop_item.setTextAlignment(Qt.AlignCenter)
        self.results_table.setItem(row_idx, 0, hop_item)
        
        # Host name
        host_item = QTableWidgetItem(host)
        self.results_table.setItem(row_idx, 1, host_item)
        
        # IP address
        ip_item = QTableWidgetItem(ip)
        self.results_table.setItem(row_idx, 2, ip_item)
        
        # Response time
        time_item = QTableWidgetItem(f"{time_ms}" if time_ms > 0 else "*")
        time_item.setTextAlignment(Qt.AlignCenter)
        self.results_table.setItem(row_idx, 3, time_item)
        
        # Country
        country_item = QTableWidgetItem(country)
        self.results_table.setItem(row_idx, 4, country_item)
        
        # Color row based on response time
        if ip == "Timeout":
            row_color = QColor(255, 200, 200)  # Light red for timeout
        elif time_ms > 100:
            row_color = QColor(255, 230, 180)  # Light orange for slow response
        else:
            row_color = QColor(200, 255, 200)  # Light green for fast response
            
        for col in range(5):
            self.results_table.item(row_idx, col).setBackground(row_color)

    def on_hop_ready(self, hop_data):
        """Handle a new hop as it comes in from the trace process"""
        # Add to our ongoing collection
        self.incremental_hops.append(hop_data)
        
        # Update the table with the new hop data
        row_idx = len(self.incremental_hops) - 1
        
        # Ensure table has enough rows
        if self.results_table.rowCount() <= row_idx:
            self.results_table.setRowCount(row_idx + 1)
        
        # Extract data
        hop_num = hop_data['hop']
        host = hop_data['host']
        ip = hop_data['ip']
        time_ms = hop_data['time_ms']
        
        # Add to table first (always works even for timeouts)
        self.add_hop_to_table(row_idx, hop_num, host, ip, time_ms, "Looking up...")
        
        # If it's a valid IP (not timeout), get location data and update the map
        if ip != "Timeout" and not is_reserved_ip(ip):
            # Run in a separate thread to avoid blocking UI
            lookup_thread = LocationLookupThread(row_idx, hop_data)
            lookup_thread.result_ready.connect(self.on_location_lookup_complete)
            lookup_thread.start()
            self.lookup_threads.append(lookup_thread)  # Store reference to prevent garbage collection
    
    def on_location_lookup_complete(self, row_idx, response, country, country_name, city):
        """Handle completion of location lookup"""
        if not self.results_table or row_idx >= self.results_table.rowCount():
            return
            
        # Update country in the table
        country_item = QTableWidgetItem(country)
        self.results_table.setItem(row_idx, 4, country_item)
        
        # Clean up finished threads to prevent memory leaks
        self.lookup_threads = [t for t in self.lookup_threads if t.isRunning()]
        
        # Now update the map with all current hops
        self.update_map_with_hops()
    
    def update_map_with_hops(self):
        """Update the map with all the hops we have so far"""
        # Create a new map
        m = folium.Map(location=[20, 0], zoom_start=2)
        locations = []
        
        for hop in self.incremental_hops:
            ip = hop['ip']
            if ip == "Timeout" or is_reserved_ip(ip):
                continue
                
            try:
                response = requests.get(f"http://ip-api.com/json/{ip}").json()
                if response['status'] == 'success':
                    lat, lon = response['lat'], response['lon']
                    hop_num = hop['hop']
                    host = hop['host']
                    time_ms = hop['time_ms']
                    country = response['countryCode']
                    country_name = response['country']
                    city = response['city']
                    flag_url = f"https://flagcdn.com/w40/{country.lower()}.png"
                    
                    # Create popup
                    popup_html = f"""
                    <div style="font-family: Arial, sans-serif;">
                        <div style="font-size: 16px; font-weight: bold; text-align: center; margin-bottom: 8px;">
                            Hop #{hop_num}
                        </div>
                        <div>
                            <b>IP:</b> {ip}<br>
                            <b>Host:</b> {host}<br>
                            <b>Location:</b> {city}, {country}<br>
                            <b>Response time:</b> {time_ms} ms<br>
                            <img src="{flag_url}" width="40">
                        </div>
                    </div>
                    """
                    
                    popup = folium.Popup(popup_html, max_width=300)
                    
                    # Create custom icon with hop number
                    icon_html = f'''
                    <div style="background-color: #3186cc; color: white; border-radius: 50%; 
                         width: 25px; height: 25px; line-height: 25px; text-align: center; 
                         font-weight: bold; font-size: 14px; border: 2px solid white;">
                        {hop_num}
                    </div>
                    '''
                    
                    # Add the marker
                    folium.Marker(
                        [lat, lon],
                        popup=popup,
                        icon=folium.DivIcon(html=icon_html, icon_size=(30, 30))
                    ).add_to(m)
                    
                    # Add country flag
                    folium.Marker(
                        [lat, lon],
                        icon=folium.features.CustomIcon(flag_url, icon_size=(20, 15)),
                        popup=f"Country: {country_name}"
                    ).add_to(m)
                    
                    # Store location for line drawing
                    locations.append([lat, lon])
                    
            except Exception as e:
                print(f"Error adding marker for hop {hop['hop']}: {str(e)}")
                
        # Draw path line if we have multiple locations
        if len(locations) > 1:
            folium.PolyLine(locations, color="blue", weight=2.5, opacity=0.8, 
                           dash_array='5').add_to(m)
            
            # Zoom to fit the route
            if len(locations) > 0:
                try:
                    southwest = [min(loc[0] for loc in locations), min(loc[1] for loc in locations)]
                    northeast = [max(loc[0] for loc in locations), max(loc[1] for loc in locations)]
                    m.fit_bounds([southwest, northeast], padding=(50, 50))
                except:
                    pass
        
        # Add title showing trace is in progress
        target = self.ip_input.text().strip()
        progress_html = f'''
            <div style="position: fixed; top: 10px; left: 50px; width: 300px; 
                       background-color: white; padding: 10px; z-index: 9999; 
                       border: 2px solid #3186cc; border-radius: 5px;">
                <h4 style="margin: 0;">Tracing route to {target}</h4>
                <p style="margin: 5px 0 0 0;">Hop {len(self.incremental_hops)} - Trace in progress...</p>
            </div>
        '''
        m.get_root().html.add_child(folium.Element(progress_html))
        
        # Save and display
        data = os.path.join(os.path.dirname(__file__), 'trace_map.html')
        m.save(data)
        self.web_view.setUrl(QUrl.fromLocalFile(data))
    
    def show_initial_map(self, message):
        """Show an initial map with a message that the trace is starting"""
        m = folium.Map(location=[20, 0], zoom_start=2)
        
        # Add a title with the starting message
        title_html = f'''
            <div style="position: fixed; top: 10px; left: 50px; width: 300px; 
                       background-color: white; padding: 10px; z-index: 9999; 
                       border: 2px solid #3186cc; border-radius: 5px;">
                <h4 style="margin: 0;">{message}</h4>
                <p style="margin: 5px 0 0 0;">Initializing trace...</p>
            </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Save and display
        data = os.path.join(os.path.dirname(__file__), 'trace_map.html')
        m.save(data)
        self.web_view.setUrl(QUrl.fromLocalFile(data))
    
    def on_trace_finished(self):
        """Handle trace completion"""
        self.trace_btn.setEnabled(True)
        self.trace_btn.setText("Trace Route")
        self.status_label.setText("Trace complete!")

    def closeEvent(self, event):
        """Cleanup when the widget is closed"""
        # Stop the main trace worker if it exists and is running
        if hasattr(self, 'worker') and self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(1000)  # Wait up to 1 second for it to stop
            
        # Clean up any lookup threads that might still be running
        for thread in self.lookup_threads:
            if thread.isRunning():
                thread.wait(500)  # Give threads time to finish
                
        self.lookup_threads.clear()
        super().closeEvent(event)


def is_reserved_ip(ip):
    """Check if an IP address is in a reserved range that should be ignored in traceroute visualization"""
    if ip == "Timeout":
        return False
        
    # Reserved/private IP ranges to filter out
    reserved_ranges = [
        ("192.0.0.", "192.0.0 block"),
        ("192.168.", "Private network"),
        ("10.", "Private network"),
        ("172.16.", "Private network"),
        ("127.", "Localhost"),
        ("169.254.", "Link-local"),
        ("224.", "Multicast"),
        ("0.", "Invalid"),
    ]
    
    for prefix, _ in reserved_ranges:
        if ip.startswith(prefix):
            return True
    
    return False
