import sqlite3
import os

def get_connection():
    # ✅ Store DB in Documents/PharmacyData folder
    folder_path = os.path.expanduser("~/Documents/PharmacyData")
    os.makedirs(folder_path, exist_ok=True)
    db_path = os.path.join(folder_path, "pharmacy.db")
    return sqlite3.connect(db_path)


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
    conn.commit()
    conn.close()


def insert_medicine(data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO medicines (name, batch_no, mfg_date, expiry_date, quantity, price)
        VALUES (?, ?, ?, ?, ?, ?)
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


# ✅ Recommended: Safe Delete using ID
def delete_medicine_by_id(med_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM medicines WHERE id = ?", (med_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


# ✅ Recommended: Safe Update using ID
def update_medicine_by_id(data, med_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE medicines
        SET name = ?, batch_no = ?, mfg_date = ?, expiry_date = ?, quantity = ?, price = ?
        WHERE id = ?
    ''', (*data, med_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


# 🔎 Search using partial match on name or batch
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


# 🧯 Old Delete (not recommended anymore if multiple rows have same name+batch)
def delete_medicine(name, batch):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM medicines WHERE name = ? AND batch_no = ?", (name, batch))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


# 🧯 Old Update (not recommended anymore)
def update_medicine(data, old_name, old_batch):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE medicines
        SET name = ?, batch_no = ?, mfg_date = ?, expiry_date = ?, quantity = ?, price = ?
        WHERE name = ? AND batch_no = ?
    ''', (*data, old_name, old_batch))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0
