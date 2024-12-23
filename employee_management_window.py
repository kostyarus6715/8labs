from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox
from db import get_all_employees, delete_employee, get_employee_by_username, edit_employee
from registration_window import RegistrationWindow

class EmployeeManagementWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Управление сотрудниками")
        self.setGeometry(400, 200, 600, 400)

        self.layout = QVBoxLayout()

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        self.load_employees()

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
        employee = get_employee_by_username(self.table.item(row, 4).text())

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
