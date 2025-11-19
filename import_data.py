import csv
from database import engine, Base, SessionLocal, MovieModel, LinkModel, RatingModel, TagModel

Base.metadata.create_all(bind=engine)

def load_csv_to_db(filename, model_class):
    session = SessionLocal()
    print(f"Ładowanie danych z {filename}...")
    try:
        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            batch = []
            for row in reader:
                if model_class == LinkModel:
                    if not row.get('tmdbId'):
                        row['tmdbId'] = None
                
                db_obj = model_class(**row)
                batch.append(db_obj)
            
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
    load_csv_to_db('movies.csv', MovieModel)
    load_csv_to_db('links.csv', LinkModel)
    load_csv_to_db('ratings.csv', RatingModel)
    load_csv_to_db('tags.csv', TagModel)
    print("Zakończono importowanie bazy danych.")