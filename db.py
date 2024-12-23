import sqlite3
def get_db_connection():
    try:
        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row 
        return conn
    except sqlite3.Error as e:
        print(f"Ошибка при подключении к базе данных: {e}")
        return None

def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Таблица для сотрудников
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            last_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            middle_name TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Работает'
        )
    """)

    # Таблица для смен
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Shifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL
        )
    """)

    # Таблица для связи сотрудников и смен
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS EmployeeShifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            shift_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employees(id),
            FOREIGN KEY (shift_id) REFERENCES Shifts(id)
        )
    """)

    # Таблица для заказов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_number INTEGER NOT NULL,
            num_clients INTEGER NOT NULL,
            status TEXT NOT NULL,
            date TEXT NOT NULL,
            total_price REAL,
            is_paid INTEGER NOT NULL
        )
    """)

    # Таблица для пунктов заказов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            item_name TEXT NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
    """)

    # Таблица для блюд
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dishes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)

    # Таблица для кассовых ордеров
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cash_receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            payment_method TEXT,
            amount REAL,
            date TEXT,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
    """)

    conn.commit()
    conn.close()

# Функция для добавления нового сотрудника
def add_employee(last_name, first_name, middle_name, username, password, role, status="Работает"):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO employees (last_name, first_name, middle_name, username, password, role, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (last_name, first_name, middle_name, username, password, role, status))
    conn.commit()
    conn.close()

# Функция для получения списка сотрудников
def get_all_employees():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
    conn.close()
    return employees

# Функция для поиска сотрудника по логину
def get_employee_by_username(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees WHERE username = ?", (username,))
    employee = cursor.fetchone()
    conn.close()
    return employee

# Функция для редактирования информации о сотруднике
def edit_employee(id, last_name, first_name, middle_name, username, password, role, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE employees
        SET last_name = ?, first_name = ?, middle_name = ?, username = ?, password = ?, role = ?, status = ?
        WHERE id = ?
    """, (last_name, first_name, middle_name, username, password, role, status, id))
    conn.commit()
    conn.close()

# Функция для удаления сотрудника
def delete_employee(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM employees WHERE id = ?", (id,))
    conn.commit()
    conn.close()

# Функция для получения всех смен
def get_shifts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Shifts")
    shifts = cursor.fetchall()
    conn.close()
    return [{"id": shift[0], "date": shift[1], "start_time": shift[2], "end_time": shift[3]} for shift in shifts]

# Функция для получения списка сотрудников для отображения
def get_employees():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, last_name, first_name FROM employees")
    employees = cursor.fetchall()
    conn.close()
    return [{"id": employee["id"], "last_name": employee["last_name"], "first_name": employee["first_name"]} for employee in employees]

# Функция для назначения сотрудника на смену
def assign_employee_to_shift(employee_id, shift_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO EmployeeShifts (employee_id, shift_id) VALUES (?, ?)", (employee_id, shift_id))
    conn.commit()
    conn.close()

# Функция для создания новой смены
def create_shift(date, start_time, end_time, selected_employees):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Shifts (date, start_time, end_time) VALUES (?, ?, ?)",
                   (date, start_time, end_time))
    shift_id = cursor.lastrowid 

    # Связываем сотрудников с этой сменой
    for employee_id in selected_employees:
        cursor.execute("INSERT INTO EmployeeShifts (shift_id, employee_id) VALUES (?, ?)",
                       (shift_id, employee_id))
    conn.commit()
    conn.close()

# Функция для редактирования смены
def edit_shift(shift_id, date, start_time, end_time, selected_employees):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Shifts SET date = ?, start_time = ?, end_time = ? WHERE id = ?",
                   (date, start_time, end_time, shift_id))

    # Обновляем список сотрудников
    cursor.execute("DELETE FROM EmployeeShifts WHERE shift_id = ?", (shift_id,))
    for employee_id in selected_employees:
        cursor.execute("INSERT INTO EmployeeShifts (shift_id, employee_id) VALUES (?, ?)",
                       (shift_id, employee_id))
    conn.commit()
    conn.close()

# Функция для получения всех смен с их сотрудниками
def get_all_shifts():
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    cursor.execute("""
        SELECT shifts.id, shifts.date, shifts.start_time, shifts.end_time, 
               COUNT(employees.id) AS employee_count, 
               GROUP_CONCAT(employees.first_name || ' ' || employees.last_name) AS employees,
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
             "employees": shift["employees"], "employee_ids": shift["employee_ids"] if shift["employee_ids"] else ""} 
            for shift in shifts]

# Функция для добавления нового блюда
def add_dish(name, price):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO dishes (name, price)
        VALUES (?, ?)
    """, (name, price))
    conn.commit()
    conn.close()

# Функция для получения всех блюд
def get_all_dishes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dishes")
    dishes = cursor.fetchall()
    conn.close()
    return dishes

# Функция для удаления блюда
def delete_dish(dish_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM dishes WHERE id = ?", (dish_id,))
    conn.commit()
    conn.close()