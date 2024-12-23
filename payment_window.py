from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QComboBox, QMessageBox,QLabel,QLineEdit
import sqlite3

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

class PaymentWindow(QWidget):
    def __init__(self, order_id, parent=None):
        super().__init__()
        self.setWindowTitle("Оплата заказа")
        self.setGeometry(400, 200, 400, 300)
        self.order_id = order_id
        self.parent = parent

        self.layout = QVBoxLayout()

        self.amount_label = QLabel("Сумма к оплате:")
        self.layout.addWidget(self.amount_label)

        # Поле для ввода суммы
        self.amount_input = QLineEdit()
        self.amount_input.setText(str(self.get_order_total()))
        self.layout.addWidget(self.amount_input)

        self.payment_method_label = QLabel("Способ оплаты:")
        self.layout.addWidget(self.payment_method_label)

        self.payment_method_combo = QComboBox()
        self.payment_method_combo.addItems(["Наличные", "Безналичный расчет"])
        self.layout.addWidget(self.payment_method_combo)

        self.pay_button = QPushButton("Оплатить")
        self.pay_button.clicked.connect(self.process_payment)
        self.layout.addWidget(self.pay_button)

        self.setLayout(self.layout)

    def get_order_total(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT total_price FROM orders WHERE id = ?", (self.order_id,))
        total_price = cursor.fetchone()
        conn.close()
        return total_price["total_price"] if total_price else 0

    def process_payment(self):
        payment_method = self.payment_method_combo.currentText()
        amount = self.amount_input.text()

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Сумма должна быть положительным числом.")
        except ValueError as e:
            self.show_error_message(str(e))
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE orders SET is_paid = 1 WHERE id = ?", (self.order_id,))
        cursor.execute("INSERT INTO cash_receipts (order_id, payment_method, amount) VALUES (?, ?, ?)",
                       (self.order_id, payment_method, amount))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Успех", "Оплата прошла успешно. Кассовый ордер создан.")
        self.parent.load_orders()
        self.close()

    def show_error_message(self, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Ошибка")
        msg.setText(message)
        msg.exec()
