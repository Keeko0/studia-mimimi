import csv
from database import engine, Base, SessionLocal, MovieModel, LinkModel, RatingModel, TagModel

# 1. Tworzenie tabel w bazie danych (jeśli nie istnieją)
Base.metadata.create_all(bind=engine)

def load_csv_to_db(filename, model_class):
    session = SessionLocal()
    print(f"Ładowanie danych z {filename}...")
    try:
        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            batch = []
            for row in reader:
                # Specjalna obsługa dla LinkModel (puste tmdbId)
                if model_class == LinkModel:
                    if not row.get('tmdbId'):
                        row['tmdbId'] = None
                
                # Tworzymy obiekt modelu SQL
                db_obj = model_class(**row)
                batch.append(db_obj)
            
            # Bulk save objects (szybsze niż dodawanie pojedynczo)
            session.add_all(batch)
            session.commit()
            print(f"Sukces! Załadowano {len(batch)} rekordów do tabeli {model_class.__tablename__}.")
            
    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku {filename}")
    except Exception as e:
        print(f"Wystąpił błąd: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    # Uruchamiamy import dla wszystkich plików
    # Upewnij się, że pliki CSV są w tym samym folderze!
    load_csv_to_db('movies.csv', MovieModel)
    load_csv_to_db('links.csv', LinkModel)
    load_csv_to_db('ratings.csv', RatingModel)
    load_csv_to_db('tags.csv', TagModel)
    print("Zakończono importowanie bazy danych.")