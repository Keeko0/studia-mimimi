from sqlalchemy import create_engine, Column, String, Float, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./movies.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default="ROLE_USER")

class MovieModel(Base):
    __tablename__ = "movies"
    
    movieId = Column(String, primary_key=True, index=True)
    title = Column(String)
    genres = Column(String)

class LinkModel(Base):
    __tablename__ = "links"
    
    movieId = Column(String, primary_key=True, index=True)
    imdbId = Column(String)
    tmdbId = Column(String, nullable=True)

class RatingModel(Base):
    __tablename__ = "ratings"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    userId = Column(String)
    movieId = Column(String, index=True)
    rating = Column(Float)
    timestamp = Column(String)

class TagModel(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    userId = Column(String)
    movieId = Column(String, index=True)
    tag = Column(String)
    timestamp = Column(String)