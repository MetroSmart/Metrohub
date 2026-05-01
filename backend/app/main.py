from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

import app.models  # noqa: F401 — registra todos los modelos en SQLAlchemy

from app.database import engine, Base
from app.routers import auth, rutas, horarios, choferes, dashboard, conflictos

# ── Instancia principal de FastAPI ────────────
app = FastAPI(
    title="MetroSmart API",
    description="Backend de programación inteligente de horarios "
                "y asignación de choferes para el Metropolitano de Lima",
    version="2.0.0",
)

# ── CORS ──────────────────────────────────────
# Permite que el frontend React se comunique con este backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],  # puerto de Vite (React)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers (módulos de endpoints) ───────────
app.include_router(auth.router,     prefix="/api/auth",     tags=["Autenticación"])
app.include_router(rutas.router,    prefix="/api/rutas",    tags=["Rutas"])
app.include_router(horarios.router, prefix="/api/horarios", tags=["Horarios"])
app.include_router(choferes.router, prefix="/api/choferes", tags=["Choferes"])
app.include_router(dashboard.router,   prefix="/api/dashboard",   tags=["Dashboard"])
app.include_router(conflictos.router,  prefix="/api/conflictos",  tags=["Conflictos"])

# ── Endpoint raíz ─────────────────────────────
@app.get("/")
def root():
    return {
        "sistema": "MetroSmart API",
        "version": "2.0.0",
        "estado": "activo",
        "docs": "/docs"
    }

# ── Health check ──────────────────────────────
@app.get("/health")
def health_check():
    return {"status": "ok"}
