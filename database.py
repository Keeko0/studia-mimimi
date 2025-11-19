from sqlalchemy import create_engine, Column, String, Float, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Konfiguracja połączenia z SQLite
# Plik bazy 'movies.db' utworzy się w tym samym folderze
SQLALCHEMY_DATABASE_URL = "sqlite:///./movies.db"

# check_same_thread=False jest potrzebne tylko dla SQLite w FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 2. Definicja Tabel (Modele SQL)
# To są odwzorowania tabel w bazie danych, NIE modele Pydantic (API)

class MovieModel(Base):
    __tablename__ = "movies"
    
    movieId = Column(String, primary_key=True, index=True)
    title = Column(String)
    genres = Column(String)

class LinkModel(Base):
    __tablename__ = "links"
    
    movieId = Column(String, primary_key=True, index=True)
    imdbId = Column(String)
    tmdbId = Column(String, nullable=True) # nullable=True bo może być puste

class RatingModel(Base):
    __tablename__ = "ratings"
    
    # Dodajemy sztuczne ID jako klucz główny
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