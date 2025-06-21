from database.db_handler import (
    insert_medicine,
    fetch_all_medicines,
    delete_medicine_by_id,
    update_medicine_by_id,
    search_medicine
)
from utils.expiry_checker import check_expiry
from tkinter import messagebox, filedialog
import csv
import threading
import time
from datetime import datetime

REFRESH_INTERVAL = 4 * 60 * 60  # 4 hours
LOW_STOCK_THRESHOLD = 10

tree_widget = None
form_entries = None

dashboard_labels = {
    'total': None,
    'expired': None,
    'near_expiry': None,
    'low_stock': None
}

sort_column = None
sort_reverse = False

current_filters = {
    'min_quantity': None,
    'max_quantity': None,
    'min_price': None,
    'max_price': None,
    'status': None,
}

tooltip_var = None


def set_dashboard_labels(lbl_total, lbl_expired, lbl_near_expiry, lbl_low_stock):
    dashboard_labels['total'] = lbl_total
    dashboard_labels['expired'] = lbl_expired
    dashboard_labels['near_expiry'] = lbl_near_expiry
    dashboard_labels['low_stock'] = lbl_low_stock


def set_tree(tree):
    global tree_widget
    tree_widget = tree
    threading.Thread(target=auto_refresh, daemon=True).start()


def set_entries(entries):
    global form_entries
    form_entries = entries


def set_sorting(column):
    global sort_column, sort_reverse
    if sort_column == column:
        sort_reverse = not sort_reverse
    else:
        sort_column = column
        sort_reverse = False
    load_data(show_popup=False)


def set_filters(min_q=None, max_q=None, min_p=None, max_p=None, status=None):
    global current_filters
    current_filters.update({
        'min_quantity': min_q,
        'max_quantity': max_q,
        'min_price': min_p,
        'max_price': max_p,
        'status': status
    })
    load_data(show_popup=False)


def apply_filters(rows):
    filtered = []
    for row in rows:
        quantity = row[5]
        price = row[6]
        status_icon, _ = check_expiry(row[4])

        if current_filters['min_quantity'] is not None and quantity < current_filters['min_quantity']:
            continue
        if current_filters['max_quantity'] is not None and quantity > current_filters['max_quantity']:
            continue
        if current_filters['min_price'] is not None and price < current_filters['min_price']:
            continue
        if current_filters['max_price'] is not None and price > current_filters['max_price']:
            continue
        if current_filters['status'] and current_filters['status'] not in status_icon:
            continue

        filtered.append(row)
    return filtered


def apply_sort(rows):
    if not sort_column:
        return rows

    col_idx_map = {
        "Name": 1,
        "Batch": 2,
        "Mfg Date": 3,
        "Expiry Date": 4,
        "Quantity": 5,
        "Price": 6,
    }
    idx = col_idx_map.get(sort_column)
    if idx is None:
        return rows

    def sort_key(row):
        val = row[idx]
        try:
            if sort_column in ["Mfg Date", "Expiry Date"]:
                return datetime.strptime(val, "%Y-%m-%d")
            elif sort_column in ["Quantity", "Price"]:
                return float(val)
            return val.lower() if isinstance(val, str) else val
        except:
            return float('-inf')

    return sorted(rows, key=sort_key, reverse=sort_reverse)


def add_medicine(entries):
    values = [e.get().strip() for e in entries]
    if not values[0] or not values[3] or not values[4]:
        messagebox.showwarning("Input Error", "Please fill required fields (Name, Expiry Date, Quantity).")
        return
    try:
        values[4] = int(values[4])
        values[5] = float(values[5]) if values[5] else 0.0
    except ValueError:
        messagebox.showerror("Input Error", "Invalid quantity or price.")
        return

    insert_medicine(values)
    messagebox.showinfo("Success", "Medicine added successfully!")
    for e in entries:
        e.delete(0, 'end')
    entries[0].focus_set()
    load_data()


def load_data(show_popup=True):
    expired, near_expiry, low_stock = [], [], []
    tree_widget.delete(*tree_widget.get_children())

    all_medicines = fetch_all_medicines()
    filtered = apply_filters(all_medicines)
    sorted_rows = apply_sort(filtered)

    for row in sorted_rows:
        med_id = row[0]
        status_icon, days_info = check_expiry(row[4])
        status = f"{status_icon} ({days_info})"
        tags = []

        if row[5] < LOW_STOCK_THRESHOLD:
            status += " 🔔 Low Stock"
            tags.append("low_stock")
            low_stock.append(row[1])
        if "❌" in status_icon:
            tags.append("expired")
            expired.append(row[1])
        elif "⚠️" in status_icon:
            tags.append("near_expiry")
            near_expiry.append(row[1])

        tree_widget.insert('', 'end', iid=str(med_id), values=row[1:] + (status,), tags=tags)

    if dashboard_labels['total']:
        dashboard_labels['total'].config(text=f"📦 Total Medicines: {len(sorted_rows)}")
    if dashboard_labels['expired']:
        dashboard_labels['expired'].config(text=f"❌ Expired: {len(expired)}")
    if dashboard_labels['near_expiry']:
        dashboard_labels['near_expiry'].config(text=f"⚠️ Near Expiry: {len(near_expiry)}")
    if dashboard_labels['low_stock']:
        dashboard_labels['low_stock'].config(text=f"🔔 Low Stock: {len(low_stock)}")

    if show_popup and (expired or near_expiry or low_stock):
        msg = ""
        if expired:
            msg += f"❌ Expired Medicines: {len(expired)}\n"
        if near_expiry:
            msg += f"⚠️ Near Expiry (within 30 days): {len(near_expiry)}\n"
        if low_stock:
            msg += f"🔔 Low Stock Medicines (<{LOW_STOCK_THRESHOLD}): {len(low_stock)}\n"
        messagebox.showwarning("Inventory Alert", msg.strip())

        if form_entries:
            form_entries[0].focus_set()


def delete_selected():
    selected = tree_widget.selection()
    if not selected:
        messagebox.showwarning("No selection", "Please select a record to delete.")
        return

    med_id = selected[0]
    values = tree_widget.item(med_id, 'values')
    name, batch = values[0], values[1]

    if messagebox.askyesno("Confirm Delete", f"Delete {name} (Batch {batch})?"):
        if delete_medicine_by_id(med_id):
            messagebox.showinfo("Deleted", f"{name} (Batch {batch}) has been deleted.")
            load_data(show_popup=False)
        else:
            messagebox.showerror("Error", "Medicine not found or could not be deleted.")


def search_medicines(query):
    query = query.strip().lower()
    if not query:
        load_data(show_popup=False)
        return

    results = search_medicine(query)
    tree_widget.delete(*tree_widget.get_children())

    if not results:
        messagebox.showinfo("Search", "No matching medicines found.")
        return

    for row in results:
        med_id = row[0]
        status_icon, days_info = check_expiry(row[4])
        status = f"{status_icon} ({days_info})"
        tags = []

        if row[5] < LOW_STOCK_THRESHOLD:
            status += " 🔔 Low Stock"
            tags.append("low_stock")
        if "❌" in status_icon:
            tags.append("expired")
        elif "⚠️" in status_icon:
            tags.append("near_expiry")

        tree_widget.insert('', 'end', iid=str(med_id), values=row[1:] + (status,), tags=tags)


def filter_status(status_filter):
    set_filters(status=status_filter)


def edit_selected(entries):
    selected = tree_widget.selection()
    if not selected:
        messagebox.showwarning("No selection", "Please select a row to update.")
        return
    values = [e.get().strip() for e in entries]
    if not values[0] or not values[3] or not values[4]:
        messagebox.showwarning("Input Error", "Please fill required fields (Name, Expiry Date, Quantity).")
        return
    try:
        values[4] = int(values[4])
        values[5] = float(values[5]) if values[5] else 0.0
    except ValueError:
        messagebox.showerror("Input Error", "Invalid quantity or price.")
        return

    med_id = selected[0]
    if update_medicine_by_id(values, med_id):
        messagebox.showinfo("Updated", f"Medicine ID {med_id} has been updated.")
        for e in entries:
            e.delete(0, 'end')
        entries[0].focus_set()
        load_data(show_popup=False)
    else:
        messagebox.showerror("Error", "Update failed. Record not found.")


def export_to_csv():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if not file_path:
        return

    data = fetch_all_medicines()
    try:
        with open(file_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Batch", "Mfg Date", "Expiry Date", "Quantity", "Price", "Status"])
            for row in data:
                status_icon, days_info = check_expiry(row[4])
                status = f"{status_icon} ({days_info})"
                if row[5] < LOW_STOCK_THRESHOLD:
                    status += " 🔔 Low Stock"
                writer.writerow(row[1:] + (status,))
        messagebox.showinfo("Success", f"Data exported to {file_path}")
    except Exception as e:
        messagebox.showerror("Export Error", str(e))


def auto_refresh():
    while True:
        time.sleep(REFRESH_INTERVAL)
        load_data(show_popup=False)


def reset_filters():
    global current_filters
    current_filters = {
        'min_quantity': None,
        'max_quantity': None,
        'min_price': None,
        'max_price': None,
        'status': None,
    }
    load_data(show_popup=False)
