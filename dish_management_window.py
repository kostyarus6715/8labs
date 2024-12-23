from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QDialogButtonBox, QDialog, QFormLayout, QLineEdit
from db import add_dish, get_all_dishes, delete_dish

class DishManagementWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Управление блюдами")
        self.setGeometry(450, 250, 600, 400)

        self.layout = QVBoxLayout()

        self.add_dish_button = QPushButton("Добавить блюдо")
        self.layout.addWidget(self.add_dish_button)
        self.add_dish_button.clicked.connect(self.add_dish)

        self.delete_dish_button = QPushButton("Удалить блюдо")
        self.layout.addWidget(self.delete_dish_button)
        self.delete_dish_button.clicked.connect(self.delete_dish)

        self.dish_table = QTableWidget()
        self.dish_table.setRowCount(0) 
        self.dish_table.setColumnCount(2)
        self.dish_table.setHorizontalHeaderLabels(['Название', 'Цена'])
        self.layout.addWidget(self.dish_table)

        self.setLayout(self.layout)
        self.update_dish_table()

    def add_dish(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить блюдо")
        layout = QFormLayout()

        name_input = QLineEdit()
        price_input = QLineEdit()
        layout.addRow("Название блюда:", name_input)
        layout.addRow("Цена блюда:", price_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        dialog.setLayout(layout)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = name_input.text()
            price = price_input.text()

            if name and price:
                try:
                    price = float(price)
                    add_dish(name, price) 
                    print(f"Блюдо '{name}' добавлено!")
                    self.update_dish_table() 
                except ValueError:
                    print("Цена должна быть числом.")
            else:
                print("Пожалуйста, заполните все поля.")

    def delete_dish(self):
        dishes = get_all_dishes()

        if not dishes:
            print("Нет блюд для удаления.")
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Удалить блюдо")
        layout = QVBoxLayout()

        for dish in dishes:
            button = QPushButton(dish['name']) 
            button.clicked.connect(lambda _, dish_id=dish['id']: self.confirm_delete(dish_id))
            layout.addWidget(button)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        layout.addWidget(buttons)

        buttons.rejected.connect(dialog.reject)

        dialog.setLayout(layout)
        dialog.exec()

    def confirm_delete(self, dish_id):
        delete_dish(dish_id)
        print(f"Блюдо с ID {dish_id} удалено.")
        self.update_dish_table() 

    def update_dish_table(self):
        dishes = get_all_dishes()

        self.dish_table.setRowCount(0)

        for dish in dishes:
            row_position = self.dish_table.rowCount()
            self.dish_table.insertRow(row_position)
            self.dish_table.setItem(row_position, 0, QTableWidgetItem(dish['name']))
            self.dish_table.setItem(row_position, 1, QTableWidgetItem(str(dish['price'])))
