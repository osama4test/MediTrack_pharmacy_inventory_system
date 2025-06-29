import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox, ttk
import datetime

from database.db_handler import (
    fetch_sales_with_remaining_qty,
    fetch_sales_by_invoice,
    fetch_all_medicines,
    update_medicine_by_id,
    insert_return_record,
    fetch_returns_by_invoice
)

# Reference to track if window is already open
return_window_ref = None

def open_return_window(on_return_complete=None):
    global return_window_ref
    if return_window_ref and return_window_ref.winfo_exists():
        return_window_ref.deiconify()
        return_window_ref.lift()
        return_window_ref.focus_force()
        return

    win = tb.Toplevel()
    win.title("↩️ Return Medicine")
    win.geometry("950x650")
    return_window_ref = win

    def on_close():
        global return_window_ref
        if return_window_ref:
            return_window_ref.destroy()
            return_window_ref = None

    win.protocol("WM_DELETE_WINDOW", on_close)

    tb.Label(win, text="↩️ Return Sold Medicine", font=("Segoe UI", 16, "bold")).pack(pady=10)

    # Date + Invoice Inputs
    top_frame = tb.Frame(win)
    top_frame.pack(pady=5)

    tb.Label(top_frame, text="📅 Date (YYYY-MM-DD):").pack(side="left", padx=(0, 5))
    date_entry = tb.Entry(top_frame, width=12)
    date_entry.insert(0, datetime.datetime.now().strftime('%Y-%m-%d'))
    date_entry.pack(side="left")

    tb.Button(top_frame, text="🔍 Load by Date", command=lambda: load_sales_by_date(), bootstyle="primary").pack(side="left", padx=10)

    tb.Label(top_frame, text="🧾 Invoice ID:").pack(side="left", padx=(20, 5))
    invoice_entry = tb.Entry(top_frame, width=15)
    invoice_entry.pack(side="left")
    tb.Button(top_frame, text="🔍 Search Invoice", command=lambda: load_sales_by_invoice_id(), bootstyle="info").pack(side="left", padx=10)

    # Sales Tree
    columns = ("med_id", "name", "qty", "price", "subtotal", "invoice_id")
    sales_tree = ttk.Treeview(win, columns=columns, show="headings", height=16)

    for col in columns:
        sales_tree.heading(col, text=col.replace("_", " ").capitalize())
        sales_tree.column(col, anchor="center", width=130)
    sales_tree.pack(padx=10, pady=10, fill="both", expand=True)

    # Quantity selector
    qty_frame = tb.Frame(win)
    qty_frame.pack(pady=(10, 0))

    tb.Label(qty_frame, text="Enter Return Quantity:").pack(side="left", padx=(0, 5))
    return_qty_spinbox = tb.Spinbox(qty_frame, from_=1, to=1000, width=10)
    return_qty_spinbox.pack(side="left")

    def load_sales_by_date():
        date_str = date_entry.get().strip()
        try:
            datetime.datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Invalid Date", "Enter date in YYYY-MM-DD format.")
            return

        rows = fetch_sales_with_remaining_qty(date_str, date_str)
        sales_tree.delete(*sales_tree.get_children())

        for row in rows:
            try:
                med_id, name = row[0], row[1]
                qty_sold = int(row[2])
                qty_returned = int(row[3])
                price = float(row[4])
                invoice_id = row[5]

                net_qty = qty_sold - qty_returned
                if net_qty > 0:
                    subtotal = round(price * net_qty, 2)
                    sales_tree.insert('', 'end', values=(med_id, name, net_qty, price, subtotal, invoice_id))
            except Exception as e:
                print(f"Skipping row due to error: {e}")

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
            try:
                med_id, name = row[1], row[2]
                qty = int(row[3])
                price = float(row[4])
                invoice_id = row[7]
                previous_returns = fetch_returns_by_invoice(invoice_id)
                total_returned = sum(r[3] for r in previous_returns if r[1] == med_id and r[7] == invoice_id)
                net_qty = qty - total_returned
                if net_qty > 0:
                    new_subtotal = round(price * net_qty, 2)
                    sales_tree.insert('', 'end', values=(med_id, name, net_qty, price, new_subtotal, invoice_id))
            except Exception as e:
                print(f"Skipping row due to error: {e}")

    def return_selected():
        selected = sales_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a sale to return.")
            return

        return_qty_input = return_qty_spinbox.get().strip()
        if not return_qty_input.isdigit() or int(return_qty_input) <= 0:
            messagebox.showerror("Invalid Quantity", "Return quantity must be a positive number.")
            return

        return_qty = int(return_qty_input)

        for item_id in selected:
            values = sales_tree.item(item_id)['values']
            med_id, name, sold_qty, price, subtotal, invoice_id = values
            sold_qty = int(sold_qty)
            price = float(price)

            remaining_returnable = sold_qty  # FIX: already net qty in the tree

            if remaining_returnable <= 0:
                messagebox.showwarning(
                    "Already Returned",
                    f"All quantity of '{name}' (Invoice: {invoice_id}) has already been returned."
                )
                continue

            if return_qty > remaining_returnable:
                messagebox.showerror(
                    "Return Quantity Too High",
                    f"Only {remaining_returnable} can be returned for '{name}'."
                )
                continue

            medicines = fetch_all_medicines()
            med = next((m for m in medicines if m[0] == med_id), None)
            if not med:
                messagebox.showerror("Medicine Not Found", f"Medicine ID {med_id} not found in inventory.")
                continue

            updated_qty = med[5] + return_qty
            updated_data = (med[1], med[2], med[3], med[4], updated_qty, med[6], med[7])
            update_medicine_by_id(updated_data, med_id)

            refund_amount = price * return_qty
            return_entry = (
                med_id, name, return_qty, price, refund_amount,
                datetime.datetime.now().strftime('%Y-%m-%d'), invoice_id
            )
            insert_return_record(return_entry)

            messagebox.showinfo(
                "Refunded",
                f"Medicine '{name}' returned: {return_qty} units\nRefund: Rs. {refund_amount:.2f}"
            )

            new_remaining = remaining_returnable - return_qty
            if new_remaining <= 0:
                sales_tree.delete(item_id)
            else:
                new_values = list(values)
                new_values[2] = new_remaining
                new_values[4] = round(price * new_remaining, 2)
                sales_tree.item(item_id, values=new_values)

            if on_return_complete:
                on_return_complete()

    tb.Button(win, text="↩️ Return Selected", command=return_selected, bootstyle="danger").pack(pady=10)

# For standalone testing
if __name__ == '__main__':
    app = tb.Window(themename="flatly")
    tb.Button(app, text="Open Return UI", command=open_return_window).pack(pady=50)
    app.mainloop()
