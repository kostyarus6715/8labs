from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox
from db import add_employee

class RegistrationWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Регистрация нового пользователя")
        self.setGeometry(400, 200, 400, 350)

        self.layout = QVBoxLayout()

        self.last_name_label = QLabel("Фамилия:")
        self.layout.addWidget(self.last_name_label)
        self.last_name_input = QLineEdit()
        self.layout.addWidget(self.last_name_input)

        self.first_name_label = QLabel("Имя:")
        self.layout.addWidget(self.first_name_label)
        self.first_name_input = QLineEdit()
        self.layout.addWidget(self.first_name_input)

        self.middle_name_label = QLabel("Отчество:")
        self.layout.addWidget(self.middle_name_label)
        self.middle_name_input = QLineEdit()
        self.layout.addWidget(self.middle_name_input)

        self.username_label = QLabel("Логин:")
        self.layout.addWidget(self.username_label)
        self.username_input = QLineEdit()
        self.layout.addWidget(self.username_input)

        self.password_label = QLabel("Пароль:")
        self.layout.addWidget(self.password_label)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.password_input)

        self.role_label = QLabel("Роль:")
        self.layout.addWidget(self.role_label)
        self.role_combo = QComboBox()
        self.role_combo.addItems(["Официант", "Повар"])
        self.layout.addWidget(self.role_combo)

        self.status_label = QLabel("Статус:")
        self.layout.addWidget(self.status_label)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Работает", "В отпуске", "Уволен"])
        self.layout.addWidget(self.status_combo)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_user)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

    def save_user(self):
        last_name = self.last_name_input.text()
        first_name = self.first_name_input.text()
        middle_name = self.middle_name_input.text()
        username = self.username_input.text()
        password = self.password_input.text()
        role = self.role_combo.currentText()
        status = self.status_combo.currentText()

        if not last_name or not first_name or not middle_name or not username or not password or not role:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
            return

        try:
            add_employee(last_name, first_name, middle_name, username, password, role, status)
            QMessageBox.information(self, "Успех", "Новый пользователь добавлен успешно!")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении данных: {e}")
