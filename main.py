from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from database import SessionLocal, MovieModel, LinkModel, RatingModel, TagModel

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class MovieSchema(BaseModel):
    movieId: str 
    title: str
    genres: str
    class Config:
        from_attributes = True

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


@app.get("/")
def read_root():
    return {"hello": "world"}

@app.get("/movies", response_model=List[MovieSchema])
def get_movies(db: Session = Depends(get_db)):
    return db.query(MovieModel).all()

@app.get("/links", response_model=List[LinkSchema])
def get_links(db: Session = Depends(get_db)):
    return db.query(LinkModel).all()

@app.get("/ratings", response_model=List[RatingSchema])
def get_ratings(db: Session = Depends(get_db)):
    return db.query(RatingModel).limit(100).all()

@app.get("/tags", response_model=List[TagSchema])
def get_tags(db: Session = Depends(get_db)):
    return db.query(TagModel).all()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)