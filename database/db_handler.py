import sqlite3
import os

def get_connection():
    folder_path = os.path.expanduser("~/Documents/PharmacyData")
    os.makedirs(folder_path, exist_ok=True)
    db_path = os.path.join(folder_path, "pharmacy.db")
    return sqlite3.connect(db_path)

def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    # Create medicines table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            batch_no TEXT,
            mfg_date TEXT,
            expiry_date TEXT,
            quantity INTEGER,
            price REAL
        )
    ''')

    # Add 'demand' column if not present
    cursor.execute("PRAGMA table_info(medicines)")
    columns = [col[1] for col in cursor.fetchall()]
    if "demand" not in columns:
        cursor.execute("ALTER TABLE medicines ADD COLUMN demand TEXT")

    # Create sales table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicine_id INTEGER,
            name TEXT,
            quantity INTEGER,
            price REAL,
            subtotal REAL,
            date TEXT
        )
    ''')

    # Add 'invoice_id' column if not present
    cursor.execute("PRAGMA table_info(sales)")
    sales_columns = [col[1] for col in cursor.fetchall()]
    if "invoice_id" not in sales_columns:
        cursor.execute("ALTER TABLE sales ADD COLUMN invoice_id TEXT")

    # Create returns table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS returns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicine_id INTEGER,
            name TEXT,
            quantity INTEGER,
            price REAL,
            refund_amount REAL,
            date TEXT
        )
    ''')

    conn.commit()
    conn.close()

# ---------------- Medicines Table Operations ---------------- #

def insert_medicine(data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO medicines (name, batch_no, mfg_date, expiry_date, quantity, price, demand)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', data)
    conn.commit()
    conn.close()

def fetch_all_medicines():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medicines")
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_medicine_by_id(med_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM medicines WHERE id = ?", (med_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def update_medicine_by_id(data, med_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE medicines
        SET name = ?, batch_no = ?, mfg_date = ?, expiry_date = ?, quantity = ?, price = ?, demand = ?
        WHERE id = ?
    ''', (*data, med_id))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def search_medicine(query):
    conn = get_connection()
    cursor = conn.cursor()
    wildcard = f"%{query}%"
    cursor.execute('''
        SELECT * FROM medicines
        WHERE LOWER(name) LIKE ? OR LOWER(batch_no) LIKE ?
    ''', (wildcard, wildcard))
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_medicine(name, batch):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM medicines WHERE name = ? AND batch_no = ?", (name, batch))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def update_medicine(data, old_name, old_batch):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE medicines
        SET name = ?, batch_no = ?, mfg_date = ?, expiry_date = ?, quantity = ?, price = ?, demand = ?
        WHERE name = ? AND batch_no = ?
    ''', (*data, old_name, old_batch))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0

# ---------------- Sales Table Operations ---------------- #

def insert_sale_record(sale):
    """
    sale = (medicine_id, name, quantity, price, subtotal, date, invoice_id)
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sales (medicine_id, name, quantity, price, subtotal, date, invoice_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', sale)
    conn.commit()
    conn.close()

def fetch_sales_by_date(date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sales WHERE date = ?", (date,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_sales_by_date_range(start_date, end_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sales WHERE date BETWEEN ? AND ?", (start_date, end_date))
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_sales_by_invoice(invoice_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sales WHERE invoice_id = ?", (invoice_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# ---------------- Return Table Operations ---------------- #

def insert_return_record(return_entry):
    """
    return_entry = (medicine_id, name, quantity, price, refund_amount, date)
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO returns (medicine_id, name, quantity, price, refund_amount, date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', return_entry)
    conn.commit()
    conn.close()
