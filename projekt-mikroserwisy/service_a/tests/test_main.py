import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app, get_db
from database import Base

# 1. Tworzymy testową bazę danych w pamięci RAM (znika po testach)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 2. Funkcja, która podmienia oryginalne połączenie do bazy
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# 3. Podmieniamy zależność w naszej aplikacji
app.dependency_overrides[get_db] = override_get_db

# 4. Tworzymy klienta testowego
client = TestClient(app)

# 5. Przygotowanie bazy przed testami (tworzenie tabel)
@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# --- WŁAŚCIWE TESTY ---

def test_create_result():
    """Testuje, czy endpoint POST /results poprawnie zapisuje dane."""
    payload = {
        "image_url": "http://test.com/photo.jpg",
        "person_count": 10
    }
    
    response = client.post("/results", json=payload)
    
    # Asercje (sprawdzenia)
    assert response.status_code == 200
    data = response.json()
    assert data["image_url"] == "http://test.com/photo.jpg"
    assert data["person_count"] == 10
    assert "id" in data  # Sprawdzamy, czy baza nadała ID

def test_read_results():
    """Testuje, czy endpoint GET /results zwraca to, co dodaliśmy."""
    # Najpierw dodajemy 2 wyniki
    client.post("/results", json={"image_url": "http://a.com", "person_count": 1})
    client.post("/results", json={"image_url": "http://b.com", "person_count": 2})

    # Teraz pobieramy listę
    response = client.get("/results")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2  # Powinny być 2 elementy
    assert data[0]["person_count"] == 1
    assert data[1]["person_count"] == 2