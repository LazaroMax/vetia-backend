# backend/app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.veterinary_locator import buscar_veterinarios_cercanos_from_db


import os

app = FastAPI(title="VetIA MCP - API")

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]
# Add your Vercel domain in production, e.g. "https://your-app.vercel.app"
if os.getenv("FRONTEND_URL"):
    origins.append(os.getenv("FRONTEND_URL"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET","POST","OPTIONS"],
    allow_headers=["*"],
)

class DuenoModel(BaseModel):
    direccion: str | None = None
    municipio: str | None = None
    departamento: str | None = None
    latitud: float | None = None
    longitud: float | None = None

@app.post("/api/v1/vets")
async def api_vets(dueno: DuenoModel, radio_km: float = 10.0, limite: int = 10):
    try:
        vets = buscar_veterinarios_cercanos_from_db(dueno, radio_km=radio_km, limite=limite)
        return vets
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
