from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from backend.routes import gti, signals, narratives

app = FastAPI(
    title="GEO·INTEL API",
    description="Geopolitical Market Intelligence Backend",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(gti.router, prefix="/api")
app.include_router(signals.router, prefix="/api")
app.include_router(narratives.router, prefix="/api")

@app.get("/")
def root():
    return {"status": "ok", "service": "GEO·INTEL API", "version": "0.1.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}
