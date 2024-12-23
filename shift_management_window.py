from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTimeEdit, QPushButton, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QDateEdit, QListWidget, QAbstractItemView
from PyQt6.QtCore import QDate, QTime, Qt
import sqlite3

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row 
    return conn

def get_all_shifts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT shifts.id, shifts.date, shifts.start_time, shifts.end_time, 
               COUNT(employees.id) AS employee_count, 
               GROUP_CONCAT(employees.id) AS employee_ids
        FROM Shifts shifts
        LEFT JOIN EmployeeShifts es ON shifts.id = es.shift_id
        LEFT JOIN employees ON es.employee_id = employees.id
        GROUP BY shifts.id
    """)
    shifts = cursor.fetchall()
    conn.close()

    return [{"id": shift["id"], "date": shift["date"], "start_time": shift["start_time"], 
             "end_time": shift["end_time"], "employee_count": shift["employee_count"], 
             "employee_ids": shift["employee_ids"] if shift["employee_ids"] else ""} 
            for shift in shifts]

def get_shift_by_id(shift_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM shifts WHERE id = ?", (shift_id,))
    shift = cursor.fetchone()
    conn.close()
    return shift


def create_shift(date, start_time, end_time, selected_employees):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Shifts (date, start_time, end_time) VALUES (?, ?, ?)", 
                   (date, start_time, end_time))
    shift_id = cursor.lastrowid

    for employee_id in selected_employees:
        cursor.execute("INSERT INTO EmployeeShifts (shift_id, employee_id) VALUES (?, ?)", 
                       (shift_id, employee_id))

    conn.commit()
    conn.close()

def edit_shift(shift_id, date, start_time, end_time, selected_employees):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Shifts SET date = ?, start_time = ?, end_time = ? WHERE id = ?",
                   (date, start_time, end_time, shift_id))

    cursor.execute("DELETE FROM EmployeeShifts WHERE shift_id = ?", (shift_id,))
    for employee_id in selected_employees:
        cursor.execute("INSERT INTO EmployeeShifts (shift_id, employee_id) VALUES (?, ?)",
                       (shift_id, employee_id))

    conn.commit()
    conn.close()

class ShiftManagementWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Управление сменами")
        self.setGeometry(400, 200, 600, 400)

        self.layout = QVBoxLayout()

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        self.load_shifts()


        self.add_button = QPushButton("Добавить смену")
        self.add_button.clicked.connect(self.add_shift)
        self.layout.addWidget(self.add_button)

        self.edit_button = QPushButton("Редактировать смену")
        self.edit_button.clicked.connect(self.edit_shift)
        self.layout.addWidget(self.edit_button)

        self.setLayout(self.layout)

    def load_shifts(self):
        self.table.setRowCount(0)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Дата", "Время начала", "Время окончания", "Сотрудники"])

        shifts = get_all_shifts()
        for row_num, shift in enumerate(shifts):
            self.table.insertRow(row_num)
            self.table.setItem(row_num, 0, QTableWidgetItem(str(shift["id"])))
            self.table.setItem(row_num, 1, QTableWidgetItem(shift["date"]))
            self.table.setItem(row_num, 2, QTableWidgetItem(shift["start_time"]))
            self.table.setItem(row_num, 3, QTableWidgetItem(shift["end_time"]))
            self.table.setItem(row_num, 4, QTableWidgetItem(str(shift["employee_count"])))

    def add_shift(self):
        self.shift_window = ShiftWindow(self)
        self.shift_window.show()

    def edit_shift(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите смену для редактирования.")
            return

        shift_id = self.table.item(row, 0).text() 
        shift = get_shift_by_id(shift_id)

        self.shift_window = ShiftWindow(self, shift)
        self.shift_window.show()

    def update_shifts(self):
        self.load_shifts()

class ShiftWindow(QWidget):
    def __init__(self, parent=None, shift=None):
        super().__init__()

        self.parent = parent
        self.setWindowTitle("Создание/Редактирование смены")
        self.setGeometry(400, 200, 400, 400)

        self.layout = QVBoxLayout()

        self.date_label = QLabel("Дата:")
        self.layout.addWidget(self.date_label)
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setMaximumDate(QDate.currentDate().addDays(5))
        self.layout.addWidget(self.date_input)

        self.start_time_label = QLabel("Время начала:")
        self.layout.addWidget(self.start_time_label)
        self.start_time_input = QTimeEdit()
        self.layout.addWidget(self.start_time_input)

        self.end_time_label = QLabel("Время окончания:")
        self.layout.addWidget(self.end_time_label)
        self.end_time_input = QTimeEdit()
        self.layout.addWidget(self.end_time_input)

        self.employee_label = QLabel("Выберите сотрудников (от 4 до 7):")
        self.layout.addWidget(self.employee_label)
        self.employee_list_widget = QListWidget()
        self.employee_list_widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.layout.addWidget(self.employee_list_widget)

        self.load_employees()

        if shift:
            date_str = shift["date"]
            date_obj = QDate.fromString(date_str, "yyyy-MM-dd")
            self.date_input.setDate(date_obj)

            start_time_str = shift["start_time"]
            start_time_obj = QTime.fromString(start_time_str, "HH:mm")
            self.start_time_input.setTime(start_time_obj)

            end_time_str = shift["end_time"]
            end_time_obj = QTime.fromString(end_time_str, "HH:mm")
            self.end_time_input.setTime(end_time_obj)

            if "employee_ids" in shift and shift["employee_ids"]:
                selected_employee_ids = shift["employee_ids"].split(",")
                for employee_id in selected_employee_ids:
                    item = self.employee_list_widget.findItems(employee_id, Qt.MatchExactly)
                    if item:
                        item[0].setSelected(True)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_shift)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

        self.shift = shift

    def load_employees(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, last_name, first_name FROM employees")
        employees = cursor.fetchall()
        conn.close()


        for employee in employees:
            full_name = f"{employee['last_name']} {employee['first_name']}"
            self.employee_list_widget.addItem(str(employee['id']) + " - " + full_name)

    def save_shift(self):
        date = self.date_input.date().toString("yyyy-MM-dd")
        start_time = self.start_time_input.time().toString("HH:mm")
        end_time = self.end_time_input.time().toString("HH:mm")

        selected_items = self.employee_list_widget.selectedItems()
        selected_employees = []

        print(f"Выбрано сотрудников: {len(selected_items)}")

        for item in selected_items:
            employee_text = item.text()
            employee_id = employee_text.split(" - ")[0]

            selected_employees.append(employee_id)

        print(f"Количество сотрудников, добавленных в список: {len(selected_employees)}")

        if len(selected_employees) < 4 or len(selected_employees) > 7:
            QMessageBox.warning(self, "Ошибка", "Количество сотрудников должно быть от 4 до 7!")
            return

        if not date or not start_time or not end_time or not selected_employees:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
            return

        try:
            if self.shift:
                edit_shift(self.shift["id"], date, start_time, end_time, selected_employees)
                QMessageBox.information(self, "Успех", "Смена успешно обновлена!")
            else:
                create_shift(date, start_time, end_time, selected_employees)
                QMessageBox.information(self, "Успех", "Смена успешно создана!")

            self.parent.update_shifts()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении смены: {e}")
