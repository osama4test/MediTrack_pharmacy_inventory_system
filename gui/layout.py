import ttkbootstrap as tb
from ttkbootstrap.constants import *
from gui import events
from gui.events import reset_filters
from gui.checkout_gui import open_checkout_window
from gui.sales_report_gui import open_sales_report_window  # ✅ Added

def create_tooltip(widget, text):
    def on_enter(event):
        events.tooltip_var.set(text)
    def on_leave(event):
        events.tooltip_var.set("")
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

def build_gui():
    root = tb.Window(themename="flatly")
    root.title("Pharmacy Inventory System")
    root.state('zoomed')

    # Tooltip label at the bottom
    events.tooltip_var = tb.StringVar()
    tooltip_label = tb.Label(root, textvariable=events.tooltip_var, bootstyle="secondary")
    tooltip_label.pack(side="bottom", fill="x")

    # Dashboard
    dashboard_frame = tb.Frame(root, padding=10)
    dashboard_frame.pack(fill="x", padx=15)

    lbl_total = tb.Label(dashboard_frame, text="📦 Total Medicines: 0", font=("Segoe UI", 12, "bold"))
    lbl_expired = tb.Label(dashboard_frame, text="❌ Expired: 0", font=("Segoe UI", 12, "bold"), foreground="red")
    lbl_near_expiry = tb.Label(dashboard_frame, text="⚠️ Near Expiry: 0", font=("Segoe UI", 12, "bold"), foreground="orange")
    lbl_low_stock = tb.Label(dashboard_frame, text="🔔 Low Stock: 0", font=("Segoe UI", 12, "bold"), foreground="brown")

    for lbl in (lbl_total, lbl_expired, lbl_near_expiry, lbl_low_stock):
        lbl.pack(side="left", padx=25)

    events.set_dashboard_labels(lbl_total, lbl_expired, lbl_near_expiry, lbl_low_stock)

    # Form section
    form_frame = tb.Labelframe(root, text="Add / Edit Medicine", padding=20)
    form_frame.pack(fill="x", padx=15, pady=10)

    labels = ["Name*", "Batch No", "Mfg Date (YYYY-MM-DD)", "Expiry Date*", "Quantity*", "Price", "Demand"]
    entries = []
    for i, label in enumerate(labels):
        tb.Label(form_frame, text=label).grid(row=i // 2, column=(i % 2) * 2, sticky="e", padx=8, pady=10)
        entry = tb.Entry(form_frame, width=30, bootstyle="light")
        entry.grid(row=i // 2, column=(i % 2) * 2 + 1, padx=8, pady=10)
        entries.append(entry)

    # Buttons
    btn_frame = tb.Frame(form_frame)
    btn_frame.grid(row=4, column=0, columnspan=4, pady=15)
    btn_add = tb.Button(btn_frame, text="Add Medicine", bootstyle="success", width=16,
                        command=lambda: events.add_medicine(entries))
    btn_update = tb.Button(btn_frame, text="Update Selected", bootstyle="info", width=16,
                           command=lambda: events.edit_selected(entries))
    btn_add.pack(side="left", padx=15)
    btn_update.pack(side="left", padx=15)

    create_tooltip(btn_add, "Add a new medicine to inventory")
    create_tooltip(btn_update, "Update the selected medicine record")

    # Search and filter toolbar
    toolbar = tb.Frame(root)
    toolbar.pack(fill="x", padx=15, pady=5)

    search_frame = tb.Frame(toolbar)
    search_frame.pack(side="left", fill="x", expand=True)

    tb.Label(search_frame, text="🔍 Search by Name or Batch:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
    search_entry = tb.Entry(search_frame, width=35)
    search_entry.insert(0, "Type to search...")
    search_entry.pack(side="left")

    def clear_placeholder(event):
        if search_entry.get() == "Type to search...":
            search_entry.delete(0, "end")

    def add_placeholder(event):
        if not search_entry.get():
            search_entry.insert(0, "Type to search...")

    search_entry.bind("<FocusIn>", clear_placeholder)
    search_entry.bind("<FocusOut>", add_placeholder)

    tb.Button(search_frame, text="Search", width=8,
              command=lambda: events.search_medicines(search_entry.get()), bootstyle="primary").pack(side="left", padx=5)
    tb.Button(search_frame, text="Reset", width=8,
              command=lambda: [search_entry.delete(0, 'end'), events.load_data(show_popup=False)],
              bootstyle="secondary").pack(side="left")

    # 💳 Checkout Button
    tb.Button(root, text="💳 Checkout", bootstyle="primary outline", width=20,
              command=open_checkout_window).pack(pady=(0, 5))

    # 📅 Sales Report Button (new)
    tb.Button(root, text="📅 View Sales Report", bootstyle="info outline", width=20,
              command=open_sales_report_window).pack(pady=(0, 10))

    # Filter Buttons
    filter_frame = tb.Frame(toolbar)
    filter_frame.pack(side="right")

    tb.Button(filter_frame, text="Show All", width=12, command=reset_filters, bootstyle="secondary").pack(side="left", padx=6)
    tb.Button(filter_frame, text="Only Expired", width=12, command=lambda: events.filter_status("❌"), bootstyle="danger").pack(side="left", padx=6)
    tb.Button(filter_frame, text="Near Expiry", width=12, command=lambda: events.filter_status("⚠️"), bootstyle="warning").pack(side="left", padx=6)

    # Treeview Section
    tree_frame = tb.Frame(root)
    tree_frame.pack(fill="both", expand=True, padx=15, pady=10)

    columns = ["Name", "Batch", "Mfg Date", "Expiry Date", "Quantity", "Price", "Demand", "Status"]
    tree = tb.Treeview(tree_frame, columns=columns, show="headings", bootstyle="info")

    tree.tag_configure("expired", background="#ffcccc")
    tree.tag_configure("near_expiry", background="#fff4cc")
    tree.tag_configure("low_stock", background="#ecd9c6")

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

    # Control buttons
    ctrl_btn_frame = tb.Frame(tree_frame)
    ctrl_btn_frame.pack(pady=10)

    btn_delete = tb.Button(ctrl_btn_frame, text="Delete Selected", width=18, command=events.delete_selected, bootstyle="danger")
    btn_export = tb.Button(ctrl_btn_frame, text="Export to CSV", width=18, command=events.export_to_csv, bootstyle="success")

    btn_delete.pack(side="left", padx=15)
    btn_export.pack(side="left", padx=15)

    create_tooltip(btn_delete, "Delete selected medicine")
    create_tooltip(btn_export, "Export current data to CSV file")

    # Tree selection logic
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

    def load_data_and_set_focus():
        events.load_data()

    root.after(100, lambda: entries[0].focus_force())
    root.after(100, load_data_and_set_focus)

    root.mainloop()
