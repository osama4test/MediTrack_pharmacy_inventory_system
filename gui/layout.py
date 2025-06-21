import tkinter as tk
from tkinter import ttk
from gui import events
from gui.events import reset_filters 

def create_tooltip(widget, text):
    def on_enter(event):
        events.tooltip_var.set(text)
    def on_leave(event):
        events.tooltip_var.set("")
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

def build_gui():
    root = tk.Tk()
    root.title("Pharmacy Inventory System")
    root.geometry("980x720")

    style = ttk.Style()
    style.theme_use("clam")
    style.map("Treeview", background=[('selected', '#347083')], foreground=[('selected', 'white')])

    tooltip_label = tk.Label(root, text="", fg="gray", anchor="w")
    tooltip_label.pack(side="bottom", fill="x")
    events.tooltip_var = tk.StringVar()
    tooltip_label.config(textvariable=events.tooltip_var)

    dashboard_frame = tk.Frame(root, pady=10)
    dashboard_frame.pack(fill="x", padx=15)

    lbl_total = tk.Label(dashboard_frame, text="📦 Total Medicines: 0", font=("Arial", 12, "bold"))
    lbl_expired = tk.Label(dashboard_frame, text="❌ Expired: 0", fg="red", font=("Arial", 12, "bold"))
    lbl_near_expiry = tk.Label(dashboard_frame, text="⚠️ Near Expiry: 0", fg="orange", font=("Arial", 12, "bold"))
    lbl_low_stock = tk.Label(dashboard_frame, text="🔔 Low Stock: 0", fg="brown", font=("Arial", 12, "bold"))

    for lbl in (lbl_total, lbl_expired, lbl_near_expiry, lbl_low_stock):
        lbl.pack(side="left", padx=20)

    events.set_dashboard_labels(lbl_total, lbl_expired, lbl_near_expiry, lbl_low_stock)

    form_frame = tk.LabelFrame(root, text="Add / Edit Medicine", padx=15, pady=15)
    form_frame.pack(fill="x", padx=15, pady=10)

    labels = ["Name*", "Batch No", "Mfg Date (YYYY-MM-DD)", "Expiry Date*", "Quantity*", "Price"]
    entries = []
    for i, label in enumerate(labels):
        tk.Label(form_frame, text=label).grid(row=i // 2, column=(i % 2) * 2, sticky="e", padx=6, pady=8)
        entry = tk.Entry(form_frame, width=32)
        entry.grid(row=i // 2, column=(i % 2) * 2 + 1, padx=6, pady=8)
        entries.append(entry)

    btn_frame = tk.Frame(form_frame)
    btn_frame.grid(row=3, column=0, columnspan=4, pady=12)
    btn_add = tk.Button(btn_frame, text="Add Medicine", width=15, command=lambda: events.add_medicine(entries))
    btn_update = tk.Button(btn_frame, text="Update Selected", width=15, command=lambda: events.edit_selected(entries))
    btn_add.pack(side="left", padx=12)
    btn_update.pack(side="left", padx=12)

    create_tooltip(btn_add, "Add a new medicine to inventory")
    create_tooltip(btn_update, "Update the selected medicine record")

    filter_search_frame = tk.Frame(root)
    filter_search_frame.pack(fill="x", padx=15, pady=5)

    search_frame = tk.Frame(filter_search_frame)
    search_frame.pack(side="left", fill="x", expand=True)

    tk.Label(search_frame, text="🔍 Search by Name or Batch:", font=("Arial", 10)).pack(side="left", padx=(0, 5))
    search_entry = tk.Entry(search_frame, width=35)
    search_entry.pack(side="left")
    search_entry.insert(0, "Type to search...")

    def clear_placeholder(event):
        if search_entry.get() == "Type to search...":
            search_entry.delete(0, "end")

    def add_placeholder(event):
        if not search_entry.get():
            search_entry.insert(0, "Type to search...")

    search_entry.bind("<FocusIn>", clear_placeholder)
    search_entry.bind("<FocusOut>", add_placeholder)

    btn_search = tk.Button(search_frame, text="Search", width=8,
                           command=lambda: events.search_medicines(search_entry.get()))
    btn_reset = tk.Button(search_frame, text="Reset", width=8,
                          command=lambda: [search_entry.delete(0, 'end'), events.load_data(show_popup=False)])
    btn_search.pack(side="left", padx=(10, 5))
    btn_reset.pack(side="left")

    create_tooltip(btn_search, "Search medicines by name or batch number")
    create_tooltip(btn_reset, "Clear search and show all medicines")

    filter_frame = tk.Frame(filter_search_frame)
    filter_frame.pack(side="right")

    # ✅ Fix applied here
    btn_show_all = tk.Button(filter_frame, text="Show All", width=12,
                             command=reset_filters)
    btn_expired = tk.Button(filter_frame, text="Only Expired", width=12,
                            command=lambda: events.filter_status("❌"))
    btn_near_expiry = tk.Button(filter_frame, text="Near Expiry", width=12,
                                command=lambda: events.filter_status("⚠️"))

    for btn in (btn_show_all, btn_expired, btn_near_expiry):
        btn.pack(side="left", padx=6)

    create_tooltip(btn_show_all, "Show all medicines")
    create_tooltip(btn_expired, "Filter only expired medicines")
    create_tooltip(btn_near_expiry, "Filter medicines near expiry")

    tree_frame = tk.Frame(root)
    tree_frame.pack(fill="both", expand=True, padx=15, pady=10)

    columns = ["Name", "Batch", "Mfg Date", "Expiry Date", "Quantity", "Price", "Status"]
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

    tree.tag_configure("expired", background="#ffcccc")
    tree.tag_configure("near_expiry", background="#ffe6b3")
    tree.tag_configure("low_stock", background="#d2b48c")

    def heading_click(col):
        def handler():
            events.set_sorting(col)
            update_sort_indicators(col)
        return handler

    for col in columns:
        tree.heading(col, text=col, command=heading_click(col))
        tree.column(col, anchor="center", width=120)

    tree.pack(fill="both", expand=True)

    def update_sort_indicators(active_col):
        for col in columns:
            text = col
            if col == active_col:
                arrow = " ▼" if events.sort_reverse else " ▲"
                text += arrow
            tree.heading(col, text=text, command=heading_click(col))

    update_sort_indicators(None)

    ctrl_btn_frame = tk.Frame(tree_frame)
    ctrl_btn_frame.pack(pady=10)

    btn_delete = tk.Button(ctrl_btn_frame, text="Delete Selected", width=15, command=events.delete_selected)
    btn_export = tk.Button(ctrl_btn_frame, text="Export to CSV", width=15, command=events.export_to_csv)

    btn_delete.pack(side="left", padx=15)
    btn_export.pack(side="left", padx=15)

    create_tooltip(btn_delete, "Delete selected medicine")
    create_tooltip(btn_export, "Export current data to CSV file")

    btn_update.config(state="disabled")
    btn_delete.config(state="disabled")

    def on_tree_select(event):
        selected = tree.selection()
        if selected:
            btn_update.config(state="normal")
            btn_delete.config(state="normal")
            item = tree.item(selected[0], 'values')
            for i, val in enumerate(item[:-1]):
                entries[i].delete(0, "end")
                entries[i].insert(0, val)
        else:
            btn_update.config(state="disabled")
            btn_delete.config(state="disabled")
            for e in entries:
                e.delete(0, "end")

    tree.bind("<<TreeviewSelect>>", on_tree_select)

    events.set_tree(tree)
    events.set_entries(entries)
    events.load_data()

    root.mainloop()
