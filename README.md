# 💊 MediTrack – Pharmacy Inventory Management System

MediTrack is a lightweight desktop application built using **Python and Tkinter** to help pharmacies efficiently manage their medicine inventory. It provides real-time expiry tracking, low-stock alerts, batch-wise management, and CSV export for reporting. The app is designed with usability in mind and works without requiring an internet connection or installation of complex software.

---

## 🚀 Features

- 📦 **Add, Edit, and Delete Medicines** with batch, price, quantity, expiry, and MFG details
- ⏳ **Expiry Tracking**: Automatically flags expired and near-expiry medicines
- 📉 **Low Stock Alerts**: Highlights medicines running below threshold quantity
- 🗂️ **Batch-wise Identification**: Avoids accidental deletion of all entries with same name
- 🔍 **Search & Filter**: Quickly find medicines by name or batch
- 📊 **Dashboard Summary**: Shows total medicines, expired, near-expiry, and low stock stats
- 🧮 **CSV Export**: Export inventory with expiry status for backup/reporting
- ⚠️ **Popup Alerts**: Get notified immediately about inventory issues at launch
- 🖼️ **Custom Desktop Icon + Standalone Executable**: Easily launchable by non-technical users

---

## 🛠️ Tech Stack

| Component       | Tool/Tech        |
|----------------|------------------|
| GUI Framework   | Tkinter (Python Standard Library) |
| Backend Logic   | Python 3.x       |
| Database        | SQLite           |
| Packaging       | PyInstaller      |
| Icon Conversion | ICOConvert / PNG-to-ICO tools     |
| Development IDE | VS Code          |

---

## 📁 Project Structure

pharmacy-inventory-app/
├── main.py # Entry point to launch the GUI
├── gui/
│ └── layout.py # UI layout and element definitions
├── events.py # Event handlers and business logic
├── database/
│ └── db_handler.py # SQLite operations (CRUD)
├── utils/
│ └── expiry_checker.py # Expiry logic (Expired / Near Expiry)
├── assets/
│ └── medi_icon.ico # App icon used for .exe
├── dist/
│ └── MediTrack.exe # Executable for Windows
└── README.md # Project documentation
