import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox, Listbox
from tkinter import ttk
import datetime
import os
import uuid

from database.db_handler import fetch_all_medicines, update_medicine_by_id, insert_sale_record

cart = []
selected_medicine = None

def generate_receipt_text(items, total, cash, change, invoice_id):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = []
    lines.append("        PHARMACY RECEIPT")
    lines.append("     Address: Your Shop Address")
    lines.append("*" * 40)
    lines.append("             CASH RECEIPT")
    lines.append("*" * 40)
    lines.append(f"Date: {now}")
    lines.append(f"Invoice ID: {invoice_id}")
    lines.append("")
    lines.append(f"{'Description':<25}{'Price':>10}")

    for name, qty, price in items:
        subtotal = qty * price
        lines.append(f"{name} x{qty:<21}{subtotal:>7.2f}")

    lines.append("")
    lines.append("*" * 40)
    lines.append(f"{'Total':<25}Rs. {total:>7.2f}")
    lines.append(f"{'Cash':<25}Rs. {cash:>7.2f}")
    lines.append(f"{'Change':<25}Rs. {change:>7.2f}")
    lines.append("*" * 40)
    lines.append("        THANK YOU FOR VISITING!")
    lines.append("*" * 40)
    lines.append("|| ||| || || ||||| || | || ||| |")  # Fake barcode
    return "\n".join(lines)

def open_checkout_window(on_checkout_complete=None):
    global selected_medicine
    selected_medicine = None
    cart.clear()

    window = tb.Toplevel()
    window.title("Medicine Checkout")
    window.geometry("860x640")

    tb.Label(window, text="💊 Pharmacy Checkout", font=("Segoe UI", 16, "bold")).pack(pady=10)

    # Search Section
    search_frame = tb.Labelframe(window, text="Search Medicine", padding=10)
    search_frame.pack(fill="x", padx=20, pady=5)

    inner_search_frame = tb.Frame(search_frame)
    inner_search_frame.pack(fill="x")

    tb.Label(inner_search_frame, text="Search:").pack(side="left", padx=(0, 5))
    search_entry = tb.Entry(inner_search_frame, width=30)
    search_entry.pack(side="left")

    result_box = Listbox(search_frame, height=6, font=("Segoe UI", 10))
    result_box.pack(fill="x", pady=8)

    def search():
        result_box.delete(0, "end")
        keyword = search_entry.get().lower()
        for row in fetch_all_medicines():
            name = row[1].lower()
            if keyword in name:
                result_box.insert("end", f"{row[0]} | {row[1]} | Qty: {row[5]} | Price: {row[6]}")

    tb.Button(inner_search_frame, text="Search", command=search, bootstyle="primary").pack(side="left", padx=10)

    def on_select(event):
        global selected_medicine
        try:
            selected = result_box.get(result_box.curselection())
            selected_id = int(selected.split('|')[0].strip())
            for row in fetch_all_medicines():
                if row[0] == selected_id:
                    selected_medicine = row
                    break
        except:
            pass

    result_box.bind("<<ListboxSelect>>", on_select)

    # Add to Cart Section
    qty_frame = tb.Labelframe(window, text="Add to Cart", padding=10)
    qty_frame.pack(fill="x", padx=20, pady=5)

    tb.Label(qty_frame, text="Quantity:").pack(side="left")
    qty_entry = tb.Entry(qty_frame, width=5)
    qty_entry.pack(side="left", padx=(5, 10))

    columns = ("name", "qty", "price", "subtotal")
    cart_tree = ttk.Treeview(window, columns=columns, show="headings", height=8)
    cart_tree.heading("name", text="Medicine")
    cart_tree.heading("qty", text="Qty")
    cart_tree.heading("price", text="Price")
    cart_tree.heading("subtotal", text="Subtotal")

    for col in columns:
        cart_tree.column(col, anchor="center", width=160)
    cart_tree.pack(fill="both", expand=True, padx=20, pady=(10, 0))

    total_label = tb.Label(window, text="Total: Rs. 0", font=("Segoe UI", 11, "bold"), foreground="green")
    total_label.pack(anchor="e", padx=20, pady=(5, 0))

    def update_total():
        total = sum(item["subtotal"] for item in cart)
        total_label.config(text=f"Total: Rs. {total:.2f}")

    def add_to_cart():
        if not selected_medicine:
            messagebox.showwarning("No Selection", "Please select a medicine.")
            return
        try:
            qty = int(qty_entry.get())
            if qty <= 0 or qty > selected_medicine[5]:
                raise ValueError
            subtotal = round(qty * selected_medicine[6], 2)
            tree_id = cart_tree.insert("", "end", values=(selected_medicine[1], qty, selected_medicine[6], subtotal))
            cart.append({
                "id": selected_medicine[0],
                "name": selected_medicine[1],
                "price": selected_medicine[6],
                "qty": qty,
                "subtotal": subtotal,
                "tree_id": tree_id
            })
            qty_entry.delete(0, "end")
            update_total()
        except:
            messagebox.showerror("Invalid Quantity", "Enter a valid quantity within available stock.")

    tb.Button(qty_frame, text="Add to Cart", command=add_to_cart, bootstyle="success").pack(side="left", padx=10)

    def remove_selected_cart_item():
        selected = cart_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an item to remove.")
            return

        for tree_id in selected:
            cart_tree.delete(tree_id)
            for i, item in enumerate(cart):
                if item.get("tree_id") == tree_id:
                    del cart[i]
                    break
        update_total()

    tb.Button(window, text="🗑 Remove Selected Item", command=remove_selected_cart_item,
              bootstyle="danger outline").pack(pady=(5, 0))

    def checkout():
        if not cart:
            messagebox.showerror("Empty Cart", "Add items to cart first.")
            return

        total = round(sum(item["subtotal"] for item in cart), 2)

        # Prompt for cash input
        cash_win = tb.Toplevel(window)
        cash_win.title("Cash Received")
        cash_win.geometry("300x140")
        cash_win.grab_set()

        tb.Label(cash_win, text=f"Total Amount: Rs. {total:.2f}").pack(pady=(10, 5))
        tb.Label(cash_win, text="Enter Cash Received:").pack()
        cash_entry = tb.Entry(cash_win)
        cash_entry.pack(pady=5)

        def confirm_cash():
            try:
                cash = float(cash_entry.get())
                if cash < total:
                    messagebox.showerror("Insufficient Cash", "Cash is less than total amount.")
                    return
                change = round(cash - total, 2)

                invoice_id = str(uuid.uuid4())[:8]  # Short unique invoice

                date_str = datetime.datetime.now().strftime('%Y-%m-%d')
                items_summary = []
                for item in cart:
                    items_summary.append((item['name'], item['qty'], item['price']))
                    med = next((m for m in fetch_all_medicines() if m[0] == item['id']), None)
                    if med:
                        updated_qty = med[5] - item['qty']
                        update_medicine_by_id((med[1], med[2], med[3], med[4], updated_qty, med[6], med[7]), med[0])
                    insert_sale_record((item['id'], item['name'], item['qty'], item['price'], item['subtotal'], date_str, invoice_id))

                receipt_text = generate_receipt_text(items_summary, total, cash, change, invoice_id)
                file_path = os.path.expanduser(
                    f"~/Documents/PharmacyData/receipt_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                )
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(receipt_text)

                messagebox.showinfo("Checkout Successful", f"Receipt saved to:\n{file_path}")
                cart.clear()
                cart_tree.delete(*cart_tree.get_children())
                update_total()
                if on_checkout_complete:
                    on_checkout_complete()

                cash_win.destroy()
                window.destroy()

            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid number.")

        tb.Button(cash_win, text="Confirm", command=confirm_cash, bootstyle="success").pack(pady=10)

    tb.Button(window, text="Checkout & Print Slip", bootstyle="primary", command=checkout).pack(pady=15)
