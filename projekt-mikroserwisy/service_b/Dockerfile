FROM python:3.9-slim

WORKDIR /app

# 1. Instalacja bibliotek systemowych
# ZMIANA: używamy 'libgl1' zamiast 'libgl1-mesa-glx'
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 2. Instalacja zależności Pythonowych
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Kopiowanie kodu
COPY . .

# Komenda startowa
CMD ["python", "worker.py"]