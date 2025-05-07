from ui.frontend import NetworkMonitor
import sys
from PyQt5.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    window = NetworkMonitor()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()