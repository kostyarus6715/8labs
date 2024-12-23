from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QDialog
import sqlite3

class ChefWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Окно повара")
        self.setGeometry(400, 200, 800, 400)

        self.layout = QVBoxLayout()

        self.title_label = QLabel("Список заказов:")
        self.layout.addWidget(self.title_label)

        self.order_table = QTableWidget(self)
        self.order_table.setColumnCount(5)
        self.order_table.setHorizontalHeaderLabels(["Номер заказа", "Стол", "Клиенты", "Статус", "Дата"])

        self.orders = self.get_orders_from_db()

        self.fill_order_table()

        self.layout.addWidget(self.order_table)

        self.change_status_button = QPushButton("Изменить статус на 'Готов'")
        self.change_status_button.clicked.connect(self.change_status)
        self.layout.addWidget(self.change_status_button)

        self.view_order_items_button = QPushButton("Посмотреть блюда заказа")
        self.view_order_items_button.clicked.connect(self.view_order_items)
        self.layout.addWidget(self.view_order_items_button)

        self.setLayout(self.layout)

    def get_orders_from_db(self):
        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT orders.id, orders.table_number, orders.num_clients, orders.status, orders.date 
            FROM orders
            ORDER BY orders.id
        """)
        orders = cursor.fetchall()
        conn.close()
        return orders

    def fill_order_table(self):
        self.order_table.setRowCount(len(self.orders))

        for i, order in enumerate(self.orders):
            self.order_table.setItem(i, 0, QTableWidgetItem(str(order["id"])))
            self.order_table.setItem(i, 1, QTableWidgetItem(str(order["table_number"])))
            self.order_table.setItem(i, 2, QTableWidgetItem(str(order["num_clients"])))
            self.order_table.setItem(i, 3, QTableWidgetItem(order["status"]))
            self.order_table.setItem(i, 4, QTableWidgetItem(order["date"]))

    def change_status(self):
        selected_row = self.order_table.currentRow()
        if selected_row == -1:
            self.show_error("Выберите заказ для изменения статуса.")
            return

        order_id = self.order_table.item(selected_row, 0).text()
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM orders WHERE id = ?", (order_id,))
        current_status = cursor.fetchone()
        conn.close()

        if current_status:
            current_status = current_status[0]

            if current_status == "Оплачен":
                self.show_error("Невозможно изменить статус с 'Оплачен' на 'Готов'.")
                return
        self.update_order_status(order_id, "Готов")
        self.orders = self.get_orders_from_db()
        self.fill_order_table()
        self.show_message("Статус заказа изменен на 'Готов'.")


    def update_order_status(self, order_id, status):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE orders
            SET status = ?
            WHERE id = ?
        """, (status, order_id))
        conn.commit()
        conn.close()

    def view_order_items(self):
        selected_row = self.order_table.currentRow()
        if selected_row == -1:
            self.show_error("Выберите заказ для просмотра блюд.")
            return

        order_id = self.order_table.item(selected_row, 0).text()
        items = self.get_order_items(order_id)
        self.show_order_items(order_id, items)

    def get_order_items(self, order_id):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT order_items.item_name
            FROM order_items
            WHERE order_items.order_id = ?
        """, (order_id,))
        items = cursor.fetchall()
        conn.close()
        return items

    def show_order_items(self, order_id, items):
        items_window = QDialog()
        items_window.setWindowTitle(f"Блюда для заказа #{order_id}")
        items_window.setGeometry(450, 250, 300, 200)
        layout = QVBoxLayout()
        title_label = QLabel(f"Блюда для заказа #{order_id}")
        layout.addWidget(title_label)

        if not items:
            layout.addWidget(QLabel("Нет блюд в этом заказе"))
        else:
            for item in items:
                layout.addWidget(QLabel(item[0]))

        items_window.setLayout(layout)
        items_window.show() 
        items_window.exec()

    def show_error(self, message):
        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Icon.Critical)
        error_msg.setText(message)
        error_msg.setWindowTitle("Ошибка")
        error_msg.exec()

    def show_message(self, message):
        info_msg = QMessageBox()
        info_msg.setIcon(QMessageBox.Icon.Information)
        info_msg.setText(message)
        info_msg.setWindowTitle("Успех")
        info_msg.exec()
