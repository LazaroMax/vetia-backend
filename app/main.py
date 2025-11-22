# backend/app/main.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from app.services.veterinary_locator import buscar_veterinarios_cercanos_from_db


app = FastAPI(
    title="VetIA MCP - API",
    description="API para localizar veterinarias cercanas según ubicación del usuario.",
    version="0.1.0"
)

# CORS
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]

if os.getenv("FRONTEND_URL"):
    origins.append(os.getenv("FRONTEND_URL"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# MODELO DE ENTRADA DEL CLIENTE (lat/lon)
# -----------------------------
class UbicacionUsuario(BaseModel):
    latitud: float
    longitud: float

# -----------------------------
# NUEVO ENDPOINT PRINCIPAL (GET)
# -----------------------------
@app.get("/veterinarias/cercanas", tags=["Veterinarias"])
async def obtener_veterinarias_cercanas(
    latitud: float = Query(..., description="Latitud del usuario"),
    longitud: float = Query(..., description="Longitud del usuario"),
    radio_km: float = Query(10.0, description="Radio de búsqueda en kilómetros"),
    limite: int = Query(10, description="Cantidad máxima de resultados")
):
    try:
        usuario = UbicacionUsuario(latitud=latitud, longitud=longitud)
        veterinarios = buscar_veterinarios_cercanos_from_db(
            usuario, radio_km=radio_km, limite=limite
        )
        return veterinarios
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------------------------------
# ENDPOINT OPCIONAL (por compatibilidad con tu app) - recibe direccion (POST)
# -------------------------------------------------
class DuenoModel(BaseModel):
    direccion: str | None = None
    municipio: str | None = None
    departamento: str | None = None
    latitud: float | None = None
    longitud: float | None = None

@app.post("/api/v1/vets", tags=["Compatibilidad API antigua"])
async def api_vets(dueno: DuenoModel, radio_km: float = 10.0, limite: int = 10):
    try:
        vets = buscar_veterinarios_cercanos_from_db(dueno, radio_km=radio_km, limite=limite)
        return vets
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
