# Python-Basis-Image verwenden
FROM python:3.11-slim

# Arbeitsverzeichnis im Container
WORKDIR /app

# Requirements kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App-Dateien in Container kopieren
COPY . .

# Port für Gunicorn
EXPOSE 5000

# Environment-Variablen setzen
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Startbefehl für die App
CMD ["gunicorn", "-b", "0.0.0.0:5000", "run:app"]