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

#testowa baza danych w ramie
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#override db na fake'a
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

#zaleznosc
app.dependency_overrides[get_db] = override_get_db

#test client
client = TestClient(app)

#robienie tabel
@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

#TESTY
def test_create_result():
    #enpoint POST /results - zapisywanie danych
    payload = {
        "image_url":"https://media.istockphoto.com/id/1977329451/photo/diverse-businesspeople-smiling-while-standing-arm-in-arm-in-an-office.jpg?s=612x612&w=0&k=20&c=FvQFfKBc7iAUPz48tdU_hzvTPCdGSntmdlceDeUuKRs=",
        "person_count": 10
    }
    
    response = client.post("/results", json=payload)
    
    #check
    assert response.status_code == 200
    data = response.json()
    assert data["image_url"] == "https://media.istockphoto.com/id/1977329451/photo/diverse-businesspeople-smiling-while-standing-arm-in-arm-in-an-office.jpg?s=612x612&w=0&k=20&c=FvQFfKBc7iAUPz48tdU_hzvTPCdGSntmdlceDeUuKRs="
    assert data["person_count"] == 10
    assert "id" in data

def test_read_results():
    #endpoint GET /results - zwracanie danych
    #dodajemy 2 wyniki
    client.post("/results", json={"image_url": "http://a.com", "person_count": 1})
    client.post("/results", json={"image_url": "http://b.com", "person_count": 2})

    response = client.get("/results")
    
    #sprawdzamy czy sa te 2 wyniki
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["person_count"] == 1
    assert data[1]["person_count"] == 2