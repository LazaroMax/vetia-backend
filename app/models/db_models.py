# backend/app/models/db_models.py
from typing import List, Optional
from pydantic import BaseModel

class VeterinarioModel(BaseModel):
    id: str
    nombre: str
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    especialidades: Optional[List[str]] = []
    calificacion: Optional[float] = None
    atiende_emergencias: Optional[bool] = False
    horario: Optional[dict] = {}
