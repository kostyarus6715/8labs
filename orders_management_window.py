from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QComboBox, QMessageBox, QLineEdit, QLabel, QListWidget
from PyQt6.QtCore import Qt
from payment_window import PaymentWindow
import sqlite3

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

class OrdersManagementWindow(QWidget):
    def __init__(self, role):
        super().__init__()

        self.role = role 
        self.setWindowTitle("Управление заказами")
        self.setGeometry(400, 200, 800, 600)

        self.layout = QVBoxLayout()

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        self.load_orders()

        # Кнопки для администратора
        if self.role == 'admin':
            self.add_button = QPushButton("Добавить заказ")
            self.add_button.clicked.connect(self.add_order)
            self.layout.addWidget(self.add_button)

            self.toggle_payment_button = QPushButton("Изменить статус оплаты")
            self.toggle_payment_button.clicked.connect(self.toggle_payment_status)
            self.layout.addWidget(self.toggle_payment_button)

        # Кнопки для официанта и повара
        if self.role in ['waiter', 'cook']:
            self.update_status_button = QPushButton("Изменить статус")
            self.update_status_button.clicked.connect(self.update_order_status)
            self.layout.addWidget(self.update_status_button)

            self.payment_button = QPushButton("Завершить оплату")
            self.payment_button.clicked.connect(self.process_payment)
            self.layout.addWidget(self.payment_button)

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

    def add_order(self):
        self.add_order_window = AddOrderWindow(self)
        self.add_order_window.show()

    def update_order_status(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите заказ для изменения статуса.")
            return

        order_id = self.table.item(row, 0).text()
        new_status = "Готово"

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
        conn.commit()
        conn.close()
        self.load_orders()
        QMessageBox.information(self, "Успех", "Статус заказа изменен!")

    def toggle_payment_status(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите заказ для изменения статуса оплаты.")
            return

        order_id = self.table.item(row, 0).text()
        current_status = self.table.item(row, 6).text()
        print(f"Выбран заказ с ID {order_id}. Текущий статус оплаты: {current_status}")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT is_paid FROM orders WHERE id = ?", (order_id,))
        order_data = cursor.fetchone()
        conn.close()

        if not order_data:
            QMessageBox.warning(self, "Ошибка", "Не удалось найти заказ в базе данных.")
            return

        current_status_in_db = order_data["is_paid"]
        print(f"Статус оплаты в базе данных: {'Оплачен' if current_status_in_db else 'Не оплачен'}")

        new_status = 0 if current_status_in_db == 1 else 1
        print(f"Новый статус оплаты: {'Оплачен' if new_status else 'Не оплачен'}") 

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE orders SET is_paid = ? WHERE id = ?", (new_status, order_id))
        conn.commit()
        conn.close()

        print(f"Статус оплаты для заказа с ID {order_id} успешно обновлен.")

        self.load_orders()
        self.table.viewport().update()

        QMessageBox.information(self, "Успех", "Статус оплаты изменен!")

    def process_payment(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите заказ для оплаты.")
            return

        order_id = int(self.table.item(row, 0).text())
        total_amount = float(self.table.item(row, 5).text())

        payment_window = PaymentWindow(order_id, total_amount)
        payment_window.show()

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

