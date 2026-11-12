from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from database import Base, engine
from routers import products, customers


@asynccontextmanager
async def lifespan(app: FastAPI):
    # For this learning project, create missing tables at startup.
    # Use Alembic migrations for schema changes in production.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Product & Customer Management API",
    description="CRUD REST API built with Python, FastAPI, PostgreSQL, SQLAlchemy, and Pydantic.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/", tags=["Home"])
def home():
    return {"message": "Product & Customer Management API is running"}


@app.get("/health", tags=["Health"])
def health_check():
    # Confirms that the API can reach PostgreSQL.
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"status": "healthy", "database": "connected"}


app.include_router(products.router)
app.include_router(customers.router)
