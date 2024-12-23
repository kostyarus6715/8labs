from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox
from db import get_shifts, get_employees, assign_employee_to_shift

class AssignShiftWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Назначение сотрудников на смены")
        self.setGeometry(400, 200, 600, 400)

        self.layout = QVBoxLayout()

        self.shift_label = QLabel("Выберите смену:")
        self.layout.addWidget(self.shift_label)

        self.shift_combo = QComboBox()
        self.layout.addWidget(self.shift_combo)
        self.load_shifts()

        self.employee_label = QLabel("Выберите сотрудника:")
        self.layout.addWidget(self.employee_label)

        self.employee_combo = QComboBox()
        self.layout.addWidget(self.employee_combo)
        self.load_employees()

        self.assign_button = QPushButton("Назначить")
        self.assign_button.clicked.connect(self.assign_employee)
        self.layout.addWidget(self.assign_button)

        self.setLayout(self.layout)

    def load_shifts(self):
        shifts = get_shifts()
        for shift in shifts:
            self.shift_combo.addItem(f"{shift['start_time']} - {shift['end_time']} ({shift['role']})", shift['id'])

    def load_employees(self):
        employees = get_employees()
        for employee in employees:
            self.employee_combo.addItem(f"{employee['last_name']} {employee['first_name']} ({employee['role']})", employee['id'])

    def assign_employee(self):
        shift_id = self.shift_combo.currentData()
        employee_id = self.employee_combo.currentData()

        if not shift_id or not employee_id:
            QMessageBox.warning(self, "Ошибка", "Выберите смену и сотрудника для назначения!")
            return

        try:
            assign_employee_to_shift(employee_id, shift_id)
            QMessageBox.information(self, "Успех", "Сотрудник успешно назначен на смену!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при назначении: {e}")
