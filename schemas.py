"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
import datetime as dt

# Example schemas (you can keep or remove these if not needed)
class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# --------------------------------------------------
# Daily Expense Tracker Schemas
# --------------------------------------------------

ExpenseCategory = Literal[
    "Makanan & Minuman",
    "Transportasi",
    "Belanja",
    "Tagihan",
    "Kesehatan",
    "Hiburan",
    "Pendidikan",
    "Lainnya",
]

class Expense(BaseModel):
    """
    Expense collection schema
    Collection name: "expense"
    """
    amount: float = Field(..., gt=0, description="Nominal pengeluaran")
    category: ExpenseCategory = Field(..., description="Kategori pengeluaran")
    date: dt.date = Field(..., description="Tanggal pengeluaran (YYYY-MM-DD)")
    notes: Optional[str] = Field(None, description="Catatan tambahan")
    payment_method: Optional[str] = Field(None, description="Metode pembayaran (cash, e-wallet, bank)")
    merchant: Optional[str] = Field(None, description="Tempat/merchant")
