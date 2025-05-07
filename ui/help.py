from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton, QTextEdit, QScrollArea, QWidget
from PyQt5.QtCore import Qt

def create_faq_item(question, answer, dark_mode=False):
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)

    btn = QPushButton(f"❓ {question}")
    btn.setStyleSheet("text-align: left; padding: 8px; font-weight: bold;")
    btn.setCheckable(True)

    answer_box = QTextEdit(answer)
    answer_box.setReadOnly(True)
    answer_box.setVisible(False)
    
    if dark_mode:
        answer_box.setStyleSheet("background: #34495e; color: white; padding: 6px;")
    else:
        answer_box.setStyleSheet("background: #f0f0f0; padding: 6px;")

    def toggle():
        answer_box.setVisible(btn.isChecked())

    btn.clicked.connect(toggle)

    layout.addWidget(btn)
    layout.addWidget(answer_box)
    return container

def setup_help_page(layout, dark_mode=False):
    title = QLabel("<h2>Help & FAQ</h2>")
    title.setAlignment(Qt.AlignLeft)
    layout.addWidget(title)

    # FAQ section inside a scrollable widget
    faq_scroll = QScrollArea()
    faq_scroll.setWidgetResizable(True)
    faq_container = QWidget()
    faq_layout = QVBoxLayout(faq_container)

    faqs = [
        ("How do I scan my network?",
         "Go to 'Network Scanner', click 'Scan Network', and wait for results."),

        ("How do I block a port?",
         "Navigate to 'Port Blocker', enter the port number, and click 'Block Port'."),

        ("Why can't I see my IP in Trace Visualizer?",
         "Trace might not work on local/private IPs like 192.168.x.x due to how routing works."),

        ("How do I enable dark mode?",
         "Go to 'Settings' and toggle the 'Dark Mode' switch."),

        ("How do I export reports?",
         "Visit the 'Reports' tab and click on any report to auto-generate it. Export options will appear soon.")
    ]

    for q, a in faqs:
        faq_layout.addWidget(create_faq_item(q, a, dark_mode))

    faq_layout.addStretch()
    faq_scroll.setWidget(faq_container)
    layout.addWidget(faq_scroll)

    # Footer
    contact = QLabel("<br><b>Still need help?</b><br>Email: support@networkmonitor.app")
    contact.setTextFormat(Qt.RichText)
    layout.addWidget(contact)
    layout.addStretch()

def update_help_theme(help_page, dark_mode):
    # Clear existing layout
    for i in reversed(range(help_page.layout().count())):
        widget = help_page.layout().itemAt(i).widget()
        if widget:
            widget.deleteLater()
    
    # Rebuild with new theme
    setup_help_page(help_page.layout(), dark_mode)
