import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database.db_handler import fetch_sales_by_date_range
import datetime
import csv

def open_sales_report_window():
    report_win = tb.Toplevel()
    report_win.title("📈 Sales Report by Date Range")
    report_win.geometry("800x570")

    # Date range input
    input_frame = tb.Frame(report_win)
    input_frame.pack(pady=(10, 0))

    tb.Label(input_frame, text="📅 From:", font=("Segoe UI", 11)).pack(side="left", padx=5)
    from_date_entry = tb.Entry(input_frame, width=12)
    from_date_entry.insert(0, datetime.datetime.now().strftime('%Y-%m-%d'))
    from_date_entry.pack(side="left")

    tb.Label(input_frame, text="📅 To:", font=("Segoe UI", 11)).pack(side="left", padx=5)
    to_date_entry = tb.Entry(input_frame, width=12)
    to_date_entry.insert(0, datetime.datetime.now().strftime('%Y-%m-%d'))
    to_date_entry.pack(side="left")

    # Table with invoice ID
    columns = ("invoice_id", "name", "qty", "price", "subtotal")
    tree = ttk.Treeview(report_win, columns=columns, show="headings", height=15)

    for col in columns:
        tree.heading(col, text=col.replace("_", " ").capitalize())
        tree.column(col, anchor="center", width=130)

    tree.pack(pady=10, fill="both", expand=True)

    # Total label
    total_label = tb.Label(report_win, text="Total: Rs. 0", font=("Segoe UI", 11, "bold"))
    total_label.pack(anchor="e", padx=20)

    # Load report function
    def load_report():
        from_date = from_date_entry.get().strip()
        to_date = to_date_entry.get().strip()

        try:
            datetime.datetime.strptime(from_date, '%Y-%m-%d')
            datetime.datetime.strptime(to_date, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter dates in YYYY-MM-DD format.")
            return

        rows = fetch_sales_by_date_range(from_date, to_date)
        tree.delete(*tree.get_children())

        total = 0
        for row in rows:
            # row = (id, medicine_id, name, quantity, price, subtotal, date, invoice_id)
            name = row[2]
            qty = row[3]
            price = row[4]
            subtotal = row[5]
            invoice_id = row[7]
            tree.insert('', 'end', values=(invoice_id, name, qty, price, subtotal))
            total += subtotal

        total_label.config(text=f"Total: Rs. {total:.2f}")

    # Export to CSV function
    def export_to_csv():
        if not tree.get_children():
            messagebox.showwarning("No Data", "Please load the report first before exporting.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save Report As"
        )
        if not file_path:
            return

        with open(file_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([col.replace("_", " ").capitalize() for col in columns])
            for child in tree.get_children():
                writer.writerow(tree.item(child)['values'])

        messagebox.showinfo("Exported", f"Report exported successfully to:\n{file_path}")

    # Buttons frame
    btn_frame = tb.Frame(report_win)
    btn_frame.pack(pady=10)

    tb.Button(btn_frame, text="🔍 Load Report", command=load_report, bootstyle="primary").pack(side="left", padx=5)
    tb.Button(btn_frame, text="📁 Export to CSV", command=export_to_csv, bootstyle="success").pack(side="left", padx=5)
