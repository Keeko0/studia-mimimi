from fastapi import FastAPI, Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
import bcrypt

from database import SessionLocal, MovieModel, LinkModel, RatingModel, TagModel, User, engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

SECRET_KEY = "super_tajny_klucz_zmien_go_w_produkcji"
ALGORITHM = "HS256"
security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class LoginData(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "ROLE_USER"

class MovieBase(BaseModel):
    title: str
    genres: str

class MovieCreate(MovieBase):
    movieId: str

class Movie(MovieBase):
    movieId: str
    class Config:
        from_attributes = True

class LinkBase(BaseModel):
    imdbId: str
    tmdbId: Optional[str] = None

class LinkCreate(LinkBase):
    movieId: str

class Link(LinkBase):
    movieId: str
    class Config:
        from_attributes = True

class RatingBase(BaseModel):
    userId: str
    movieId: str
    rating: float
    timestamp: str

class RatingCreate(RatingBase):
    pass

class Rating(RatingBase):
    id: int
    class Config:
        from_attributes = True

class TagBase(BaseModel):
    userId: str
    movieId: str
    tag: str
    timestamp: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int
    class Config:
        from_attributes = True


def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def get_current_user_payload(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def verify_admin_role(payload: dict = Depends(get_current_user_payload)):
    if payload.get("role") != "ROLE_ADMIN":
        raise HTTPException(status_code=403, detail="Admin role required")
    return payload


@app.post("/login")
def login(data: LoginData, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    payload = {
        "sub": user.username,
        "role": user.role,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(
    new_user: UserCreate, 
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_admin_role)
):
    if db.query(User).filter(User.username == new_user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_pw = get_password_hash(new_user.password)
    db_user = User(
        username=new_user.username, 
        password_hash=hashed_pw, 
        role=new_user.role
    )
    db.add(db_user)
    db.commit()
    return {"msg": "User created successfully"}

@app.get("/user_details")
def get_user_details(payload: dict = Depends(get_current_user_payload)):
    return {
        "username": payload.get("sub"),
        "role": payload.get("role"),
        "expires_at": payload.get("exp")
    }

@app.post("/setup_admin")
def setup_admin(db: Session = Depends(get_db)):
    if not db.query(User).filter(User.username == "admin").first():
        admin = User(username="admin", password_hash=get_password_hash("admin123"), role="ROLE_ADMIN")
        db.add(admin)
        db.commit()
        return {"msg": "Admin created"}
    return {"msg": "Admin already exists"}


@app.get("/")
def read_root():
    return {"hello": "world"}

# --- MOVIES ---
@app.get("/movies", response_model=List[Movie], dependencies=[Depends(get_current_user_payload)])
def get_movies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(MovieModel).offset(skip).limit(limit).all()

@app.get("/movies/{movie_id}", response_model=Movie, dependencies=[Depends(get_current_user_payload)])
def get_movie(movie_id: str, db: Session = Depends(get_db)):
    db_movie = db.query(MovieModel).filter(MovieModel.movieId == movie_id).first()
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return db_movie

@app.post("/movies", response_model=Movie, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user_payload)])
def create_movie(movie: MovieCreate, db: Session = Depends(get_db)):
    existing_movie = db.query(MovieModel).filter(MovieModel.movieId == movie.movieId).first()
    if existing_movie:
        raise HTTPException(status_code=400, detail="Movie with this ID already exists")
    
    new_movie = MovieModel(**movie.dict())
    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)
    return new_movie

@app.put("/movies/{movie_id}", response_model=Movie, dependencies=[Depends(get_current_user_payload)])
def update_movie(movie_id: str, movie_update: MovieBase, db: Session = Depends(get_db)):
    db_movie = db.query(MovieModel).filter(MovieModel.movieId == movie_id).first()
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    db_movie.title = movie_update.title
    db_movie.genres = movie_update.genres
    db.commit()
    db.refresh(db_movie)
    return db_movie

@app.delete("/movies/{movie_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_user_payload)])
def delete_movie(movie_id: str, db: Session = Depends(get_db)):
    db_movie = db.query(MovieModel).filter(MovieModel.movieId == movie_id).first()
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    db.delete(db_movie)
    db.commit()
    return None

# --- LINKS ---
@app.get("/links", response_model=List[Link], dependencies=[Depends(get_current_user_payload)])
def get_links(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(LinkModel).offset(skip).limit(limit).all()

@app.get("/links/{movie_id}", response_model=Link, dependencies=[Depends(get_current_user_payload)])
def get_link(movie_id: str, db: Session = Depends(get_db)):
    db_link = db.query(LinkModel).filter(LinkModel.movieId == movie_id).first()
    if db_link is None:
        raise HTTPException(status_code=404, detail="Links not found for this movie")
    return db_link

@app.post("/links", response_model=Link, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user_payload)])
def create_link(link: LinkCreate, db: Session = Depends(get_db)):
    existing_link = db.query(LinkModel).filter(LinkModel.movieId == link.movieId).first()
    if existing_link:
        raise HTTPException(status_code=400, detail="Links for this movie already exist")
    
    new_link = LinkModel(**link.dict())
    db.add(new_link)
    db.commit()
    db.refresh(new_link)
    return new_link

@app.put("/links/{movie_id}", response_model=Link, dependencies=[Depends(get_current_user_payload)])
def update_link(movie_id: str, link_update: LinkBase, db: Session = Depends(get_db)):
    db_link = db.query(LinkModel).filter(LinkModel.movieId == movie_id).first()
    if db_link is None:
        raise HTTPException(status_code=404, detail="Links not found")
    
    db_link.imdbId = link_update.imdbId
    db_link.tmdbId = link_update.tmdbId
    db.commit()
    db.refresh(db_link)
    return db_link

@app.delete("/links/{movie_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_user_payload)])
def delete_link(movie_id: str, db: Session = Depends(get_db)):
    db_link = db.query(LinkModel).filter(LinkModel.movieId == movie_id).first()
    if db_link is None:
        raise HTTPException(status_code=404, detail="Links not found")
    
    db.delete(db_link)
    db.commit()
    return None

# --- RATINGS ---
@app.get("/ratings", response_model=List[Rating], dependencies=[Depends(get_current_user_payload)])
def get_ratings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(RatingModel).offset(skip).limit(limit).all()

@app.get("/ratings/{rating_id}", response_model=Rating, dependencies=[Depends(get_current_user_payload)])
def get_rating(rating_id: int, db: Session = Depends(get_db)):
    db_rating = db.query(RatingModel).filter(RatingModel.id == rating_id).first()
    if db_rating is None:
        raise HTTPException(status_code=404, detail="Rating not found")
    return db_rating

@app.post("/ratings", response_model=Rating, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user_payload)])
def create_rating(rating: RatingCreate, db: Session = Depends(get_db)):
    new_rating = RatingModel(**rating.dict())
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    return new_rating

@app.put("/ratings/{rating_id}", response_model=Rating, dependencies=[Depends(get_current_user_payload)])
def update_rating(rating_id: int, rating_update: RatingCreate, db: Session = Depends(get_db)):
    db_rating = db.query(RatingModel).filter(RatingModel.id == rating_id).first()
    if db_rating is None:
        raise HTTPException(status_code=404, detail="Rating not found")
    
    for key, value in rating_update.dict().items():
        setattr(db_rating, key, value)
    
    db.commit()
    db.refresh(db_rating)
    return db_rating

@app.delete("/ratings/{rating_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_user_payload)])
def delete_rating(rating_id: int, db: Session = Depends(get_db)):
    db_rating = db.query(RatingModel).filter(RatingModel.id == rating_id).first()
    if db_rating is None:
        raise HTTPException(status_code=404, detail="Rating not found")
    
    db.delete(db_rating)
    db.commit()
    return None

# --- TAGS ---
@app.get("/tags", response_model=List[Tag], dependencies=[Depends(get_current_user_payload)])
def get_tags(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(TagModel).offset(skip).limit(limit).all()

@app.get("/tags/{tag_id}", response_model=Tag, dependencies=[Depends(get_current_user_payload)])
def get_tag(tag_id: int, db: Session = Depends(get_db)):
    db_tag = db.query(TagModel).filter(TagModel.id == tag_id).first()
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return db_tag

@app.post("/tags", response_model=Tag, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user_payload)])
def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    new_tag = TagModel(**tag.dict())
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    return new_tag

@app.put("/tags/{tag_id}", response_model=Tag, dependencies=[Depends(get_current_user_payload)])
def update_tag(tag_id: int, tag_update: TagCreate, db: Session = Depends(get_db)):
    db_tag = db.query(TagModel).filter(TagModel.id == tag_id).first()
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    for key, value in tag_update.dict().items():
        setattr(db_tag, key, value)
    
    db.commit()
    db.refresh(db_tag)
    return db_tag

@app.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_user_payload)])
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    db_tag = db.query(TagModel).filter(TagModel.id == tag_id).first()
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    db.delete(db_tag)
    db.commit()
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)