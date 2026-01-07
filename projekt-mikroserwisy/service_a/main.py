from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
import crud
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/results", response_model=schemas.Result)
def create_analysis_result(result: schemas.ResultCreate, db: Session = Depends(get_db)):
    return crud.create_result(db=db, result=result)

@app.get("/results", response_model=List[schemas.Result])
def read_results(db: Session = Depends(get_db)):
    return crud.get_results(db)