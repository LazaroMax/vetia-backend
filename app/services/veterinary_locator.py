import os
from typing import List, Optional, Tuple
from models.db_models import VeterinarioModel
from geopy.geocoders import Nominatim
import time
import math

def calcular_distancia_haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    a = math.sin(delta_lat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distancia = R * c
    return round(distancia, 2)

def obtener_coordenadas_desde_direccion(direccion: str, municipio: str = '', departamento: str = '') -> Optional[Tuple[float, float]]:
    try:
        geolocator = Nominatim(user_agent="vetia_geocoder")
        direccion_completa = direccion
        if municipio:
            direccion_completa += f", {municipio}"
        if departamento:
            direccion_completa += f", {departamento}"
        # respetar rate limit de Nominatim
        time.sleep(1)
        location = geolocator.geocode(direccion_completa, timeout=10)
        if location:
            return (location.latitude, location.longitude)
        return None
    except Exception:
        return None

# Supabase optional client
try:
    from supabase import create_client
except Exception:
    create_client = None

def _get_supabase_client():
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY')
    if not SUPABASE_URL or not SUPABASE_KEY or create_client is None:
        return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def buscar_veterinarios_cercanos_from_db(dueno, radio_km: float = 10, limite: int = 10) -> List[dict]:
    client = _get_supabase_client()
    vets = []
    if client:
        try:
            resp = client.table('veterinarios').select('*').execute()
            vets = resp.data or []
        except Exception:
            vets = []

    if not vets:
        vets = [
            {"id":"1","nombre":"VetCare Express","telefono":"+50255551234","direccion":"Av. Central 123, Ciudad","latitud":14.6308,"longitud":-90.5138,"especialidades":["general","vacunacion"],"calificacion":4.5,"atiende_emergencias":True},
            {"id":"2","nombre":"Clínica San Juan","telefono":"+50255558899","direccion":"Calle 5, Zona 3","latitud":14.5987,"longitud":-90.5145,"especialidades":["general","odontologia"],"calificacion":4.2,"atiende_emergencias":False},
            {"id":"3","nombre":"Animal Health Center","telefono":"+50255557711","direccion":"Boulevard Libertad","latitud":14.6012,"longitud":-90.4987,"especialidades":["cirugia","emergencias"],"calificacion":4.7,"atiende_emergencias":True},
        ]

    # calcular coordenadas del dueño si no vienen y si trae direccion
    if hasattr(dueno, 'direccion') and (not getattr(dueno, 'latitud', None) or not getattr(dueno, 'longitud', None)):
        coords = None
        if dueno.direccion:
            coords = obtener_coordenadas_desde_direccion(dueno.direccion, getattr(dueno, 'municipio', ''), getattr(dueno, 'departamento', ''))
        if coords:
            dueno.latitud, dueno.longitud = coords

    lat0 = getattr(dueno, 'latitud', 14.6349) or 14.6349
    lon0 = getattr(dueno, 'longitud', -90.5069) or -90.5069

    results = []
    for v in vets:
        dist = calcular_distancia_haversine(lat0, lon0, v.get('latitud') or v.get('lat') or 0, v.get('longitud') or v.get('lng') or 0)
        v['distancia_km'] = dist
        if dist <= radio_km:
            results.append(v)

    results.sort(key=lambda x: x['distancia_km'])
    return results[:limite]
