import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox, ttk
import datetime
from database.db_handler import (
    fetch_sales_by_date_range,
    fetch_sales_by_invoice,
    fetch_all_medicines,
    update_medicine_by_id
)

def open_return_window():
    win = tb.Toplevel()
    win.title("↩️ Return Medicine")
    win.geometry("900x600")

    tb.Label(win, text="↩️ Return Sold Medicine", font=("Segoe UI", 16, "bold")).pack(pady=10)

    # Date + Invoice Inputs
    top_frame = tb.Frame(win)
    top_frame.pack(pady=5)

    # Date input
    tb.Label(top_frame, text="📅 Date (YYYY-MM-DD):").pack(side="left", padx=(0, 5))
    date_entry = tb.Entry(top_frame, width=12)
    date_entry.insert(0, datetime.datetime.now().strftime('%Y-%m-%d'))
    date_entry.pack(side="left")

    tb.Button(top_frame, text="🔍 Load by Date", command=lambda: load_sales_by_date(), bootstyle="primary").pack(side="left", padx=10)

    # Invoice input
    tb.Label(top_frame, text="🧾 Invoice ID:").pack(side="left", padx=(20, 5))
    invoice_entry = tb.Entry(top_frame, width=15)
    invoice_entry.pack(side="left")
    tb.Button(top_frame, text="🔍 Search Invoice", command=lambda: load_sales_by_invoice_id(), bootstyle="info").pack(side="left", padx=10)

    # Sales Tree
    columns = ("med_id", "name", "qty", "price", "subtotal", "invoice_id")
    sales_tree = ttk.Treeview(win, columns=columns, show="headings", height=18)

    for col in columns:
        sales_tree.heading(col, text=col.replace("_", " ").capitalize())
        sales_tree.column(col, anchor="center", width=130)
    sales_tree.pack(padx=10, pady=10, fill="both", expand=True)

    def load_sales_by_date():
        date_str = date_entry.get().strip()
        try:
            datetime.datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Invalid Date", "Enter date in YYYY-MM-DD format.")
            return

        rows = fetch_sales_by_date_range(date_str, date_str)
        sales_tree.delete(*sales_tree.get_children())
        for row in rows:
            # (id, medicine_id, name, quantity, price, subtotal, date, invoice_id)
            sales_tree.insert('', 'end', values=(row[1], row[2], row[3], row[4], row[5], row[7]))

    def load_sales_by_invoice_id():
        invoice_id = invoice_entry.get().strip()
        if not invoice_id:
            messagebox.showwarning("Input Required", "Please enter an invoice ID.")
            return

        rows = fetch_sales_by_invoice(invoice_id)
        sales_tree.delete(*sales_tree.get_children())
        if not rows:
            messagebox.showinfo("No Results", f"No records found for Invoice ID: {invoice_id}")
            return

        for row in rows:
            sales_tree.insert('', 'end', values=(row[1], row[2], row[3], row[4], row[5], row[7]))

    def return_selected():
        selected = sales_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a sale to return.")
            return

        for item_id in selected:
            values = sales_tree.item(item_id)['values']
            med_id, name, qty, price, subtotal, invoice_id = values
            qty = int(qty)
            subtotal = float(subtotal)

            medicines = fetch_all_medicines()
            med = next((m for m in medicines if m[0] == med_id), None)
            if med:
                updated_qty = med[5] + qty
                updated_data = (med[1], med[2], med[3], med[4], updated_qty, med[6], med[7])
                update_medicine_by_id(updated_data, med_id)
                messagebox.showinfo(
                    "Refunded",
                    f"Medicine '{name}' (Invoice: {invoice_id}) returned.\nQty restored to: {updated_qty}\nRefund: Rs. {subtotal:.2f}"
                )
                # Refresh
                if invoice_entry.get().strip():
                    load_sales_by_invoice_id()
                else:
                    load_sales_by_date()

    tb.Button(win, text="↩️ Return Selected", command=return_selected, bootstyle="danger").pack(pady=10)


# For standalone testing
if __name__ == '__main__':
    app = tb.Window(themename="flatly")
    tb.Button(app, text="Open Return UI", command=open_return_window).pack(pady=50)
    app.mainloop()
