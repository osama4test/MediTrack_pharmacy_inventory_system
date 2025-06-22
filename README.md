# 💊 MediTrack – Pharmacy Inventory Management System

MediTrack is a lightweight desktop application built using Python and Tkinter to help pharmacies efficiently manage their medicine inventory and checkout process. It includes real-time expiry tracking, low-stock alerts, batch-wise management, and CSV export for reporting. The app runs offline, requires no installation, and is designed for easy use by pharmacy staff.

---

## 🚀 Features

- 📦 **Add, Edit, and Delete Medicines**  
  With details like batch number, price, quantity, expiry date, and manufacturing date

- ⏳ **Expiry Tracking**  
  Automatically highlights expired and near-expiry medicines

- 📉 **Low Stock Alerts**  
  Flags medicines running below threshold quantity

- 🗂️ **Batch-wise Management**  
  Ensures precise tracking and prevents bulk deletion of same-name entries

- 🔍 **Search & Filter**  
  Quickly find medicines by name or batch number

- 📊 **Dashboard Summary**  
  Total medicines, expired count, near-expiry items, and low stock insights

- 🧮 **CSV Export**  
  Export full inventory along with expiry and stock status

- 🛒 **New: Checkout Window with Cart Management**  
  - Add medicines to cart with quantity  
  - Real-time **Treeview cart display**  
  - ✅ Remove selected item from cart  
  - 💰 Total updates dynamically  
  - 🧾 Generates a printable receipt with reduced stock in database

- ⚠️ **Popup Alerts**  
  Get notified about critical stock and expiry issues at launch

- 🖼️ **Custom Desktop Icon + Executable**  
  Easily launchable `.exe` version for non-technical users

---

## 🛠️ Tech Stack

| Component      | Tool/Tech              |
|----------------|------------------------|
| GUI Framework  | Tkinter + ttkbootstrap |
| Backend Logic  | Python 3.x             |
| Database       | SQLite                 |
| Packaging      | PyInstaller            |
| Icon Creation  | ICOConvert, PNG-to-ICO |
| Development IDE| Visual Studio Code     |

---

## 📁 Project Structure

pharmacy-inventory-app/
├── main.py # Entry point to launch the GUI
├── gui/
│ ├── layout.py # UI layout and definitions
│ └── checkout_gui.py # Checkout window with Treeview-based cart
├── database/
│ └── db_handler.py # All SQLite database operations
├── utils/
│ └── expiry_checker.py # Logic to detect expired/near-expiry medicines
├── assets/
│ └── medi_icon.ico # Icon used for application executable
├── dist/
│ └── MediTrack.exe # Generated executable using PyInstaller
└── README.md # You're here!
