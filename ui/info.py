from PyQt5.QtWidgets import QLabel, QVBoxLayout
from PyQt5.QtCore import Qt

def setup_info_page(layout, dark_mode=False):
    layout.setSpacing(10)
    
    # Set text color based on theme
    text_color = "white" if dark_mode else "black"

    # Set consistent label styling for dark/light themes
    def styled_label(text):
        label = QLabel(text)
        label.setWordWrap(True)
        label.setTextFormat(Qt.RichText)
        label.setStyleSheet(f"color: {text_color}; font-size: 13px;")
        return label

    title = QLabel(f"<h2 style='color: {text_color};'>Application Information</h2>")
    title.setTextFormat(Qt.RichText)
    layout.addWidget(title)

    layout.addWidget(styled_label(f"<b style='color: {text_color};'>App Name:</b> Network Monitoring & Port Scanning Tool"))
    layout.addWidget(styled_label(f"<b style='color: {text_color};'>Version:</b> 1.0.3"))
    layout.addWidget(styled_label(f"<b style='color: {text_color};'>Last Updated:</b> May 1, 2025"))
    layout.addWidget(styled_label(f"<b style='color: {text_color};'>Developer:</b> Jash, Jay, Prudhviraj, Madhu (Capstone Project 2025)"))
    layout.addWidget(styled_label(f"<b style='color: {text_color};'>License:</b> MIT License"))
    layout.addWidget(styled_label(f"<b style='color: {text_color};'>Technologies Used:</b><br>"
                                 f"• Python 3<br>"
                                 f"• PyQt5<br>"
                                 f"• psutil, folium, requests, matplotlib<br>"
                                 f"• Windows Firewall API (via subprocess)"))

    link_color = "#1abc9c" if dark_mode else "#2980b9"
    layout.addWidget(styled_label(
        f"For source code or collaboration, visit the "
        f"<a href='https://github.com/jash218/Basic-Network-Monitoring/' style='color:{link_color};'>GitHub Repository</a>."
    ))

    layout.addStretch()

# Function to update the information page when theme changes
def update_info_theme(info_page, dark_mode):
    # Clear existing layout
    for i in reversed(range(info_page.layout().count())):
        widget = info_page.layout().itemAt(i).widget()
        if widget:
            widget.deleteLater()
    
    # Rebuild with new theme
    setup_info_page(info_page.layout(), dark_mode)
