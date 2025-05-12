from fastapi import APIRouter, HTTPException
from models.scan_input import ScanRequest
from services.metabigor import run_metabigor

router = APIRouter()

@router.post("/")
def metabigor_scan(scan_request: ScanRequest):
    try:
        return run_metabigor(scan_request.target)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
