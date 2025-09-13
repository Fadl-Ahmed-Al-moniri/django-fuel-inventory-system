<div align="center">
  <img src="https://raw.githubusercontent.com/Fadl-Ahmed-Al-moniri/django-fuel-inventory-system/main/.github/assets/logo.png" alt="Project Logo" width="150">
  <h1 align="center">Fuel Inventory System</h1>
  <p align="center">
    A comprehensive fuel inventory and storage management system built with Django, DRF, and PostgreSQL.
  </p>
  
  <!-- Badges -->
  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.10%2B-blue.svg" alt="Python Version">
    <img src="https://img.shields.io/badge/Django-5.0-darkgreen.svg" alt="Django Version">
    <img src="https://img.shields.io/badge/DRF-3.15-red.svg" alt="DRF Version">
    <img src="https://img.shields.io/badge/Database-PostgreSQL-blue.svg" alt="Database">
    <img src="https://img.shields.io/github/license/Fadl-Ahmed-Al-moniri/django-fuel-inventory-system" alt="License">
    <img src="https://img.shields.io/github/last-commit/Fadl-Ahmed-Al-moniri/django-fuel-inventory-system" alt="Last Commit">
  </p>
</div>

---

## 📋 Table of Contents

- [About The Project](#about-the-project )
- [✨ Key Features](#-key-features)
- [🛠️ Tech Stack](#️-tech-stack)
- [🚀 Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation & Setup](#installation--setup)
- [🔌 API Endpoints](#-api-endpoints)
- [📂 Project Structure](#-project-structure)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [📧 Contact](#-contact)

---

## 📖 About The Project

**Fuel Inventory System** is a robust backend API designed to manage the entire lifecycle of fuel products in a warehouse environment. From receiving supplies to dispatching them, tracking returns, and managing damages, this system provides a centralized, secure, and efficient solution. It is built using modern technologies to ensure scalability and maintainability.

---

## ✨ Key Features

- **👤 User & Account Management:** Secure user authentication and authorization using **JWT (JSON Web Tokens)**.
- **📦 Inventory Management:**
  - Manage warehouses, items (fuel types), suppliers, and beneficiaries.
  - Real-time tracking of item quantities and stock levels.
- **🚚 Operations Tracking:**
  - **Supply Operations:** Record incoming fuel supplies from suppliers.
  - **Dispatch Operations:** Track fuel dispatched to beneficiaries.
  - **Returns Management:** Handle both supply and dispatch returns efficiently.
  - **Warehouse Transfers:** A process of transferring from the sender's warehouse to the recipient's warehouse.
  - **Damage Logging:** Record and manage damaged or lost items.
- **🔄 Quantity Modification:** Secure endpoints to modify and correct operational quantities with detailed logging.
- **📈 Reporting:** Generate detailed reports on inventory status and movement.
- **🔒 Secure & Scalable:** Built with Django Rest Framework, following best practices for security and performance.

---

## 🛠️ Tech Stack

This project is built with a modern and powerful stack:

- **Backend:** Django, Django Rest Framework (DRF)
- **Database:** PostgreSQL
- **Authentication:** djangorestframework-simplejwt (JWT)
- **CORS:** django-cors-headers
- **Environment Variables:** python-decouple

---

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- **Python 3.10+**
- **PostgreSQL** installed and running.
- **Git**

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Fadl-Ahmed-Al-moniri/django-fuel-inventory-system.git
    cd django-fuel-inventory-system
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up the database:**
    - Create a new PostgreSQL database and a user with privileges.
    - For example, using `psql`:
      ```sql
      CREATE DATABASE fuel_warehousesdb;
      CREATE USER fuelwarehousesuser WITH PASSWORD 'password';
      GRANT ALL PRIVILEGES ON DATABASE fuel_warehousesdb TO fuelwarehousesuser;
      ```

5.  **Configure environment variables:**
    - Create a `.env` file in the project root by copying the example file.
      ```bash
      cp .env.example .env
      ```
    - Open the `.env` file and fill in your secret key and database credentials.
      ```ini
      # .env
      SECRET_KEY='your-super-secret-key-here'
      DEBUG=True
      DB_NAME=fuel_warehousesdb
      DB_USER=fuelwarehousesuser
      DB_PASSWORD=password
      DB_HOST=localhost
      DB_PORT=5432
      ```

6.  **Apply database migrations:**
    ```bash
    python manage.py migrate
    ```

7.  **Create a superuser (optional ):**
    ```bash
    python manage.py createsuperuser
    ```

8.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    The API will be available at `http://127.0.0.1:8000/`.

---

## 🔌 API Endpoints

Here are some of the main API endpoints available:

## 🔐 Authentication
| Method | Endpoint               | Description                               |
| :----- | :--------------------- | :---------------------------------------- |
| `POST` | `/api/auth/login/`     | Obtain JWT access and refresh tokens.     |
| `POST` | `/api/auth/register/`  | Create a new user.                        |

---

## 📦 Inventory
| Method | Endpoint                        | Description                       |
| :----- | :------------------------------ | :-------------------------------- |
| `POST` | `/api/inventory/items/`         | Create a new inventory items.     |
| `GET`  | `/api/inventory/items/`         | Get a list of all inventory items.|
| `POST` | `/api/inventory/warehouses/`    | Create a new inventory warehouses.|
| `GET`  | `/api/inventory/warehouses/`    | Get a list of all warehouses.     |
| `POST` | `/api/inventory/warehouse-item/`| Create a new warehouse items.     |
| `GET`  | `/api/inventory/warehouse-item/`| List warehouse items.             |
| `POST` | `/api/inventory/station/`       | Create a new inventory stations.  |
| `GET`  | `/api/inventory/station/`       | List stations.                    |

---

## 🔄 Operations
| Method | Endpoint                             | Description                               |
| :----- | :----------------------------------- | :---------------------------------------- |
| `POST` | `/api/operations/supply/`            | Create a new supply operation.            |
| `GET`  | `/api/operations/supply/`            | List all supply operations.               |
| `POST` | `/api/operations/export/`            | Create a new dispatch operation.          |
| `GET`  | `/api/operations/export/`            | List all dispatch operations.             |
| `POST` | `/api/operations/modify_supply/`     | Modify an existing supply item quantity.  |
| `GET`  | `/api/operations/modify_supply/`     | List all modified supply operations.      |
| `POST` | `/api/operations/modify_export/`     | Modify an existing export item quantity.  |
| `GET`  | `/api/operations/modify_export/`     | List all modified dispatch operations.    |
| `POST` | `/api/operations/return_supply/`     | Create a new return supply operation.     |
| `GET`  | `/api/operations/return_supply/`     | List all return supply operations.        |
| `POST` | `/api/operations/return_export/`     | Create a new return dispatch operation.   |
| `GET`  | `/api/operations/return_export/`     | List all return dispatch operations.      |
| `POST` | `/api/operations/damage/`            | Create a new damage operation.            |
| `GET`  | `/api/operations/damage/`            | List all damage operations.               |
| `POST` | `/api/operations/transfer/`          | Create a new transfer operation.          |
| `GET`  | `/api/operations/transfer/`          | List all transfer operations.             |

---

## 📊 Reports
| Method | Endpoint                                                                 | Description                                                |
| :----- | :----------------------------------------------------------------------- | :--------------------------------------------------------- |
| `GET`  | `/api/reports/item-status/?item_id=1&start_date=&end_date=`              | Get a status report for a specific item.                   |
| `GET`  | `/api/reports/general-warehouse/?warehouse_id=1&start_date=&end_date=`   | Get a general warehouse summary report.                    |
| `GET`  | `/api/reports/warehouse-status/?warehouse_id=1&start_date=&end_date=`    | Get the current status of warehouses.                      |
| `GET`  | `/api/reports/supplier-operations/?supplier_id=1&start_date=&end_date=`  | Get a report of supplier-related operations.               |
| `GET`  | `/api/reports/beneficiary-operations/?beneficiary_id=1&start_date=&end_date=` | Get a report of beneficiary-related operations.        |
| `GET`  | `/api/reports/stations-operations/?stations_id=1&start_date=&end_date=`  | Get a report of stations-related operations.               |
| `GET`  | `/api/reports/item-status/?item_id=1&start_date=&end_date=`              | Get a detailed item status report (all items or filtered). |
| `GET`  | `/api/reports/general-item/?item_id=1&start_date=&end_date=`             | Get a general summary of item-related operations.          |


---

## 📂 Project Structure

A brief overview of the project's directory structure:


django-fuel-inventory-system/
├── accounts/         # Manages users, authentication
├── inventory/        # Manages warehouses, items, suppliers
├── operations/       # Manages supply, dispatch, returns
├── reports/          # Handles report generation
├── fuel_warehouses/  # Main project configuration (settings.py)
├── .env.example      # Environment variables template
├── manage.py         # Django's command-line utility
└── requirements.txt  # Project dependencies

---

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` file for more information.

---

## 📧 Contact

Fadl Ahmed Al-moniri - [fadlahmedalmoniri@gmail.com](mailto:fadlahmedalmoniri@gmail.com)

Project Link: [https://github.com/Fadl-Ahmed-Al-moniri/django-fuel-inventory-system](https://github.com/Fadl-Ahmed-Al-moniri/django-fuel-inventory-system )


