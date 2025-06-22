import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox, Listbox
from tkinter import ttk
import datetime
import os

from database.db_handler import fetch_all_medicines, update_medicine_by_id

cart = []
selected_medicine = None

def open_checkout_window(on_checkout_complete=None):  # ✅ Added optional callback
    global selected_medicine
    selected_medicine = None
    cart.clear()

    print("Checkout window opened")

    window = tb.Toplevel()
    window.title("Medicine Checkout")
    window.geometry("860x640")

    tb.Label(window, text="💊 Pharmacy Checkout", font=("Segoe UI", 16, "bold")).pack(pady=10)

    # ---------------- Search Section ----------------
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

    # ---------------- Add to Cart Section ----------------
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
        total_label.config(text=f"Total: Rs. {total}")

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

    # ---------------- Remove from Cart ----------------
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

    # ---------------- Checkout Button ----------------
    def checkout():
        if not cart:
            messagebox.showerror("Empty Cart", "Add items to cart first.")
            return

        total = sum(item["subtotal"] for item in cart)
        receipt_lines = ["Receipt - Pharmacy", f"Date: {datetime.datetime.now()}\n"]

        for item in cart:
            receipt_lines.append(f"{item['name']} x{item['qty']} @ Rs.{item['price']} = Rs.{item['subtotal']}")
            med = next((m for m in fetch_all_medicines() if m[0] == item['id']), None)
            if med:
                updated_qty = med[5] - item['qty']
                update_medicine_by_id((med[1], med[2], med[3], med[4], updated_qty, med[6], med[7]), med[0])

        receipt_lines.append(f"\nTotal Amount: Rs. {total}")
        receipt_lines.append("\nThank you for your purchase!")

        file_path = os.path.expanduser(
            f"~/Documents/PharmacyData/receipt_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write("\n".join(receipt_lines))

        messagebox.showinfo("Checkout Successful", f"Receipt generated:\n{file_path}")
        cart.clear()
        selected_medicine = None

        # ✅ Refresh result_box with current DB data
        current_keyword = search_entry.get().lower()
        result_box.delete(0, "end")
        for row in fetch_all_medicines():
            name = row[1].lower()
            if current_keyword in name:
                result_box.insert("end", f"{row[0]} | {row[1]} | Qty: {row[5]} | Price: {row[6]}")

        # ✅ Trigger layout refresh if provided
        if on_checkout_complete:
            on_checkout_complete()

        window.destroy()

    tb.Button(window, text="Checkout & Print Slip", bootstyle="primary", command=checkout).pack(pady=15)