from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router
from src.models.db import init_db

app = FastAPI(
    title="Multi-Agent Code Reviewer API",
    description="API for reviewing code using a multi-agent system (Security, Performance, Quality)",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(router)

# Database Initialization
@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Code Reviewer API is running"}
