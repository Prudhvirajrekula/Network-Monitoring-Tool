from PyQt5.QtWidgets import (
    QLabel, QHBoxLayout, QPushButton, QVBoxLayout, QComboBox, QMessageBox
)
from PyQt5.QtGui import QColor, QPalette
import os

def setup_settings_page(settings_layout, toggle_dark_mode_cb, change_refresh_rate_cb):
    settings_layout.addWidget(QLabel("<h2>Application Settings</h2>"))

    # Dark Mode Toggle
    dark_mode_layout = QHBoxLayout()
    dark_mode_label = QLabel("Dark Mode:")
    dark_mode_layout.addWidget(dark_mode_label)

    dark_mode_button = QPushButton("OFF")
    dark_mode_button.setCheckable(True)
    dark_mode_button.setFixedWidth(80)
    dark_mode_button.clicked.connect(toggle_dark_mode_cb)
    dark_mode_layout.addWidget(dark_mode_button)
    dark_mode_layout.addStretch()
    settings_layout.addLayout(dark_mode_layout)

    # Refresh Rate Dropdown
    refresh_layout = QHBoxLayout()
    refresh_label = QLabel("Refresh Rate (seconds):")
    refresh_layout.addWidget(refresh_label)

    refresh_dropdown = QComboBox()
    refresh_dropdown.addItems(["3", "5", "10"])
    refresh_dropdown.setCurrentText("3")
    refresh_dropdown.currentTextChanged.connect(lambda _: change_refresh_rate_cb())
    refresh_dropdown.setFixedWidth(80)
    refresh_layout.addWidget(refresh_dropdown)
    refresh_layout.addStretch()
    settings_layout.addLayout(refresh_layout)

    # Reset and Clear Buttons
    action_layout = QHBoxLayout()

    reset_btn = QPushButton("Reset Settings")
    reset_btn.clicked.connect(lambda: QMessageBox.information(None, "Reset", "Settings reset."))
    clear_btn = QPushButton("Clear Logs")
    clear_btn.clicked.connect(lambda: QMessageBox.information(None, "Clear", "Logs cleared."))

    action_layout.addWidget(reset_btn)
    action_layout.addWidget(clear_btn)
    settings_layout.addLayout(action_layout)

    # Open Config Folder Button
    config_btn = QPushButton("Open Config Folder")
    config_btn.clicked.connect(lambda: os.startfile(os.getcwd()))  # or specific config path
    settings_layout.addWidget(config_btn)

    settings_layout.addStretch()

    return dark_mode_button, refresh_dropdown
