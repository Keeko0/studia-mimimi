from pydantic import BaseModel

class ResultCreate(BaseModel):
    image_url: str
    person_count: int

class Result(ResultCreate):
    id: int

    class Config:
        orm_mode = True