from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton,QTableWidgetItem,QTableWidget
from orders_management_window import OrdersManagementWindow
from shift_management_window import ShiftManagementWindow
from dish_management_window import DishManagementWindow 
from reports_window import ReportsWindow
from employee_management_window import EmployeeManagementWindow
import sqlite3

class AdminWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Администрирование")
        self.setGeometry(400, 200, 600, 400)

        self.layout = QVBoxLayout()

        self.view_employees_button = QPushButton("Просмотр сотрудников")
        self.layout.addWidget(self.view_employees_button)
        self.view_employees_button.clicked.connect(self.view_employees)

        self.manage_shifts_button = QPushButton("Управление сменами")
        self.layout.addWidget(self.manage_shifts_button)
        self.manage_shifts_button.clicked.connect(self.manage_shifts)

        self.order_management_button = QPushButton("Управление заказами")
        self.layout.addWidget(self.order_management_button)
        self.order_management_button.clicked.connect(self.orders_management)

        self.dish_management_button = QPushButton("Управление блюдами")
        self.layout.addWidget(self.dish_management_button)
        self.dish_management_button.clicked.connect(self.dish_management)

        self.reports_button = QPushButton("Генерация отчётов")
        self.layout.addWidget(self.reports_button)
        self.reports_button.clicked.connect(self.generate_reports)

        self.setLayout(self.layout)

    def view_employees(self):
        self.employee_window = EmployeeManagementWindow()
        self.employee_window.show()

    def manage_shifts(self):
        self.shift_window = ShiftManagementWindow()
        self.shift_window.show()

    def orders_management(self):
        self.orders_window = OrdersManagementWindow('admin') 
        self.orders_window.show()

    def dish_management(self):
        self.dish_window = DishManagementWindow() 
        self.dish_window.show()

    def generate_reports(self):
        # Открытие окна для генерации отчётов
        self.reports_window = ReportsWindow()
        self.reports_window.show()

class CashReceiptsWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Кассовые ордера")
        self.setGeometry(400, 200, 800, 600)

        self.layout = QVBoxLayout()

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        self.load_cash_receipts()

        self.setLayout(self.layout)

    def load_cash_receipts(self):
        # Загрузка кассовых ордеров
        self.table.setRowCount(0)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "ID заказа", "Способ оплаты", "Сумма", "Дата"])

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cash_receipts")
        receipts = cursor.fetchall()
        conn.close()

        for row_num, receipt in enumerate(receipts):
            self.table.insertRow(row_num)
            self.table.setItem(row_num, 0, QTableWidgetItem(str(receipt["id"])))
            self.table.setItem(row_num, 1, QTableWidgetItem(str(receipt["order_id"])))
            self.table.setItem(row_num, 2, QTableWidgetItem(receipt["payment_method"]))
            self.table.setItem(row_num, 3, QTableWidgetItem(str(receipt["amount"])))
            self.table.setItem(row_num, 4, QTableWidgetItem(receipt["date"]))
