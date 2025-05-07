from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QEvent, QPropertyAnimation, QEasingCurve

class CollapsibleSidebar(QWidget):
    def __init__(self, pages_order, switch_callback, dark_mode=True):
        super().__init__()
        self.expanded_width = 220
        self.collapsed_width = 60
        self.setFixedWidth(self.collapsed_width)
        self.setStyleSheet("background-color: #2c3e50;" if dark_mode else "background-color: #ecf0f1;")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.dark_mode = dark_mode
        self.buttons = []
        self.page_data = []  # Store (icon, label) tuples

        # Top and bottom items with emojis
        top_items = [
            ("\U0001F3E0", "Home"), ("\U0001F4CA", "Data Analysis"), ("\U0001F4C1", "Reports"),
            ("\U0001F50D", "Network Scanner"), ("\U0001F512", "Port Blocker"), ("\U0001F310", "Trace Visualizer")
        ]
        bottom_items = [
            ("\u2699", "Settings"), ("\u2139", "Information"), ("\u2753", "Help")
        ]

        combined_items = top_items + bottom_items

        for index, (icon, label) in enumerate(combined_items):
            btn = QPushButton(icon)
            btn.setFont(QFont("Arial", 11))
            btn.setStyleSheet(button_style(self.dark_mode))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.clicked.connect(lambda checked, i=index: switch_callback(i))
            self.layout.addWidget(btn)
            self.buttons.append(btn)
            self.page_data.append((icon, label))

        self.layout.addStretch()
        self.installEventFilter(self)
        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Enter:
            self.expand()
        elif event.type() == QEvent.Leave:
            self.collapse()
        return super().eventFilter(obj, event)

    def expand(self):
        self.animation.stop()
        self.animation.setStartValue(self.width())
        self.animation.setEndValue(self.expanded_width)
        self.animation.start()
        for btn, (icon, label) in zip(self.buttons, self.page_data):
            btn.setText(f"{icon} {label}")

    def collapse(self):
        self.animation.stop()
        self.animation.setStartValue(self.width())
        self.animation.setEndValue(self.collapsed_width)
        self.animation.start()
        for btn, (icon, _) in zip(self.buttons, self.page_data):
            btn.setText(f"{icon}")

    def update_theme(self, dark):
        self.dark_mode = dark
        self.setStyleSheet("background-color: #2c3e50;" if dark else "background-color: #ecf0f1;")
        for btn in self.buttons:
            btn.setStyleSheet(button_style(self.dark_mode))

    def apply_theme(self, dark_mode):
        self.setStyleSheet("background-color: #2c3e50;" if dark_mode else "background-color: #ecf0f1;")
        for btn in self.buttons:
            btn.setStyleSheet(button_style(dark_mode))


def create_navigation_panel(pages_order, switch_callback, dark_mode=True):
    return CollapsibleSidebar(pages_order, switch_callback, dark_mode)

def button_style(dark):
    return f"""
    QPushButton {{
        background-color: transparent;
        color: {'white' if dark else 'black'};
        border: none;
        padding: 10px;
        text-align: left;
    }}
    QPushButton:hover {{
        background-color: #1abc9c;
    }}
    """