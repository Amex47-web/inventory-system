#  Smart Stock Management System

A robust, enterprise-grade Inventory Management System built with **Django**. This application goes beyond simple counting by integrating **Machine Learning** for demand forecasting, **QR Code scanning** for quick lookup, and a **Bulk Cart** system for efficient stock distribution.

Live Demo: https://inventory-system-amey.onrender.com

---

##  Key Features

###  1. AI-Powered Demand Forecasting
Uses **Linear Regression (Scikit-Learn)** to analyze historical usage patterns and predict exactly when an item will run out of stock.
- **Visual Trends:** View burn-rate charts.
- **Smart Alerts:** "Days remaining" countdown based on actual consumption, not just static thresholds.

###  2. QR Code Integration
- **Scan-to-View:** Use your laptop or phone camera to scan item QR codes.
- **Instant Lookup:** deeply integrated with the search system for rapid inventory audits.

###  3. Bulk Issue "Shopping Cart"
- **Session-Based Cart:** Managers can add multiple items (Laptop, Mouse, Charger) to a temporary list.
- **One-Click Checkout:** Issue all items to an employee in a single transaction, updating inventory instantly.

###  4. Financial & Activity Analytics
- **Asset Valuation:** Real-time calculation of Total Inventory Value (Quantity × Unit Price).
- **Interactive Dashboards:** Chart.js integration for visual breakdown of Stock Levels, Categories, and In/Out history.
- **ABC Analysis:** Automated categorization of high-value vs. low-value stock.

###  5. Enterprise Security & UI
- **Role-Based Access Control (RBAC):** Distinct permissions for Admins (Full Access) vs. Staff (Read/Issue only).
- **Dark/Light Mode:** Persists user preference across sessions.
- **Mobile Responsive:** Built with Bootstrap 4 & DashLite for perfect rendering on tablets and phones.

---

## 🛠️ Tech Stack

**Backend:**
- Python 3.10+
- Django 5.x
- **ML/Data:** Scikit-Learn, NumPy, Pandas (for forecasting)
- **Database:** PostgreSQL (Production), SQLite (Local Dev)

**Frontend:**
- HTML5, CSS3, JavaScript
- **Chart.js** (Data Visualization)
- **Html5-Qrcode** (Scanner)
- Bootstrap 4 (Responsive UI)

**Deployment & DevOps:**
- **Host:** Render.com
- **Server:** Gunicorn
- **Static Files:** WhiteNoise
- **CI/CD:** Automatic deployment via GitHub

---

##  Screenshots

### **Smart Dashboard (Dark Mode)**
*Real-time overview of assets, low stock alerts, and financial value.*
<img src="<img width="2940" height="1602" alt="Image" src="https://github.com/user-attachments/assets/c6e971b5-2333-45fc-a34c-ebf5cc95e901" />" alt="Dashboard">

### **AI Inventory Forecast**
*Predictive analytics showing burn rate and estimated stockout dates.*
<img src="<img width="2042" height="1184" alt="Image" src="https://github.com/user-attachments/assets/c20e1cdf-107a-4274-b053-549bbc19bf84" />" alt="AI Forecast">

### **Bulk Issue Cart**
*Add multiple items to a cart and issue them in one go.*
<img src="https://user-images.githubusercontent.com/89584431/213712524-32478065-e0cd-45f7-939e-2f9d41c82f63.gif" alt="Bulk Cart">

### **Stock List with QR Support**
*Manage inventory with search, edit, delete, and history tracking.*
<img src="https://user-images.githubusercontent.com/89584431/213707384-a08835e1-3322-40ac-b09f-186fa7a2b64f.png" alt="Stock List">

### **Login Page**
*Secure and Robust authentication.*
<img src="<img width="2940" height="1604" alt="Image" src="https://github.com/user-attachments/assets/c6953a59-9483-4124-937a-0421b685136b" />" alt="Login page">

---

##  Local Installation Guide

Follow these steps to run the project on your machine.

**Prerequisites:** Python 3.10+ installed.

1. **Clone the Repository**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/inventory-system.git](https://github.com/YOUR_USERNAME/inventory-system.git)
   cd inventory-system
   Create Virtual Environment

2. Create Virtual Environment

# Windows
python -m venv venv
.\venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate


3. Install Dependencies
   pip install -r requirements.txt
   
5. Setup Database
   python manage.py makemigrations
python manage.py migrate

7. Create Admin User
   python manage.py createsuperuser
   
9. Run Server
    python manage.py runserver


   Deployment (Render.com)
This project is configured for seamless deployment on Render.

Fork/Clone this repo to your GitHub.

Create a new Web Service on Render.

Connect your repository.

Environment Variables:

PYTHON_VERSION: 3.10.0

SECRET_KEY: (Generate a random string)

DATABASE_URL: (Render creates this automatically if you link a Postgres DB)

Build Command: ./build.sh

Start Command: gunicorn stockmgtr.wsgi:application

Contributing
Contributions are welcome!

Fork the project.

Create your feature branch (git checkout -b feature/AmazingFeature).

Commit your changes (git commit -m 'Add some AmazingFeature').

Push to the branch (git push origin feature/AmazingFeature).

Open a Pull Request.

License
Distributed under the MIT License. See LICENSE for more information.
