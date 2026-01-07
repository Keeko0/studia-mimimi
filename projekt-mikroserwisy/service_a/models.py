from sqlalchemy import Column, Integer, String
from database import Base

class AnalysisResult(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String, index=True)
    person_count = Column(Integer)