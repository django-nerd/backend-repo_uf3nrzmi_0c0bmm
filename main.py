import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List

from database import create_document, get_documents
from schemas import (
    Trust,
    Beneficiary,
    Trustee,
    Asset,
    Distribution,
    NGO,
    Donation,
    ComplianceDocument,
)

app = FastAPI(title="Living Trust & NGO Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Living Trust & NGO Management Backend is running"}


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
        from database import db
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
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


# ---------------------- Schema Introspection ----------------------

@app.get("/schema")
def get_schema() -> Dict[str, Any]:
    """Expose JSON schema for each collection model."""
    models = {
        "trust": Trust,
        "beneficiary": Beneficiary,
        "trustee": Trustee,
        "asset": Asset,
        "distribution": Distribution,
        "ngo": NGO,
        "donation": Donation,
        "compliancedocument": ComplianceDocument,
    }
    return {name: model.model_json_schema() for name, model in models.items()}


# ---------------------- CRUD Endpoints (Create + List) ----------------------

# Map collection names to Pydantic models for validation
COLLECTION_MODELS: Dict[str, BaseModel] = {
    "trust": Trust,
    "beneficiary": Beneficiary,
    "trustee": Trustee,
    "asset": Asset,
    "distribution": Distribution,
    "ngo": NGO,
    "donation": Donation,
    "compliancedocument": ComplianceDocument,
}


@app.get("/api/{collection}")
def list_documents(collection: str, limit: int | None = 50):
    collection = collection.lower()
    if collection not in COLLECTION_MODELS:
        raise HTTPException(status_code=404, detail="Unknown collection")
    try:
        docs = get_documents(collection, limit=limit)
        # Convert ObjectId to string where present
        for d in docs:
            if "_id" in d:
                d["_id"] = str(d["_id"])
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/{collection}")
def create_document_endpoint(collection: str, payload: Dict[str, Any]):
    collection = collection.lower()
    if collection not in COLLECTION_MODELS:
        raise HTTPException(status_code=404, detail="Unknown collection")

    Model = COLLECTION_MODELS[collection]
    try:
        obj = Model(**payload)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Validation error: {str(e)}")

    try:
        new_id = create_document(collection, obj)
        return {"id": new_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------- Dashboard Summary ----------------------

@app.get("/api/summary")
def get_summary():
    """Basic KPIs for dashboard cards."""
    try:
        trusts = get_documents("trust", {})
        beneficiaries = get_documents("beneficiary", {})
        assets = get_documents("asset", {})
        ngos = get_documents("ngo", {})
        donations = get_documents("donation", {})

        total_donation = sum(float(d.get("amount", 0) or 0) for d in donations)
        asset_value = sum(float(a.get("value", 0) or 0) for a in assets)

        return {
            "trusts": len(trusts),
            "beneficiaries": len(beneficiaries),
            "assets": len(assets),
            "ngos": len(ngos),
            "donations": len(donations),
            "total_donation": total_donation,
            "total_asset_value": asset_value,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
