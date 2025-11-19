import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from main import app, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture()
def test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

#tests
def test_create_movie(test_db):
    response = client.post(
        "/movies",
        json={"movieId": "999", "title": "Test Movie", "genres": "Test Genre"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Movie"
    assert data["movieId"] == "999"

def test_read_movie(test_db):
    client.post("/movies", json={"movieId": "888", "title": "Read Me", "genres": "Drama"})
    response = client.get("/movies/888")
    assert response.status_code == 200
    assert response.json()["title"] == "Read Me"

def test_read_movie_not_found(test_db):
    response = client.get("/movies/missing")
    assert response.status_code == 404

def test_update_movie(test_db):
    client.post("/movies", json={"movieId": "777", "title": "Old Title", "genres": "Drama"})
    response = client.put(
        "/movies/777",
        json={"title": "New Title", "genres": "Comedy"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"

def test_delete_movie(test_db):
    client.post("/movies", json={"movieId": "666", "title": "Del Me", "genres": "Horror"})
    response = client.delete("/movies/666")
    assert response.status_code == 204
    assert client.get("/movies/666").status_code == 404

def test_create_link(test_db):
    response = client.post(
        "/links",
        json={"movieId": "100", "imdbId": "tt12345", "tmdbId": "54321"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["movieId"] == "100"
    assert data["imdbId"] == "tt12345"

def test_read_link(test_db):
    client.post("/links", json={"movieId": "101", "imdbId": "tt101", "tmdbId": "101"})
    response = client.get("/links/101")
    assert response.status_code == 200
    assert response.json()["imdbId"] == "tt101"

def test_update_link(test_db):
    client.post("/links", json={"movieId": "200", "imdbId": "ttold", "tmdbId": "111"})
    response = client.put(
        "/links/200",
        json={"imdbId": "ttnew", "tmdbId": "222"}
    )
    assert response.status_code == 200
    assert response.json()["imdbId"] == "ttnew"

def test_delete_link(test_db):
    client.post("/links", json={"movieId": "300", "imdbId": "ttdel", "tmdbId": "333"})
    response = client.delete("/links/300")
    assert response.status_code == 204
    assert client.get("/links/300").status_code == 404

def test_create_rating(test_db):
    response = client.post(
        "/ratings",
        json={"userId": "u1", "movieId": "m1", "rating": 5.0, "timestamp": "999"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["rating"] == 5.0
    assert "id" in data

def test_read_rating(test_db):
    client.post("/ratings", json={"userId": "u1", "movieId": "m1", "rating": 4.0, "timestamp": "888"})
    response = client.get("/ratings/1")
    assert response.status_code == 200
    assert response.json()["rating"] == 4.0

def test_update_rating(test_db):
    client.post("/ratings", json={"userId": "u1", "movieId": "m1", "rating": 2.0, "timestamp": "777"})
    response = client.put(
        "/ratings/1",
        json={"userId": "u1", "movieId": "m1", "rating": 5.0, "timestamp": "777"}
    )
    assert response.status_code == 200
    assert response.json()["rating"] == 5.0

def test_delete_rating(test_db):
    client.post("/ratings", json={"userId": "u1", "movieId": "m1", "rating": 3.0, "timestamp": "666"})
    response = client.delete("/ratings/1")
    assert response.status_code == 204
    assert client.get("/ratings/1").status_code == 404

def test_create_tag(test_db):
    response = client.post(
        "/tags",
        json={"userId": "1", "movieId": "1", "tag": "funny", "timestamp": "123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["tag"] == "funny"
    assert "id" in data

def test_read_tag(test_db):
    client.post("/tags", json={"userId": "1", "movieId": "1", "tag": "drama", "timestamp": "456"})
    response = client.get("/tags/1")
    assert response.status_code == 200
    assert response.json()["tag"] == "drama"

def test_update_tag(test_db):
    client.post("/tags", json={"userId": "1", "movieId": "1", "tag": "bad", "timestamp": "789"})
    response = client.put(
        "/tags/1",
        json={"userId": "1", "movieId": "1", "tag": "good", "timestamp": "789"}
    )
    assert response.status_code == 200
    assert response.json()["tag"] == "good"

def test_delete_tag(test_db):
    client.post("/tags", json={"userId": "1", "movieId": "1", "tag": "delete_me", "timestamp": "000"})
    response = client.delete("/tags/1")
    assert response.status_code == 204
    assert client.get("/tags/1").status_code == 404