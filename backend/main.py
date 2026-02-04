from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import db
from routers import auth, schemes, admin, chat, info, applications
import os

app = FastAPI(title="Kanthalloor Digital Governance Platform")

# CORS Setup
origins = [
    "http://localhost:3000", 
    "http://localhost:8000",
    "http://localhost:8045",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8045",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:5501",
    "http://localhost:5501",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Includes
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(schemes.router, prefix="/schemes", tags=["Schemes"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(info.router, prefix="/info", tags=["Info"])
app.include_router(applications.router, prefix="/applications", tags=["Applications"])

# Mount Static & Frontend (Only if directories exist)
from fastapi.staticfiles import StaticFiles

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_db_client():
    await db.connect_to_database()

@app.on_event("shutdown")
async def shutdown_db_client():
    await db.close_database_connection()

if os.path.exists("../frontend"):
    app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
