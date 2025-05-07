import time
import random
from PyQt5.QtWidgets import QTextEdit, QGridLayout, QPushButton, QLabel
from PyQt5.QtCore import pyqtSignal, QObject

class ReportGenerator(QObject):
    report_generated = pyqtSignal(str)  # Signal to emit generated reports
    
    def __init__(self):
        super().__init__()
        self.sample_devices = [
            ("192.168.1.15", "Workstation-15"),
            ("192.168.1.23", "Server-23"),
            ("192.168.1.42", "Workstation-42"),
            ("192.168.1.8", "NAS-8"),
            ("192.168.1.19", "Workstation-19"),
            ("192.168.1.3", "Printer-3"),
            ("192.168.1.11", "Workstation-11"),
            ("192.168.1.7", "IP-Phone-7"),
            ("192.168.1.30", "Tablet-30"),
            ("192.168.1.5", "Security-Cam-5")
        ]
    
    def generate_daily_traffic_report(self):
        """Generate daily traffic summary report."""
        total_packets = random.randint(500000, 1000000)
        total_bytes = total_packets * random.randint(500, 1500)
        active_conn = random.randint(50, 200)
        
        report = f"""
        <h3>Daily Traffic Summary Report - {time.strftime('%Y-%m-%d')}</h3>
        <table border="1" cellpadding="5">
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Total Packets</td><td>{total_packets:,}</td></tr>
            <tr><td>Total Bytes</td><td>{total_bytes:,}</td></tr>
            <tr><td>Active Connections</td><td>{active_conn}</td></tr>
            <tr><td>Average Packet Size</td><td>{total_bytes/total_packets:,.2f} bytes</td></tr>
        </table>
        <p>Report generated at: {time.strftime('%H:%M:%S')}</p>
        """
        self.report_generated.emit(report)
    
    def generate_bandwidth_report(self):
        """Generate top bandwidth consumers report."""
        devices = [(ip, name, f"{random.uniform(1.5, 45.2):.1f} GB") 
                  for ip, name in self.sample_devices]
        devices.sort(key=lambda x: float(x[2].split()[0]), reverse=True)
        
        report = f"""
        <h3>Top 10 Bandwidth Consumers - Last 24 Hours</h3>
        <table border="1" cellpadding="5">
            <tr><th>Rank</th><th>IP Address</th><th>Device</th><th>Usage</th></tr>
        """
        
        for i, (ip, device, usage) in enumerate(devices[:10], 1):
            report += f"""
            <tr>
                <td>{i}</td>
                <td>{ip}</td>
                <td>{device}</td>
                <td>{usage}</td>
            </tr>
            """
        
        report += """
        </table>
        <p>Note: Data includes both incoming and outgoing traffic.</p>
        <p>Report generated at: """ + time.strftime('%H:%M:%S') + """</p>
        """
        self.report_generated.emit(report)
    
    def generate_protocol_report(self):
        """Generate protocol analysis report (TCP and UDP only)."""
        protocols = {
            'TCP': {
                'percent': random.uniform(65, 85),  # TCP typically dominates
                'ports': '80 (HTTP), 443 (HTTPS), 22 (SSH), 3389 (RDP)',
                'description': 'Connection-oriented, reliable transport protocol'
            },
            'UDP': {
                'percent': random.uniform(15, 35),
                'ports': '53 (DNS), 123 (NTP), 161 (SNMP), 500 (IPSec)',
                'description': 'Connectionless, lightweight transport protocol'
            }
        }
        
        report = """
        <h3>Protocol Analysis Report</h3>
        <table border="1" cellpadding="5">
            <tr><th>Protocol</th><th>Percentage</th><th>Common Ports</th><th>Description</th></tr>
        """
        
        for proto, data in protocols.items():
            report += f"""
            <tr>
                <td>{proto}</td>
                <td>{data['percent']:.1f}%</td>
                <td>{data['ports']}</td>
                <td>{data['description']}</td>
            </tr>
            """
        
        report += """
        </table>
        <h4>Observations:</h4>
        <ul>
            <li>TCP dominates network traffic (web, secure shell, remote desktop)</li>
            <li>UDP usage is primarily for DNS, NTP, and other lightweight services</li>
            <li>Typical enterprise networks show 70-85% TCP and 15-30% UDP traffic</li>
        </ul>
        <p>Report generated at: """ + time.strftime('%H:%M:%S') + """</p>
        """
        self.report_generated.emit(report)
    
    def generate_security_report(self):
        """Generate security alert report."""
        alerts = [
            ("High", "Multiple failed SSH attempts", "192.168.1.15", time.strftime('%H:%M:%S')),
            ("Medium", "Port scan detected", "192.168.1.42", time.strftime('%H:%M:%S')),
            ("Low", "Unusual DNS query", "192.168.1.19", time.strftime('%H:%M:%S')),
            ("High", "Possible brute force attack", "192.168.1.23", time.strftime('%H:%M:%S')),
            ("Medium", "Suspicious HTTP request", "192.168.1.8", time.strftime('%H:%M:%S'))
        ]
        
        report = """
        <h3>Security Alert Report - Last 24 Hours</h3>
        <table border="1" cellpadding="5">
            <tr><th>Severity</th><th>Description</th><th>Source IP</th><th>Time</th></tr>
        """
        
        for severity, desc, ip, time_alert in alerts:
            color = "#ff0000" if severity == "High" else "#ff9900" if severity == "Medium" else "#ffff00"
            report += f"""
            <tr>
                <td bgcolor="{color}">{severity}</td>
                <td>{desc}</td>
                <td>{ip}</td>
                <td>{time_alert}</td>
            </tr>
            """
        
        report += """
        </table>
        <h4>Recommendations:</h4>
        <ul>
            <li>Investigate failed SSH attempts from 192.168.1.15</li>
            <li>Check 192.168.1.42 for port scanning activity</li>
            <li>Review firewall rules for suspicious HTTP traffic</li>
        </ul>
        <p>Report generated at: """ + time.strftime('%H:%M:%S') + """</p>
        """
        self.report_generated.emit(report)
    
    def generate_peak_usage_report(self):
        """Generate peak usage hours report."""
        hours = [
            ("08:00-09:00", "Morning logins", "High"),
            ("12:00-13:00", "Lunchtime browsing", "Medium"),
            ("14:00-15:00", "Backup operations", "High"),
            ("17:00-18:00", "Evening logoffs", "Medium"),
            ("22:00-23:00", "Nightly updates", "Low")
        ]
        
        report = """
        <h3>Peak Usage Hours Report - Typical Day</h3>
        <table border="1" cellpadding="5">
            <tr><th>Time Period</th><th>Activity</th><th>Traffic Level</th></tr>
        """
        
        for time_period, activity, level in hours:
            color = "#ff0000" if level == "High" else "#ff9900" if level == "Medium" else "#00ff00"
            report += f"""
            <tr>
                <td>{time_period}</td>
                <td>{activity}</td>
                <td bgcolor="{color}">{level}</td>
            </tr>
            """
        
        report += """
        </table>
        <h4>Analysis:</h4>
        <ul>
            <li>Highest traffic during morning login and afternoon backup periods</li>
            <li>Consider scheduling non-critical network operations during low-traffic periods</li>
            <li>Monitor for unusual traffic patterns outside these expected peaks</li>
        </ul>
        <p>Report generated at: """ + time.strftime('%H:%M:%S') + """</p>
        """
        self.report_generated.emit(report)