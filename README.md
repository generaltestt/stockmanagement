# Stock Management System

A coursework project built with a **Flask REST API** backend and a **Kivy** mobile/desktop frontend for managing in-store stock operations.

## Features

- 🔐 Store & colleague login with JWT authentication
- 📦 Product and stock management
- 🚚 Delivery tracking and processing
- 🔍 Barcode scanning
- 📊 Gap scanning & accuracy reporting
- 🗑️ Waste logging

## Project Structure

```
OCRCoursework/
├── backend/          # Flask API
│   ├── app.py        # Main application & routes
│   ├── models.py     # Database models (SQLAlchemy)
│   ├── test.py       # Tests
│   └── requirements.txt
└── kivy-app/         # Kivy frontend
    ├── main.py       # App entry point
    ├── api.py        # API client
    ├── login.py      # Login screen
    └── screens/      # Individual app screens
```

## Setup & Running

### Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

The API will run at `http://localhost:5000`.

### Kivy App

```bash
cd kivy-app
pip install kivy requests
python main.py
```

## Tech Stack

- **Backend:** Python, Flask, Flask-SQLAlchemy, SQLite, JWT
- **Frontend:** Python, Kivy
