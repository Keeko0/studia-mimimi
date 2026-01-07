from sqlalchemy.orm import Session
import models
import schemas

def get_results(db: Session):
    return db.query(models.AnalysisResult).all()

def create_result(db: Session, result: schemas.ResultCreate):
    db_result = models.AnalysisResult(image_url=result.image_url, person_count=result.person_count)
    
    db.add(db_result)
    
    db.commit()
    
    db.refresh(db_result)
    return db_result