# main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

# Importujemy rzeczy z naszego pliku database.py
from database import SessionLocal, MovieModel, LinkModel, RatingModel, TagModel

app = FastAPI()

# --- Dependency ---
# Ta funkcja tworzy sesję bazy danych dla każdego requestu i zamyka ją po zakończeniu
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Modele Pydantic (Schematy odpowiedzi API) ---
# To zostaje bez zmian - definiuje jak wygląda JSON
class MovieSchema(BaseModel):
    movieId: str 
    title: str
    genres: str
    class Config:
        from_attributes = True # Ważne dla ORM! (dawniej orm_mode = True)

class LinkSchema(BaseModel):
    movieId: str
    imdbId: str
    tmdbId: Optional[str] = None
    class Config:
        from_attributes = True

class RatingSchema(BaseModel):
    userId: str
    movieId: str
    rating: float
    timestamp: str
    class Config:
        from_attributes = True

class TagSchema(BaseModel):
    userId: str
    movieId: str
    tag: str
    timestamp: str
    class Config:
        from_attributes = True

# --- Endpointy ---

@app.get("/")
def read_root():
    return {"hello": "world"}

# Wstrzykujemy sesję bazy danych (db: Session = Depends(get_db))

@app.get("/movies", response_model=List[MovieSchema])
def get_movies(db: Session = Depends(get_db)):
    # Pobieramy dane SQL: SELECT * FROM movies
    return db.query(MovieModel).all()

@app.get("/links", response_model=List[LinkSchema])
def get_links(db: Session = Depends(get_db)):
    return db.query(LinkModel).all()

@app.get("/ratings", response_model=List[RatingSchema])
def get_ratings(db: Session = Depends(get_db)):
    # Limitujemy do 100, bo ratingów może być bardzo dużo i zamuli przeglądarkę
    return db.query(RatingModel).limit(100).all()

@app.get("/tags", response_model=List[TagSchema])
def get_tags(db: Session = Depends(get_db)):
    return db.query(TagModel).all()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)