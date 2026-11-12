# Product & Customer Management REST API

A beginner-friendly backend project built with Python, FastAPI, PostgreSQL, SQLAlchemy ORM, and Pydantic.

## Features

- Product CRUD endpoints
- Customer CRUD endpoints
- PostgreSQL persistence
- Pydantic request/response validation
- Duplicate SKU and email handling (`409 Conflict`)
- HTTP errors for missing records (`404 Not Found`)
- Pagination via `skip` and `limit`
- Interactive Swagger UI
- Health endpoint to check database connectivity

## Project structure

```text
product_customer_api/
├── main.py
├── database.py
├── models.py
├── schemas.py
├── requirements.txt
├── .env.example
├── .gitignore
└── routers/
    ├── __init__.py
    ├── products.py
    └── customers.py
```

## Requirements

- Python 3.11+
- PostgreSQL
- Cursor IDE

## Setup on Windows

1. Install Python and PostgreSQL.
2. In PostgreSQL, create the database:

   ```sql
   CREATE DATABASE product_customer_db;
   ```

3. Open this project folder in Cursor.
4. Open Cursor Terminal and create a virtual environment:

   ```powershell
   python -m venv venv
   ```

5. Activate it:

   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt terminal and run:

   ```bat
   venv\Scripts\activate.bat
   ```

6. Install packages:

   ```bash
   python -m pip install -r requirements.txt
   ```

7. Copy `.env.example` to `.env`. On Windows PowerShell:

   ```powershell
   Copy-Item .env.example .env
   ```

8. Edit `.env` and set your real PostgreSQL username and password:

   ```text
   DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/product_customer_db
   ```

   If your password contains URL-special characters, URL-encode them.

9. Start the API:

   ```bash
   uvicorn main:app --reload
   ```

10. Open Swagger UI: http://127.0.0.1:8000/docs

## Example product JSON

Use `POST /products/`:

```json
{
  "name": "Wireless Mouse",
  "description": "Wireless optical mouse",
  "price": 799.0,
  "stock_quantity": 50,
  "sku": "MOUSE-001",
  "category": "Electronics",
  "is_active": true
}
```

## Example customer JSON

Use `POST /customers/`:

```json
{
  "name": "Ravi Kumar",
  "email": "ravi@example.com",
  "phone": "9876543210",
  "address": "Hitech City",
  "city": "Hyderabad",
  "state": "Telangana",
  "pincode": "500081",
  "is_active": true
}
```

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Welcome message |
| GET | `/health` | Check database connection |
| POST | `/products/` | Create product |
| GET | `/products/` | List products |
| GET | `/products/{product_id}` | Get one product |
| PATCH | `/products/{product_id}` | Update product fields |
| DELETE | `/products/{product_id}` | Delete product |
| POST | `/customers/` | Create customer |
| GET | `/customers/` | List customers |
| GET | `/customers/{customer_id}` | Get one customer |
| PATCH | `/customers/{customer_id}` | Update customer fields |
| DELETE | `/customers/{customer_id}` | Delete customer |

List endpoints support `?skip=0&limit=10`.

## Troubleshooting

- **Connection refused:** Confirm PostgreSQL is running and port/host are correct.
- **Password authentication failed:** Check the username/password in `.env`.
- **Database does not exist:** Create `product_customer_db` in PostgreSQL.
- **Email validation error:** Use a valid email address.
- **409 Conflict:** The SKU or email may already exist; use a unique value.
- **ModuleNotFoundError:** Activate `venv` and install requirements again.

## Notes

This is an educational project. `Base.metadata.create_all()` creates missing tables but does not migrate existing schemas. For production, use Alembic migrations, authentication/authorization, tests, structured logging, and secret management. Do not commit `.env` to source control.
