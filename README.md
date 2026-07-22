# 💊 IBSaúde — Smart Medication Tracking Platform

> A secure and traceable medication management platform designed for healthcare operations.

## 🚀 About the Project

This project is being developed as part of a three-month technology residency challenge.

Its goal is to provide complete medication control and traceability, covering the entire process from acquisition to distribution across healthcare units.

## ✨ Current Features

- User registration
- User listing and search
- User information editing
- User removal
- Role-based user classification:
  - Administrator
  - Pharmacist
  - Manager
  - Auditor

## 🛠️ Technology Stack

- Python
- Flask
- SQLite
- HTML
- Bootstrap
- Git and GitHub

## 📦 Installation

Clone the repository:

```powershell
git clone https://github.com/SEU-USUARIO/ibsaude-medication-tracking-platform.git
cd ibsaude-medication-tracking-platform
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

Initialize the database:

```powershell
python init_db.py
```

Run the application:

```powershell
python cadusuario.py
```

Open the application at:

http://127.0.0.1:5000

## 🗺️ Roadmap

- Secure authentication
- Role-based access control
- Medication registration
- Supplier and manufacturer management
- Acquisition management
- Inventory control by batch and expiration date
- Medication distribution
- Complete audit trail
- Administrative dashboard
- PDF and Excel reports
- PostgreSQL migration
- Cloud deployment

## 📌 Project Status

The project is currently under active development.

The initial user management module is functional. Authentication, security improvements, medication inventory, traceability, reporting, and deployment are planned for upcoming versions.