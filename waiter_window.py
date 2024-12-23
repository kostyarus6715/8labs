from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QComboBox, QMessageBox, QLineEdit, QLabel, QListWidget,QInputDialog
from PyQt6.QtCore import Qt
from payment_window import PaymentWindow
import sqlite3

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

class WaiterWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Окно официанта")
        self.setGeometry(400, 200, 800, 600)

        self.layout = QVBoxLayout()

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        self.load_orders()

        self.update_status_button = QPushButton("Изменить статус")
        self.update_status_button.clicked.connect(self.update_order_status)
        self.layout.addWidget(self.update_status_button)
        self.add_order_button = QPushButton("Добавить новый заказ")
        self.add_order_button.clicked.connect(self.add_new_order)
        self.layout.addWidget(self.add_order_button)

        self.setLayout(self.layout)

    def load_orders(self):
        self.table.setRowCount(0)
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Статус", "Столик", "Кол-во клиентов", "Дата", "Стоимость", "Оплата"])

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, status, table_number, num_clients, date, total_price, is_paid FROM orders")
        orders = cursor.fetchall()
        conn.close()

        for row_num, order in enumerate(orders):
            self.table.insertRow(row_num)
            self.table.setItem(row_num, 0, QTableWidgetItem(str(order["id"])))
            self.table.setItem(row_num, 1, QTableWidgetItem(order["status"]))
            self.table.setItem(row_num, 2, QTableWidgetItem(str(order["table_number"])))
            self.table.setItem(row_num, 3, QTableWidgetItem(str(order["num_clients"])))
            self.table.setItem(row_num, 4, QTableWidgetItem(order["date"]))
            self.table.setItem(row_num, 5, QTableWidgetItem(str(order["total_price"])))
            self.table.setItem(row_num, 6, QTableWidgetItem("Оплачен" if order["is_paid"] else "Не оплачен"))

    def update_order_status(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите заказ для изменения статуса.")
            return

        order_id = self.table.item(row, 0).text()
        current_status = self.table.item(row, 1).text()
        is_paid = self.table.item(row, 6).text() == "Оплачен"

        if is_paid:
            QMessageBox.warning(self, "Ошибка", "Невозможно изменить статус для оплаченного заказа.")
            return

        available_statuses = ["Принят", "Готовится", "Доставлен"]
        
        if current_status in available_statuses:
            new_status, ok = QInputDialog.getItem(self, "Выберите новый статус", "Выберите новый статус для заказа:", available_statuses, 0, False)
            if ok and new_status != current_status:
                self.update_status_in_db(order_id, new_status)
                QMessageBox.information(self, "Успех", f"Статус заказа изменен на '{new_status}'.")
            else:
                QMessageBox.warning(self, "Ошибка", "Вы не выбрали новый статус или статус не изменился.")
        else:
            QMessageBox.warning(self, "Ошибка", "Статус заказа не может быть изменен в данный момент.")

    def update_status_in_db(self, order_id, new_status):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
        conn.commit()
        conn.close()

        self.load_orders()

    def add_new_order(self):
        self.add_order_window = AddOrderWindow(self)
        self.add_order_window.show()

class AddOrderWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Добавление нового заказа")
        self.setGeometry(400, 200, 400, 400)

        self.layout = QVBoxLayout()

        self.table_number_label = QLabel("Номер столика:")
        self.layout.addWidget(self.table_number_label)
        self.table_number_input = QLineEdit()
        self.layout.addWidget(self.table_number_input)

        self.num_clients_label = QLabel("Количество клиентов:")
        self.layout.addWidget(self.num_clients_label)
        self.num_clients_input = QLineEdit()
        self.layout.addWidget(self.num_clients_input)

        self.status_label = QLabel("Статус заказа:")
        self.layout.addWidget(self.status_label)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Принят", "Готовится", "Доставлен"])
        self.layout.addWidget(self.status_combo)

        self.items_label = QLabel("Выберите заказанные блюда:")
        self.layout.addWidget(self.items_label)

        self.dish_list = QListWidget()
        self.dish_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.load_dishes()
        self.layout.addWidget(self.dish_list)

        self.save_button = QPushButton("Сохранить")
        self.layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_order)

        self.setLayout(self.layout)

    def load_dishes(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM dishes")
        dishes = cursor.fetchall()
        conn.close()
        for dish in dishes:
            self.dish_list.addItem(dish["name"])

    def save_order(self):
        table_number = self.table_number_input.text()
        num_clients = self.num_clients_input.text()
        status = self.status_combo.currentText()
        selected_dishes = self.dish_list.selectedItems()
        try:
            table_number = int(table_number)
            if table_number < 1 or table_number > 20:
                raise ValueError("Номер столика должен быть от 1 до 20.")
        except ValueError as e:
            self.show_error_message(str(e))
            return

        if not num_clients.isdigit():
            self.show_error_message("Количество клиентов должно быть числом.")
            return

        if not selected_dishes:
            self.show_error_message("Выберите хотя бы одно блюдо.")
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO orders (table_number, num_clients, status, date) VALUES (?, ?, ?, datetime('now'))", 
                       (table_number, num_clients, status))
        order_id = cursor.lastrowid
        total_price = 0 

        for dish in selected_dishes:
            cursor.execute("SELECT price FROM dishes WHERE name = ?", (dish.text(),))
            dish_data = cursor.fetchone()
            if dish_data:
                price = dish_data["price"]
                total_price += price 
                cursor.execute("INSERT INTO order_items (order_id, item_name) VALUES (?, ?)", 
                               (order_id, dish.text()))

        cursor.execute("UPDATE orders SET total_price = ? WHERE id = ?", (total_price, order_id))
        conn.commit()
        conn.close()


        self.parent.load_orders()
        self.close()

    def show_error_message(self, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Ошибка")
        msg.setText(message)
        msg.exec()
