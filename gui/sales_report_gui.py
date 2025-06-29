import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database.db_handler import fetch_sales_by_date_range, fetch_returns_by_invoice
import datetime
import csv

# Reference to track if the report window is already open
report_window_ref = None

def open_sales_report_window():
    global report_window_ref
    if report_window_ref and report_window_ref.winfo_exists():
        messagebox.showinfo("Window Already Open", "Sales report window is already open.")
        return

    report_win = tb.Toplevel()
    report_win.title("📈 Sales Report by Date Range")
    report_win.geometry("880x600")
    report_window_ref = report_win

    def on_close():
        global report_window_ref
        if report_window_ref:
            report_window_ref.destroy()
            report_window_ref = None

    report_win.protocol("WM_DELETE_WINDOW", on_close)

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
    columns = ("invoice_id", "name", "qty", "price", "subtotal", "returned")
    tree = ttk.Treeview(report_win, columns=columns, show="headings", height=15)

    for col in columns:
        tree.heading(col, text=col.replace("_", " ").capitalize())
        tree.column(col, anchor="center", width=130)

    tree.pack(pady=10, fill="both", expand=True)

    # Total labels
    totals_frame = tb.Frame(report_win)
    totals_frame.pack(anchor="e", padx=20, pady=(5, 0))

    total_label = tb.Label(totals_frame, text="Total Sales: Rs. 0.00", font=("Segoe UI", 11, "bold"))
    total_label.pack(anchor="e")

    returned_label = tb.Label(totals_frame, text="Total Returned: Rs. 0.00", font=("Segoe UI", 11, "bold"), foreground="red")
    returned_label.pack(anchor="e")

    net_label = tb.Label(totals_frame, text="Net Revenue: Rs. 0.00", font=("Segoe UI", 12, "bold"), foreground="green")
    net_label.pack(anchor="e")

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

        total_sales = 0
        total_returns = 0

        for row in rows:
            # row = (id, medicine_id, name, quantity, price, subtotal, date, invoice_id)
            invoice_id = row[7]
            name = row[2]
            qty = row[3]
            price = row[4]
            subtotal = row[5]

            # Fetch total returns for this medicine and invoice
            returned_qty = 0
            returned_amount = 0
            returns = fetch_returns_by_invoice(invoice_id)
            for r in returns:
                if r[1] == row[1]:  # r[1] = medicine_id
                    returned_qty += r[3]
                    returned_amount += r[5]

            total_sales += subtotal
            total_returns += returned_amount

            tree.insert('', 'end', values=(invoice_id, name, qty, price, subtotal, f"{returned_amount:.2f}"))

        net = total_sales - total_returns

        total_label.config(text=f"Total Sales: Rs. {total_sales:.2f}")
        returned_label.config(text=f"Total Returned: Rs. {total_returns:.2f}")
        net_label.config(text=f"Net Revenue: Rs. {net:.2f}")

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
