from fastapi import FastAPI
from pydantic import BaseModel
import csv
from typing import List, Optional

app = FastAPI()

class Movie(BaseModel):
    movieId: str 
    title: str
    genres: str

class Link(BaseModel):
    movieId: str
    imdbId: str
    tmdbId: Optional[str] = None 

class Rating(BaseModel):
    userId: str
    movieId: str
    rating: float
    timestamp: str

class Tag(BaseModel):
    userId: str
    movieId: str
    tag: str
    timestamp: str

def load_data_from_file(filepath: str, model_class: type[BaseModel]) -> List[BaseModel]:
    data = []
    try:
        with open(filepath, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            for row in csv_reader:
                try:
                    data_object = model_class(**row)
                    data.append(data_object)
                except Exception as e:
                    print(f"Błąd przetwarzania wiersza: {row}. Błąd: {e}")
                    
    except FileNotFoundError:
        print(f"BŁĄD KRYTYCZNY: Nie znaleziono pliku {filepath}.")
    except Exception as e:
        print(f"Wystąpił nieoczekiwany błąd przy wczytywaniu {filepath}: {e}")
        
    return data 

print("Wczytywanie danych z plików CSV...")

all_movies = load_data_from_file('movies.csv', Movie)
all_links = load_data_from_file('links.csv', Link)
all_ratings = load_data_from_file('ratings.csv', Rating)
all_tags = load_data_from_file('tags.csv', Tag)

print("Wczytywanie danych zakończone.")
print(f"Załadowano: {len(all_movies)} filmów, {len(all_links)} linków, {len(all_ratings)} ocen, {len(all_tags)} tagów.")

@app.get("/")
def read_root():
    return {"hello": "world"}

@app.get("/movies", response_model=List[Movie])
def get_movies():
    return all_movies

@app.get("/links", response_model=List[Link])
def get_links():
    return all_links

@app.get("/ratings", response_model=List[Rating])
def get_ratings():
    return all_ratings

@app.get("/tags", response_model=List[Tag])
def get_tags():
    return all_tags

if __name__ == "__main__":
    import uvicorn
    print("Serwer http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
    
#uvicorn main:app --reload