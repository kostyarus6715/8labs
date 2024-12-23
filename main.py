import sys
from PyQt6.QtWidgets import QApplication
from auth_window import AuthWindow
from db import create_table
if __name__ == "__main__":
    create_table()
    app = QApplication(sys.argv)

    auth_window = AuthWindow()
    auth_window.show()
    sys.exit(app.exec())
