"""Data ingestion API for source-annotated sales records.

Validation only; no user-uploaded records are silently persisted or used to train models.
"""
from fastapi import APIRouter
from pydantic import BaseModel,Field
from backend.data_quality import validate_transactions,holdout_diagnostics
router=APIRouter(prefix="/api/transactions",tags=["transactions"])
class Upload(BaseModel):
    records:list[dict]=Field(default_factory=list,max_length=2000)
    cutoff:str="2025-01-01"
@router.post("/validate")
def validate(data:Upload):
    v=validate_transactions(data.records)
    return {"accepted_count":v["accepted_count"],"rejected":v["rejected"],
            "holdout":holdout_diagnostics(v["accepted"],data.cutoff),
            "notice":"Validation does not prove authenticity, ownership, license validity or fair market value. No records were stored."}
