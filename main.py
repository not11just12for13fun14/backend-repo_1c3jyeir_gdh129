import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime, time

from database import db, create_document, get_documents
from schemas import Expense

app = FastAPI(title="Daily Expense Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Expense Tracker Backend Ready"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

# -----------------------------
# Expense Endpoints
# -----------------------------
class ExpenseCreate(BaseModel):
    amount: float
    category: str
    date: date
    notes: Optional[str] = None
    payment_method: Optional[str] = None
    merchant: Optional[str] = None

@app.post("/api/expenses")
def add_expense(payload: ExpenseCreate):
    try:
        # Validate via Pydantic schema (schemas.Expense)
        exp = Expense(**payload.model_dump())
        data = exp.model_dump()
        # Convert date (date) to datetime for MongoDB storage compatibility
        if isinstance(data.get("date"), date) and not isinstance(data.get("date"), datetime):
            d: date = data["date"]
            data["date"] = datetime.combine(d, time.min)
        inserted_id = create_document("expense", data)
        return {"id": inserted_id, "message": "Expense added"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/expenses")
def list_expenses(category: Optional[str] = None, start: Optional[date] = None, end: Optional[date] = None, limit: int = 100):
    filter_dict = {}
    if category:
        filter_dict["category"] = category
    if start or end:
        date_filter = {}
        if start:
            date_filter["$gte"] = datetime.combine(start, datetime.min.time())
        if end:
            date_filter["$lte"] = datetime.combine(end, datetime.max.time())
        filter_dict["date"] = date_filter

    docs = get_documents("expense", filter_dict or {}, limit)
    # Convert ObjectId and dates to serializable
    for d in docs:
        d["id"] = str(d.pop("_id", ""))
        if isinstance(d.get("date"), datetime):
            d["date"] = d["date"].isoformat()
        elif isinstance(d.get("date"), date):
            d["date"] = datetime.combine(d["date"], time.min).isoformat()
        if isinstance(d.get("created_at"), datetime):
            d["created_at"] = d["created_at"].isoformat()
        if isinstance(d.get("updated_at"), datetime):
            d["updated_at"] = d["updated_at"].isoformat()
    return {"items": docs}

@app.get("/api/summary")
def get_summary(month: Optional[int] = None, year: Optional[int] = None):
    """Return monthly total and totals per category"""
    try:
        filter_dict = {}
        if month and year:
            start_dt = datetime(year, month, 1)
            if month == 12:
                end_dt = datetime(year + 1, 1, 1)
            else:
                end_dt = datetime(year, month + 1, 1)
            filter_dict["date"] = {"$gte": start_dt, "$lt": end_dt}

        docs = get_documents("expense", filter_dict)
        total = 0.0
        per_category = {}
        for d in docs:
            amt = float(d.get("amount", 0))
            total += amt
            cat = d.get("category", "Lainnya")
            per_category[cat] = per_category.get(cat, 0.0) + amt
        return {
            "total": round(total, 2),
            "per_category": {k: round(v, 2) for k, v in per_category.items()}
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
