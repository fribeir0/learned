from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.scan_routes import router as scan_router
from routes.selective_scan_routes import router as selective_router
from routes.metabigor_route import router as metabigor_router
from routes.history_routes import router as history_router
from utils.logger import setup_logger

app = FastAPI()

setup_logger()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scan_router, prefix="/scan", tags=["Scan"])
app.include_router(selective_router, prefix="/tool", tags=["Tools"])
app.include_router(metabigor_router, prefix="/metabigor", tags=["Metabigor"])
app.include_router(history_router, prefix="/history", tags=["History"])
