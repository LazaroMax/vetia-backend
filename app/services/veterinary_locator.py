# backend/app/services/veterinary_locator.py
import os
from typing import List
from models.db_models import VeterinarioModel

# Optional Supabase support
try:
    from supabase import create_client, Client as SupabaseClient
except Exception:
    SupabaseClient = None
    create_client = None


def calcular_distancia_haversine(lat1, lon1, lat2, lon2):
    import math
    R = 6371.0
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    a = math.sin(delta_lat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distancia = R * c
    return round(distancia, 2)


def _get_supabase_client():
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not SUPABASE_URL or not SUPABASE_KEY or create_client is None:
        return None

    return create_client(SUPABASE_URL, SUPABASE_KEY)


def buscar_veterinarios_cercanos_from_db(dueno, radio_km=10, limite=10):
    """Fetches vets from Supabase if configured; otherwise returns static list."""
    
    client = _get_supabase_client()
    vets = []

    if client:
        try:
            resp = client.table("veterinarios").select("*").execute()
            vets = resp.data or []
        except Exception:
            vets = []

    if not vets:
        vets = [
            {"id":"1","nombre":"VetCare Express","telefono":"5555-1234","direccion":"Av. Central 123","latitud":14.63,"longitud":-90.51,"especialidades":["general"],"calificacion":4.5,"atiende_emergencias":True},
            {"id":"2","nombre":"Clínica San Juan","telefono":"5555-8899","direccion":"Calle 5","latitud":14.6,"longitud":-90.52,"especialidades":["general"],"calificacion":4.2,"atiende_emergencias":False},
            {"id":"3","nombre":"Animal Health Center","telefono":"5555-7711","direccion":"Boulevard Libertad","latitud":14.61,"longitud":-90.50,"especialidades":["cirugia"],"calificacion":4.7,"atiende_emergencias":True},
        ]

    lat0 = dueno.latitud or 14.6349
    lon0 = dueno.longitud or -90.5069

    results = []

    for v in vets:
        dist = calcular_distancia_haversine(lat0, lon0, v.get("latitud", 0), v.get("longitud", 0))
        v["distancia_km"] = dist
        if dist <= radio_km:
            results.append(v)

    results.sort(key=lambda x: x["distancia_km"])

    return results[:limite]
