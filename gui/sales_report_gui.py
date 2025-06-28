import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import ttk, messagebox
from database.db_handler import fetch_sales_by_date
import datetime

def open_sales_report_window():
    report_win = tb.Toplevel()
    report_win.title("📈 Daily Sales Report")
    report_win.geometry("700x500")

    # Date input
    tb.Label(report_win, text="📆 Select Date:", font=("Segoe UI", 12)).pack(pady=(10, 0))
    date_entry = tb.Entry(report_win)
    date_entry.insert(0, datetime.datetime.now().strftime('%Y-%m-%d'))
    date_entry.pack(pady=(0, 10))

    # Table
    columns = ("name", "qty", "price", "subtotal")
    tree = ttk.Treeview(report_win, columns=columns, show="headings", height=15)

    for col in columns:
        tree.heading(col, text=col.capitalize())
        tree.column(col, anchor="center", width=120)

    tree.pack(pady=10, fill="both", expand=True)

    # Total label
    total_label = tb.Label(report_win, text="Total: Rs. 0", font=("Segoe UI", 11, "bold"))
    total_label.pack(anchor="e", padx=20)

    # Load report function
    def load_report():
        date = date_entry.get().strip()
        try:
            datetime.datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter date in YYYY-MM-DD format.")
            return

        rows = fetch_sales_by_date(date)
        tree.delete(*tree.get_children())

        total = 0
        for row in rows:
            # Assuming row = (id, name, qty, price, subtotal)
            tree.insert('', 'end', values=row[1:])
            total += row[4]

        total_label.config(text=f"Total: Rs. {total:.2f}")

    # Button to load data
    tb.Button(report_win, text="🔍 Load Report", command=load_report, bootstyle="primary").pack(pady=(0, 10))
