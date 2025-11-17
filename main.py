import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import create_document, get_documents, db
from schemas import Appointment, ContactMessage

app = FastAPI(title="Tattoo Studio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Tattoo Studio API is running"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
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
            response["database_name"] = getattr(db, 'name', "✅ Connected")
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

# Appointments Endpoints
@app.post("/appointments")
def create_appointment(payload: Appointment):
    try:
        inserted_id = create_document("appointment", payload)
        return {"status": "ok", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/appointments")
def list_appointments(limit: Optional[int] = 50):
    try:
        docs = get_documents("appointment", {}, limit)
        # Convert ObjectId to string if present
        for d in docs:
            if "_id" in d:
                d["id"] = str(d.pop("_id"))
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Contact Messages
@app.post("/contact")
def submit_contact(msg: ContactMessage):
    try:
        inserted_id = create_document("contactmessage", msg)
        return {"status": "ok", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Optional: simple products for shop placeholder
class ProductModel(BaseModel):
    id: str
    title: str
    price: float
    image: str
    description: Optional[str] = None

SAMPLE_PRODUCTS = [
    ProductModel(id="aftercare", title="Gold-Infused Aftercare Balm", price=24.0, image="/aftercare.jpg", description="Nourishing balm with botanical oils."),
    ProductModel(id="print-forest", title="Limited Print: Forest Sigil", price=60.0, image="/print.jpg", description="Giclée print on textured paper."),
]

@app.get("/products", response_model=List[ProductModel])
def list_products():
    return SAMPLE_PRODUCTS


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
