# Używamy lekkiej wersji Pythona
FROM python:3.9-slim

# Ustawiamy katalog roboczy wewnątrz kontenera
WORKDIR /app

# Kopiujemy plik z bibliotekami i instalujemy je
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiujemy cały kod aplikacji
COPY . .

# Komenda startowa:
# host 0.0.0.0 jest konieczny, aby kontener był dostępny z zewnątrz!
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]