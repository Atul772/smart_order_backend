---

# 🛒 Smart Order Processing Backend

A **production-grade backend system** built using **Django 5.2** and **Django REST Framework**, implementing secure authentication, order management, payment processing, caching, async notifications, and comprehensive testing.

This project follows **clean architecture principles**, focuses on **correct business logic**, and is designed to handle **real-world scale and failures**.

---

## 🚀 Features Overview

### 🔐 Authentication & Authorization

* User registration and login
* JWT-based authentication
* Role-based access (User vs Admin)
* Secure permission enforcement
* Fully tested auth APIs

---

### 📦 Product Management

* List available products
* View individual product details
* Product availability checks
* Admin product management
* Redis-based caching for availability
* Cache invalidation on stock changes

---

### 🛒 Order Management

* Create orders (only for available products)
* Cancel orders (with business rules)
* Admin can update order status
* Strict order lifecycle enforcement
* Atomic stock updates using transactions

---

### 💳 Payment Processing

* Payment initiation & completion
* Idempotent payment handling
* Duplicate callback safety
* Order–payment state consistency
* Retry support for failed payments

---

### 📬 Notifications (Async)

* Email & SMS notifications
* Powered by **Celery + Redis**
* Background execution
* Retry & failure handling
* Request ID propagated for observability

---

### ⚡ Performance & Scalability

* Redis caching with TTL
* Optimized ORM queries
* Designed to handle:

  * ~500 concurrent users
  * ~5000 orders efficiently

---

### 🧪 Testing

* Unit tests & service-layer tests
* API tests for auth, orders, payments
* Transaction rollback tests
* Idempotency tests
* PostgreSQL-backed test database
* **100% passing test suite**

---

### 🔍 Observability & Debugging

* Custom request ID middleware
* Structured logging
* Request ID in logs & responses
* Easier debugging across async tasks

---

## 🏗️ Tech Stack

| Layer          | Technology             |
| -------------- | ---------------------- |
| Backend        | Django 5.2             |
| API            | Django REST Framework  |
| Database       | PostgreSQL             |
| Cache          | Redis                  |
| Async Tasks    | Celery                 |
| Authentication | JWT                    |
| Testing        | Pytest + pytest-django |
| Logging        | Python logging         |

---

## 📁 Project Structure

```text
smart_order_backend/
│
├── accounts/        # User auth & profiles
├── products/        # Product catalog & availability
├── orders/          # Order creation & lifecycle
├── payments/        # Payment processing
├── notifications/   # Email & SMS tasks (Celery)
├── core/            # Middleware, health checks, shared logic
│
├── config/          # Django project settings
├── tests/           # App-wise test suites
└── manage.py
```

---

## 🔄 High-Level Flow

1. User registers & logs in (JWT issued)
2. User views available products (cached)
3. User creates an order
4. Stock is reserved atomically
5. User initiates payment
6. Payment is completed (SUCCESS / FAILED)
7. Order status updated accordingly
8. Email & SMS notifications sent asynchronously

---

## 🔐 API Versioning

All APIs are versioned:

```
/api/v1/...
```

Example:

* `/api/v1/accounts/register/`
* `/api/v1/products/`
* `/api/v1/orders/`
* `/api/v1/payments/initiate/`

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository

```bash
git clone <repo-url>
cd smart_order_backend
```

---

### 2️⃣ Create virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

---

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Configure environment variables

Create a `.env` file with:

```env
DEBUG=True
SECRET_KEY=your-secret-key
DB_NAME=smartdb
DB_USER=smartuser
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://127.0.0.1:6379/0
```

---

### 5️⃣ Run migrations

```bash
python manage.py migrate
```

---

### 6️⃣ Start services

```bash
# Django server
python manage.py runserver

# Redis
redis-server

# Celery worker
celery -A config worker -l info
```

---

## 🧪 Running Tests

```bash
pytest
```

✔ All tests pass successfully.

---

## 🔧 Admin Panel

```bash
python manage.py createsuperuser
```

Access:

```
http://127.0.0.1:8000/admin/
```

Admins can manage:

* Users
* Products
* Orders
* Payments

---

## 🧠 Design Principles Followed

* Separation of concerns
* Service-layer architecture
* Transaction safety
* Idempotency in payments
* Fail-fast validation
* Clean, testable code
* Scalability-first mindset

---
