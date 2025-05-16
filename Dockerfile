# Basis-Image
FROM python:3.11-slim

# Arbeitsverzeichnis
WORKDIR /app

# System-Abhängigkeiten für psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Projektdateien kopieren
COPY . .

# Port freigeben
EXPOSE 5000

# Umgebungsvariablen
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Startbefehl
CMD ["gunicorn", "-b", "0.0.0.0:5000", "run:app"]