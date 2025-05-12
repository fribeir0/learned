from fastapi import APIRouter, HTTPException
from models.scan_input import ScanRequest
from services.scan_pipeline import execute_scan
from utils.history_tracker import save_scan_result

router = APIRouter()

@router.post("/")
async def scan_target(scan_request: ScanRequest):
    try:
        result = await execute_scan(scan_request.target)
        save_scan_result(scan_request.target, result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
