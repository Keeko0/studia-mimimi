import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import bcrypt

from database import Base, User
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
    
    hashed = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode('utf-8')
    admin = User(username="admin", password_hash=hashed, role="ROLE_ADMIN")
    db.add(admin)
    db.commit()
    
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

def get_auth_headers():
    response = client.post("/login", json={"username": "admin", "password": "admin123"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_login_success(test_db):
    response = client.post("/login", json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_failure(test_db):
    response = client.post("/login", json={"username": "admin", "password": "wrongpassword"})
    assert response.status_code == 401

def test_create_user_as_admin(test_db):
    auth_headers = get_auth_headers()
    response = client.post(
        "/users", 
        json={"username": "newuser", "password": "pw", "role": "ROLE_USER"}, 
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["msg"] == "User created successfully"

def test_create_user_no_auth(test_db):
    response = client.post("/users", json={"username": "hacker", "password": "pw"})
    assert response.status_code == 403 

def test_user_details(test_db):
    auth_headers = get_auth_headers()
    response = client.get("/user_details", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "admin"
    assert response.json()["role"] == "ROLE_ADMIN"

def test_create_movie(test_db):
    auth_headers = get_auth_headers()
    response = client.post(
        "/movies",
        json={"movieId": "999", "title": "Test Movie", "genres": "Test Genre"},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Movie"
    assert data["movieId"] == "999"

def test_read_movie(test_db):
    auth_headers = get_auth_headers()
    client.post("/movies", json={"movieId": "888", "title": "Read Me", "genres": "Drama"}, headers=auth_headers)
    
    response = client.get("/movies/888", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Read Me"

def test_read_movie_not_found(test_db):
    auth_headers = get_auth_headers()
    response = client.get("/movies/missing", headers=auth_headers)
    assert response.status_code == 404

def test_update_movie(test_db):
    auth_headers = get_auth_headers()
    client.post("/movies", json={"movieId": "777", "title": "Old Title", "genres": "Drama"}, headers=auth_headers)
    
    response = client.put(
        "/movies/777",
        json={"title": "New Title", "genres": "Comedy"},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"

def test_delete_movie(test_db):
    auth_headers = get_auth_headers()
    client.post("/movies", json={"movieId": "666", "title": "Del Me", "genres": "Horror"}, headers=auth_headers)
    
    response = client.delete("/movies/666", headers=auth_headers)
    assert response.status_code == 204
    
    assert client.get("/movies/666", headers=auth_headers).status_code == 404

def test_create_link(test_db):
    auth_headers = get_auth_headers()
    response = client.post(
        "/links",
        json={"movieId": "100", "imdbId": "tt12345", "tmdbId": "54321"},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["movieId"] == "100"
    assert data["imdbId"] == "tt12345"

def test_read_link(test_db):
    auth_headers = get_auth_headers()
    client.post("/links", json={"movieId": "101", "imdbId": "tt101", "tmdbId": "101"}, headers=auth_headers)
    
    response = client.get("/links/101", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["imdbId"] == "tt101"

def test_update_link(test_db):
    auth_headers = get_auth_headers()
    client.post("/links", json={"movieId": "200", "imdbId": "ttold", "tmdbId": "111"}, headers=auth_headers)
    
    response = client.put(
        "/links/200",
        json={"imdbId": "ttnew", "tmdbId": "222"},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["imdbId"] == "ttnew"

def test_delete_link(test_db):
    auth_headers = get_auth_headers()
    client.post("/links", json={"movieId": "300", "imdbId": "ttdel", "tmdbId": "333"}, headers=auth_headers)
    
    response = client.delete("/links/300", headers=auth_headers)
    assert response.status_code == 204
    assert client.get("/links/300", headers=auth_headers).status_code == 404

def test_create_rating(test_db):
    auth_headers = get_auth_headers()
    response = client.post(
        "/ratings",
        json={"userId": "u1", "movieId": "m1", "rating": 5.0, "timestamp": "999"},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["rating"] == 5.0
    assert "id" in data

def test_read_rating(test_db):
    auth_headers = get_auth_headers()
    client.post("/ratings", json={"userId": "u1", "movieId": "m1", "rating": 4.0, "timestamp": "888"}, headers=auth_headers)
    
    response = client.get("/ratings/1", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["rating"] == 4.0

def test_update_rating(test_db):
    auth_headers = get_auth_headers()
    client.post("/ratings", json={"userId": "u1", "movieId": "m1", "rating": 2.0, "timestamp": "777"}, headers=auth_headers)
    
    response = client.put(
        "/ratings/1",
        json={"userId": "u1", "movieId": "m1", "rating": 5.0, "timestamp": "777"},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["rating"] == 5.0

def test_delete_rating(test_db):
    auth_headers = get_auth_headers()
    client.post("/ratings", json={"userId": "u1", "movieId": "m1", "rating": 3.0, "timestamp": "666"}, headers=auth_headers)
    
    response = client.delete("/ratings/1", headers=auth_headers)
    assert response.status_code == 204
    assert client.get("/ratings/1", headers=auth_headers).status_code == 404

def test_create_tag(test_db):
    auth_headers = get_auth_headers()
    response = client.post(
        "/tags",
        json={"userId": "1", "movieId": "1", "tag": "funny", "timestamp": "123"},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["tag"] == "funny"
    assert "id" in data

def test_read_tag(test_db):
    auth_headers = get_auth_headers()
    client.post("/tags", json={"userId": "1", "movieId": "1", "tag": "drama", "timestamp": "456"}, headers=auth_headers)
    
    response = client.get("/tags/1", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["tag"] == "drama"

def test_update_tag(test_db):
    auth_headers = get_auth_headers()
    client.post("/tags", json={"userId": "1", "movieId": "1", "tag": "bad", "timestamp": "789"}, headers=auth_headers)
    
    response = client.put(
        "/tags/1",
        json={"userId": "1", "movieId": "1", "tag": "good", "timestamp": "789"},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["tag"] == "good"

def test_delete_tag(test_db):
    auth_headers = get_auth_headers()
    client.post("/tags", json={"userId": "1", "movieId": "1", "tag": "delete_me", "timestamp": "000"}, headers=auth_headers)
    
    response = client.delete("/tags/1", headers=auth_headers)
    assert response.status_code == 204
    assert client.get("/tags/1", headers=auth_headers).status_code == 404