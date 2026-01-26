from fastapi import FastAPI 
from routes import auth_routes ,farmer_routes , client_routes ,worker_routes , admin_routes
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5500",  # Common for VS Code Live Server
    "http://127.0.0.1:5500",
    "http://localhost:3000",  # Common for React/Vue
    # Add any other origins you use here
]
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Allow specific origins
    allow_credentials=True,
    allow_methods=["*"],              # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],              # Allow all headers
)
app.include_router(auth_routes.router,prefix="/auth", tags=["Authentication"])
app.include_router(admin_routes.router,prefix="/admin",  tags=["admin"])
app.include_router(farmer_routes.router,prefix="/farmer",  tags=["farmer"])
app.include_router(worker_routes.router,prefix="/worker",  tags=["worker"])
app.include_router(client_routes.router,  tags=["client"])






