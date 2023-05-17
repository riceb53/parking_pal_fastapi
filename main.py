from fastapi import FastAPI, status
from database import Base, engine, Citation
from sqlalchemy.orm import Session


Base.metadata.create_all(engine)
app = FastAPI()


# from pydantic import BaseModel

# I don't think this is necessary because users can't make a new citation
# class CitationRequest(BaseModel):
#     citation_number: str



@app.get("/")
def read_root():
    session = Session(bind=engine, expire_on_commit=False)
    citation_list = session.query(Citation).all()
    return citation_list


@app.get("/search")
def search():
    return {"the results of your search": []}