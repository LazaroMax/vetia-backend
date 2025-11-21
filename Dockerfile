FROM python:3.11-slim

WORKDIR /app

# Copiar requirements primero
COPY ./requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Copiar el resto del código
COPY ./app /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
