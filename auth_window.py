from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from admin_window import AdminWindow
from chef_window import ChefWindow
from waiter_window import WaiterWindow

class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Авторизация")
        self.setGeometry(400, 200, 300, 150)

        self.layout = QVBoxLayout()

        self.username_label = QLabel("Имя пользователя:")
        self.layout.addWidget(self.username_label)

        self.username_input = QLineEdit()
        self.layout.addWidget(self.username_input)

        self.password_label = QLabel("Пароль:")
        self.layout.addWidget(self.password_label)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.password_input)

        self.login_button = QPushButton("Войти")
        self.layout.addWidget(self.login_button)
        self.login_button.clicked.connect(self.login)

        self.setLayout(self.layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if username == "admin" and password == "admin":
            self.accept_login("admin")
        elif username == "chef" and password == "chef":
            self.accept_login("chef")
        elif username == "waiter" and password == "waiter":
            self.accept_login("waiter")

    def accept_login(self, role):
        self.close() 

        if role == "admin":
            self.open_admin_window()
        elif role == "chef":
            self.open_chef_window()
        elif role == "waiter":
            self.open_waiter_window()

    def open_admin_window(self):
        self.admin_window = AdminWindow()
        self.admin_window.show()

    def open_chef_window(self):
        self.chef_window = ChefWindow()
        self.chef_window.show()

    def open_waiter_window(self):
        self.waiter_window = WaiterWindow() 
        self.waiter_window.show()