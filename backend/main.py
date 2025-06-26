# main.py - FastAPI application
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from routers import orders, menu, inventory, staff
from database import engine
from models import Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="GastroPro API", version="1.0.0", description="Restaurant & Bar Management System")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create data directory for file uploads
os.makedirs("data", exist_ok=True)

# Mount static directory
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")

# Serve uploaded files
if os.path.exists("data"):
    app.mount("/data", StaticFiles(directory="data"), name="data")

# Serve the frontend HTML on root path
@app.get("/", include_in_schema=False)
async def serve_frontend():
    index_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../frontend/index.html")
    )
    return FileResponse(index_path)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "GastroPro API is running"}

# Include API routers
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(menu.router, prefix="/api/menu", tags=["menu"])
app.include_router(inventory.router, prefix="/api/inventory", tags=["inventory"])
app.include_router(staff.router, prefix="/api/staff", tags=["staff"])
