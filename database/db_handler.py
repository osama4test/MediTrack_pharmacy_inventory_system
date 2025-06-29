import sqlite3
import os
import shutil
import datetime

# ---------------- Database Connection ---------------- #

def get_connection():
    folder_path = os.path.expanduser("~/Documents/PharmacyData")
    os.makedirs(folder_path, exist_ok=True)
    db_path = os.path.join(folder_path, "pharmacy.db")
    return sqlite3.connect(db_path)

# ---------------- Table Creation ---------------- #

def create_table():
    conn = get_connection()
    cursor = conn.cursor()

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

    cursor.execute("PRAGMA table_info(medicines)")
    medicine_columns = [col[1] for col in cursor.fetchall()]
    if "demand" not in medicine_columns:
        cursor.execute("ALTER TABLE medicines ADD COLUMN demand TEXT")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicine_id INTEGER,
            name TEXT,
            quantity INTEGER,
            price REAL,
            subtotal REAL,
            date TEXT,
            invoice_id TEXT
        )
    ''')

    cursor.execute("PRAGMA table_info(sales)")
    sales_columns = [col[1] for col in cursor.fetchall()]
    if "invoice_id" not in sales_columns:
        cursor.execute("ALTER TABLE sales ADD COLUMN invoice_id TEXT")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS returns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicine_id INTEGER,
            name TEXT,
            quantity INTEGER,
            price REAL,
            refund_amount REAL,
            date TEXT,
            invoice_id TEXT
        )
    ''')

    cursor.execute("PRAGMA table_info(returns)")
    return_columns = [col[1] for col in cursor.fetchall()]
    if "invoice_id" not in return_columns:
        cursor.execute("ALTER TABLE returns ADD COLUMN invoice_id TEXT")

    conn.commit()
    conn.close()

# ---------------- Medicines Operations ---------------- #

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
    wildcard = f"%{query.lower()}%"
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

# ---------------- Sales Operations ---------------- #

def insert_sale_record(sale):
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

# ---------------- Return Operations ---------------- #

def insert_return_record(return_entry):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO returns (medicine_id, name, quantity, price, refund_amount, date, invoice_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', return_entry)
    conn.commit()
    conn.close()

def fetch_returns_by_invoice(invoice_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM returns WHERE invoice_id = ?", (invoice_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_total_returned_by_invoice_and_medicine(invoice_id, medicine_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT SUM(quantity) FROM returns
        WHERE invoice_id = ? AND medicine_id = ?
    ''', (invoice_id, medicine_id))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result and result[0] is not None else 0

# ---------------- Reports ---------------- #

def fetch_sales_report_with_returns(start_date, end_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT
            s.invoice_id,
            s.medicine_id,
            s.name,
            s.quantity AS qty_sold,
            COALESCE(SUM(r.quantity), 0) AS qty_returned,
            s.price,
            s.subtotal,
            s.date
        FROM sales s
        LEFT JOIN returns r ON s.medicine_id = r.medicine_id AND s.invoice_id = r.invoice_id
        WHERE s.date BETWEEN ? AND ?
        GROUP BY s.id
        ORDER BY s.date DESC
    ''', (start_date, end_date))

    rows = cursor.fetchall()
    conn.close()

    report_data = []
    for row in rows:
        invoice_id, med_id, name, qty_sold, qty_returned, price, subtotal, date = row
        net_qty = qty_sold - qty_returned
        net_total = net_qty * price
        returned_total = qty_returned * price

        report_data.append({
            "invoice_id": invoice_id,
            "medicine_id": med_id,
            "name": name,
            "qty_sold": qty_sold,
            "qty_returned": qty_returned,
            "net_qty": net_qty,
            "price": price,
            "subtotal": subtotal,
            "returned_amount": returned_total,
            "net_total": net_total,
            "date": date
        })

    return report_data

def fetch_sales_with_remaining_qty(start_date, end_date=None, invoice_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    base_query = '''
        SELECT 
            s.medicine_id,
            s.name,
            s.quantity AS qty_sold,
            COALESCE(SUM(r.quantity), 0) AS qty_returned,
            s.price,
            s.invoice_id
        FROM sales s
        LEFT JOIN returns r ON s.invoice_id = r.invoice_id AND s.medicine_id = r.medicine_id
    '''

    filters = []
    params = []

    if invoice_id:
        filters.append("s.invoice_id = ?")
        params.append(invoice_id)
    elif start_date:
        filters.append("s.date BETWEEN ? AND ?")
        params += [start_date, end_date or start_date]

    if filters:
        base_query += " WHERE " + " AND ".join(filters)

    base_query += " GROUP BY s.id HAVING qty_sold > qty_returned ORDER BY s.date DESC"

    cursor.execute(base_query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows

# ---------------- Automatic Backup ---------------- #

def backup_database():
    try:
        original_path = os.path.expanduser("~/Documents/PharmacyData/pharmacy.db")
        backup_folder = os.path.expanduser("~/Documents/PharmacyData/Backups")
        os.makedirs(backup_folder, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"pharmacy_backup_{timestamp}.db"
        backup_path = os.path.join(backup_folder, backup_filename)

        shutil.copy2(original_path, backup_path)
        return backup_path
    except Exception as e:
        print(f"Backup failed: {e}")
        return None

def auto_backup_once_per_day():
    backup_folder = os.path.expanduser("~/Documents/PharmacyData/Backups")
    os.makedirs(backup_folder, exist_ok=True)

    today_str = datetime.datetime.now().strftime("%Y%m%d")
    existing_backups = [f for f in os.listdir(backup_folder) if f.startswith("pharmacy_backup_") and today_str in f]

    if not existing_backups:
        backup_path = backup_database()
        print(f"✅ Daily backup created: {backup_path}")
    else:
        print("✅ Backup already created for today.")

# ---------------- Trigger Auto Backup on Load ---------------- #
auto_backup_once_per_day()
