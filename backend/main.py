from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import uvicorn

from routers import orders, menu, inventory, staff
from routers import sales_analytics, staff_management, system_settings

app = FastAPI(title="GastroPro API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory (e.g., /static/css, /static/js)
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")


# Serve the frontend HTML on root path
@app.get("/", include_in_schema=False)
async def serve_frontend():
    index_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../frontend/index.html")
    )
    return FileResponse(index_path)


# Include your routers
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(menu.router, prefix="/api/menu", tags=["menu"])
app.include_router(inventory.router, prefix="/api/inventory", tags=["inventory"])
app.include_router(staff.router, prefix="/api/staff", tags=["staff"])

# Include analytics, management and system routes
app.include_router(sales_analytics.router)
app.include_router(staff_management.router)
app.include_router(system_settings.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
