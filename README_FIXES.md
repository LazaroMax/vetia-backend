VetIA backend - fixed package layout and endpoints
- Ensured app/main.py contains both GET /veterinarias/cercanas and POST /api/v1/vets
- Separated models/db_models.py and services/veterinary_locator.py
- Updated Dockerfile to honor $PORT (default 8000) so frontend and platform match ports
- Updated requirements.txt with required packages
- Added __init__.py files where needed

How to run locally:
1) python -m venv venv
2) venv\Scripts\activate  (Windows) or source venv/bin/activate (Linux/Mac)
3) pip install -r requirements.txt
4) uvicorn app.main:app --reload --port 8000
