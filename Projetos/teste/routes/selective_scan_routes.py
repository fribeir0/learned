from fastapi import APIRouter, HTTPException
from models.scan_input import ScanRequest
from utils.runner import run_tool_async

router = APIRouter()

@router.post("/{tool_name}")
async def run_individual_tool(tool_name: str, scan_request: ScanRequest):
    target = scan_request.target
    tools = {
        "subfinder": ["subfinder", "-d", target, "-silent"],
        "dnsx": ["dnsx", "-silent"],
        "naabu": ["naabu", "-silent"],
        "httpx": ["httpx", "-silent", "-title"],
        "nuclei": ["nuclei", "-silent", "-json"]
    }
    if tool_name not in tools:
        raise HTTPException(status_code=400, detail="Tool inválida.")
    input_data = None if tool_name == "subfinder" else "\n".join([target])
    return await run_tool_async(tools[tool_name], tool_name, input_data)
