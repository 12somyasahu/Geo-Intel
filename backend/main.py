import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


if not os.environ.get("RENDER"):
    from pathlib import Path
    _env_path = Path(__file__).parent / ".env"
    if _env_path.exists():
        with open(_env_path, "r", encoding="utf-8-sig") as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip()

from backend.routes import gti, signals, narratives, analyze, price, ticker

app = FastAPI(
    title="GEO·INTEL API",
    description="Geopolitical Market Intelligence Backend",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://*.vercel.app",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(gti.router,        prefix="/api")
app.include_router(signals.router,    prefix="/api")
app.include_router(narratives.router, prefix="/api")
app.include_router(analyze.router,    prefix="/api")
app.include_router(price.router,      prefix="/api")
app.include_router(ticker.router,     prefix="/api")

@app.api_route("/", methods=["GET", "HEAD"])
def root():
    return {"status": "ok", "service": "GEO·INTEL API", "version": "0.1.0"}

@app.api_route("/health", methods=["GET", "HEAD"])
def health():
    return {"status": "healthy"}