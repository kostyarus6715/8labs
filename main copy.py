import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,QTableWidgetItem,QTableWidget, QLineEdit, QComboBox, QMessageBox
from PyQt6.QtGui import QIcon
from db import get_db_connection, add_employee, get_all_employees, edit_employee, delete_employee, create_table
import sqlite3
class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Авторизация")
        self.setWindowIcon(QIcon("icon.png"))
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

        # Проводим проверку на успешную авторизацию
        if username == "admin" and password == "admin":  # Условие успешной авторизации
            self.accept_login()

    def accept_login(self):
        # Закрываем окно авторизации и открываем окно администратора
        self.close()  # Закрываем окно авторизации
        self.open_admin_window()

    def open_admin_window(self):
        self.admin_window = AdminWindow()
        self.admin_window.show()


class AdminWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Администрирование")
        self.setWindowIcon(QIcon("icon.png"))
        self.setGeometry(400, 200, 600, 400)

        self.layout = QVBoxLayout()

        # Кнопки для функционала администратора
        self.register_button = QPushButton("Регистрация новых пользователей")
        self.layout.addWidget(self.register_button)
        self.register_button.clicked.connect(self.register_user)

        self.view_employees_button = QPushButton("Просмотр сотрудников")
        self.layout.addWidget(self.view_employees_button)
        self.view_employees_button.clicked.connect(self.view_employees)

        self.setLayout(self.layout)

    def register_user(self):
        # Логика регистрации нового пользователя
        self.registration_window = RegistrationWindow()
        self.registration_window.show()

    def fire_user(self):
        # Логика перевода пользователя в статус "уволен"
        employee = self.select_employee_for_firing()
        if employee:
            employee_id = employee[0]  # Assuming the employee ID is at index 0
            edit_employee(employee_id, status="Уволен")
            QMessageBox.information(self, "Успех", "Пользователь переведен в статус 'Уволен'.")

    def select_employee_for_firing(self):
        # Функция для выбора сотрудника для перевода в статус "уволен"
        employees = get_all_employees()
        # Здесь можно добавить окно для выбора сотрудника
        # Для примера, просто вернем первого сотрудника
        return employees[0] if employees else None

    def view_employees(self):
        self.employee_window = EmployeeManagementWindow()
        self.employee_window.show()


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

        # Добавление нового сотрудника в базу
        try:
            add_employee(last_name, first_name, middle_name, username, password, role, status)
            QMessageBox.information(self, "Успех", "Новый пользователь добавлен успешно!")
            self.close()  # Закрываем окно
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении данных: {e}")


class EmployeeManagementWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Управление сотрудниками")
        self.setGeometry(400, 200, 600, 400)

        self.layout = QVBoxLayout()

        # Таблица сотрудников
        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        self.load_employees()

        # Кнопки
        self.add_button = QPushButton("Добавить сотрудника")
        self.add_button.clicked.connect(self.add_employee)
        self.layout.addWidget(self.add_button)

        self.edit_button = QPushButton("Редактировать сотрудника")
        self.edit_button.clicked.connect(self.edit_employee)
        self.layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Удалить сотрудника")
        self.delete_button.clicked.connect(self.delete_employee)
        self.layout.addWidget(self.delete_button)

        self.setLayout(self.layout)

    def load_employees(self):
        self.table.setRowCount(0)
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Фамилия", "Имя", "Отчество", "Логин", "Пароль", "Роль", "Статус"])

        employees = get_all_employees()
        for row_num, employee in enumerate(employees):
            self.table.insertRow(row_num)
            self.table.setItem(row_num, 0, QTableWidgetItem(str(employee["id"])))
            self.table.setItem(row_num, 1, QTableWidgetItem(employee["last_name"]))
            self.table.setItem(row_num, 2, QTableWidgetItem(employee["first_name"]))
            self.table.setItem(row_num, 3, QTableWidgetItem(employee["middle_name"]))
            self.table.setItem(row_num, 4, QTableWidgetItem(employee["username"]))
            self.table.setItem(row_num, 5, QTableWidgetItem(employee["password"]))
            self.table.setItem(row_num, 6, QTableWidgetItem(employee["role"]))
            self.table.setItem(row_num, 7, QTableWidgetItem(employee["status"]))

    def add_employee(self):
        self.registration_window = RegistrationWindow()
        self.registration_window.show()

    def edit_employee(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите сотрудника для редактирования.")
            return

        id = self.table.item(row, 0).text()
        # Открытие окна редактирования с данными выбранного сотрудника
        employee = get_employee_by_username(self.table.item(row, 4).text())  # По логину

        self.registration_window = RegistrationWindow()
        self.registration_window.last_name_input.setText(employee["last_name"])
        self.registration_window.first_name_input.setText(employee["first_name"])
        self.registration_window.middle_name_input.setText(employee["middle_name"])
        self.registration_window.username_input.setText(employee["username"])
        self.registration_window.password_input.setText(employee["password"])
        self.registration_window.role_combo.setCurrentText(employee["role"])
        self.registration_window.status_combo.setCurrentText(employee["status"])
        self.registration_window.save_button.setText("Обновить")
        self.registration_window.save_button.clicked.disconnect()
        self.registration_window.save_button.clicked.connect(lambda: self.save_edited_employee(employee["id"]))
        self.registration_window.show()

    def save_edited_employee(self, id):
        last_name = self.registration_window.last_name_input.text()
        first_name = self.registration_window.first_name_input.text()
        middle_name = self.registration_window.middle_name_input.text()
        username = self.registration_window.username_input.text()
        password = self.registration_window.password_input.text()
        role = self.registration_window.role_combo.currentText()
        status = self.registration_window.status_combo.currentText()

        edit_employee(id, last_name, first_name, middle_name, username, password, role, status)
        self.load_employees()

    def delete_employee(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите сотрудника для удаления.")
            return
        employee_id = self.table.item(row, 0).text()
        delete_employee(employee_id)
        self.load_employees()

def get_employee_by_username(username):
    conn = get_db_connection()  # Используем уже существующую функцию для подключения к базе данных
    cursor = conn.cursor()
    query = "SELECT * FROM employees WHERE username = ?"
    cursor.execute(query, (username,))
    employee = cursor.fetchone()
    conn.close()
    return employee


if __name__ == "__main__":
    create_table()
    app = QApplication(sys.argv)

    auth_window = AuthWindow()
    auth_window.show()

    sys.exit(app.exec())
