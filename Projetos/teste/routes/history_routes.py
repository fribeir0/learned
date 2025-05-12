from fastapi import APIRouter, HTTPException
from utils.history_tracker import load_latest_scan, compare_scans

router = APIRouter()

@router.get("/{target}")
def get_scan_history(target: str):
    current, previous = load_latest_scan(target)
    if not current or not previous:
        raise HTTPException(status_code=404, detail="Histórico insuficiente.")
    return {
        "target": target,
        "last_scan": current,
        "previous_scan": previous,
        "changes": compare_scans(current, previous)
    }
