# Backup GUI

A simple GTK3 graphical tool for creating ZIP backups with support for multiple source directories, real-time progress tracking, and automatic daily log generation.

## 📌 Overview
This project provides a clean and practical interface for:
- Selecting multiple source directories.
- Choosing a destination directory.
- Tracking backup progress in real time.
- Generating daily log files containing:
  - Source → destination mappings.
  - Timestamps.
  - Success or error messages.

The application uses **GTK 3 (PyGObject)**, executes the backup in a separate thread to keep the UI responsive, and generates one ZIP file per day.

## 🗂️ Project Structure
```
backup_gui.py        # Main application script
main_window.ui       # GTK Builder UI layout
screenshots/         # Interface screenshots
README.md            # This document
```

<img width="1382" height="831" alt="01" src="https://github.com/codelibet/backupgui/blob/main/screenshots/05.png" />


## 🚀 Features
### ✔ Simple graphical interface
Built using **Gtk.Builder**, with dynamically generated source input fields.

### ✔ Multiple source directories
Each time a source entry is filled or a folder is selected, a new field is automatically created.

### ✔ Thread-safe operations
Backup runs in a *separate thread*, keeping the GUI responsive.

### ✔ Progress bar
Displays the percentage based on the real file count.

### ✔ Organized logs
For each day, a `backupYYYY-MM-DD.log` is created containing:
- Source → destination entries
- Timestamps
- Completion or error notices

### ✔ ZIP backup
Uses `zipfile.ZipFile` with **ZIP_DEFLATED** compression.

## 🛠 Requirements
- Python 3
- PyGObject (GTK3)
- GLib
- GTK 3 runtime libraries

### Dependencies on Arch Linux
```bash
python
python-gobject
gtk3
```

### Dependencies on Ubuntu / Debian
```bash
python3
python3-gi
python3-gi-cairo
gir1.2-gtk-3.0
```

### Dependencies on Fedora
```bash
python3
python3-gobject
gtk3
```

## ▶ Running the Application
From the project directory:
```bash
python3 backup_gui.py
```

Or make it executable:
```bash
chmod +x backup_gui.py
./backup_gui.py
```

## 🧩 Code Architecture
### 🔹 Log handling
Functions dedicated to logging:
- `log_od` – source → destination and timestamps
- `log_concluido` – completion notice
- `log_erro` – error notice

### 🔹 Dynamic interface
`adicionar_campo_origem()` automatically creates additional folder selection fields.

### 🔹 Backup execution
`fazer_backup_thread`:
- Counts all files.
- Compresses them while preserving relative paths.
- Updates the progress bar.
- Sends status messages and writes logs.

### 🔹 GTK thread safety
Uses `GLib.idle_add` to safely update the UI from the backup thread.

## 📸 Screenshots
Screenshots are available in the `screenshots/` directory.

## 📄 License
This project is released under the **MIT License**, a permissive free software license.

