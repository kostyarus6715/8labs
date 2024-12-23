from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QComboBox, QFileDialog, QMessageBox, QLabel, QDateEdit
from PyQt6.QtCore import Qt, QDate
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.ttfonts import TTFont
from openpyxl import Workbook
import sqlite3
import os

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

class ReportsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Формирование отчетов")
        self.setGeometry(400, 200, 400, 300)

        self.layout = QVBoxLayout()

        self.start_date_label = QLabel("Дата начала смены:")
        self.layout.addWidget(self.start_date_label)
        self.start_date_input = QDateEdit(calendarPopup=True)
        self.start_date_input.setDate(QDate.currentDate())
        self.layout.addWidget(self.start_date_input)

        self.end_date_label = QLabel("Дата конца смены:")
        self.layout.addWidget(self.end_date_label)
        self.end_date_input = QDateEdit(calendarPopup=True)
        self.end_date_input.setDate(QDate.currentDate())
        self.layout.addWidget(self.end_date_input)

        self.format_label = QLabel("Выберите формат отчета:")
        self.layout.addWidget(self.format_label)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PDF", "XLSX"])
        self.layout.addWidget(self.format_combo)

        self.generate_button = QPushButton("Сформировать отчет")
        self.generate_button.clicked.connect(self.generate_report)
        self.layout.addWidget(self.generate_button)

        self.setLayout(self.layout)

    def generate_report(self):
        start_date = self.start_date_input.date().toString("yyyy-MM-dd")
        end_date = self.end_date_input.date().toString("yyyy-MM-dd")
        report_format = self.format_combo.currentText()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(""" 
            SELECT id, table_number, num_clients, total_price, date 
            FROM orders 
            WHERE is_paid = 1 AND date BETWEEN ? AND ?
        """, (start_date, end_date))
        orders = cursor.fetchall()
        conn.close()

        if not orders:
            QMessageBox.warning(self, "Ошибка", "В выбранный период нет оплаченных заказов.")
            return

        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(self, "Сохранить отчет", "", f"{report_format} Files (*.{report_format.lower()})")
        if not file_path:
            return

        if report_format == "PDF":
            self.generate_pdf(file_path, orders)
        elif report_format == "XLSX":
            self.generate_xlsx(file_path, orders)

    def generate_pdf(self, file_path, orders):
        try:
            c = canvas.Canvas(file_path, pagesize=letter)

            c.setFont("Helvetica", 12)

            c.drawString(100, 800, "Отчет об оплаченных заказах")
            c.drawString(100, 780, f"Период: {self.start_date_input.text()} - {self.end_date_input.text()}")

            y = 750
            for order in orders:
                c.drawString(100, y, f"ID: {order['id']}, Столик: {order['table_number']}, "
                                    f"Клиенты: {order['num_clients']}, Сумма: {order['total_price']}, Дата: {order['date']}")
                y -= 20
                if y < 50:
                    c.showPage()
                    y = 800

            c.save()
            QMessageBox.information(self, "Успех", f"PDF отчет успешно сохранен: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать PDF отчет: {e}")

    def generate_xlsx(self, file_path, orders):
        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "Отчет о заказах"
            ws.append(["ID", "Столик", "Количество клиентов", "Сумма", "Дата"])

            for order in orders:
                ws.append([order["id"], order["table_number"], order["num_clients"], order["total_price"], order["date"]])

            wb.save(file_path)
            QMessageBox.information(self, "Успех", f"XLSX отчет успешно сохранен: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать XLSX отчет: {e}")
