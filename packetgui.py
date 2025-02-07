# Capstone Project start!
# Version 0.0.0



import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt6.QtCore import Qt  # Import Qt for alignment

class SquareWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Network Capstone Project 0.0.0")
        self.setGeometry(100, 100, 400, 400)  # Set position and size (square)

        layout = QVBoxLayout()

        # Add stretch to push buttons to the center vertically
        layout.addStretch()

        # Define buttons
        self.button1 = QPushButton("Play Game", self)
        self.button1.setFixedSize(200, 50)  # Set width and height
        self.button1.clicked.connect(self.on_button1_click)
        layout.addWidget(self.button1, alignment=Qt.AlignmentFlag.AlignHCenter)  # Center horizontally

        self.button2 = QPushButton("Actual Network S/W", self)
        self.button2.setFixedSize(200, 50)  # Set width and height
        self.button2.clicked.connect(self.on_button2_click)
        layout.addWidget(self.button2, alignment=Qt.AlignmentFlag.AlignHCenter)  # Center horizontally

        # Add stretch again to push buttons to the center vertically
        layout.addStretch()

        self.setLayout(layout)

    def on_button1_click(self):
        print("Button 1 clicked!")

    def on_button2_click(self):
        print("Button 2 clicked!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SquareWindow()
    window.show()
    sys.exit(app.exec())
