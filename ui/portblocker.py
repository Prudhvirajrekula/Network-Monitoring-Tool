import psutil
import subprocess
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QLabel, QMessageBox,
    QInputDialog, QHeaderView
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal


class PortRefresher(QThread):
    result_ready = pyqtSignal(list)

    def run(self):
        ports = []
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'LISTEN' and conn.laddr:
                try:
                    proc = psutil.Process(conn.pid)
                    name = proc.name()
                except:
                    name = "Unknown"
                ports.append((conn.laddr.port, "TCP", name, "Open"))
        self.result_ready.emit(ports)


class PortBlocker(QWidget):
    def __init__(self):
        super().__init__()
        self.blocked_ports = set()
        self.init_ui()

        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_ports_async)
        self.refresh_timer.start(2000)

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Port Blocker")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # Buttons
        btn_layout = QHBoxLayout()
        self.block_btn = QPushButton("Block Port")
        self.block_btn.clicked.connect(self.block_port)
        self.unblock_btn = QPushButton("Unblock Port")
        self.unblock_btn.clicked.connect(self.unblock_port)
        btn_layout.addWidget(self.block_btn)
        btn_layout.addWidget(self.unblock_btn)
        layout.addLayout(btn_layout)

        # Table
        self.ports_table = QTableWidget()
        self.ports_table.setColumnCount(4)
        self.ports_table.setHorizontalHeaderLabels(["Port", "Protocol", "Process", "Status"])
        self.ports_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.ports_table)

        self.setLayout(layout)
        self.refresh_ports_async()

    def refresh_ports_async(self):
        self.refresh_worker = PortRefresher()
        self.refresh_worker.result_ready.connect(self.update_ports_table)
        self.refresh_worker.start()

    def update_ports_table(self, open_ports):
        self.ports_table.setRowCount(len(open_ports))
        for row, (port, proto, proc, status) in enumerate(open_ports):
            self.ports_table.setItem(row, 0, QTableWidgetItem(str(port)))
            self.ports_table.setItem(row, 1, QTableWidgetItem(proto))
            self.ports_table.setItem(row, 2, QTableWidgetItem(proc))

            status_item = QTableWidgetItem("Blocked" if port in self.blocked_ports else "Open")
            status_item.setBackground(Qt.red if port in self.blocked_ports else Qt.green)
            self.ports_table.setItem(row, 3, status_item)

    def block_port(self):
        port, ok = QInputDialog.getInt(self, "Block Port", "Enter port number:", 0, 1, 65535, 1)
        if ok:
            try:
                subprocess.run(
                    f'netsh advfirewall firewall add rule name="BlockPort{port}" dir=in action=block protocol=TCP localport={port}',
                    shell=True, check=True)
                self.blocked_ports.add(port)
                self.refresh_ports_async()
                QMessageBox.information(self, "Success", f"Port {port} blocked successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to block port:\n{str(e)}")

    def unblock_port(self):
        port, ok = QInputDialog.getInt(self, "Unblock Port", "Enter port number:", 0, 1, 65535, 1)
        if ok:
            try:
                subprocess.run(
                    f'netsh advfirewall firewall delete rule name="BlockPort{port}"',
                    shell=True, check=True)
                self.blocked_ports.discard(port)
                self.refresh_ports_async()
                QMessageBox.information(self, "Success", f"Port {port} unblocked successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to unblock port:\n{str(e)}")
