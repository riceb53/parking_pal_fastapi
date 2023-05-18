from fastapi import FastAPI, status
from database import Base, engine, Citation
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(engine)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with a list of allowed origins (domains)
    allow_credentials=True,
    allow_methods=["*"],  # Replace with a list of allowed HTTP methods
    allow_headers=["*"],  # Replace with a list of allowed HTTP headers
)


# from pydantic import BaseModel

# I don't think this is necessary because users can't make a new citation
# class CitationRequest(BaseModel):
#     citation_number: str



@app.get("/")
def read_root():
    session = Session(bind=engine, expire_on_commit=False)
    citation_list = session.query(Citation).filter(Citation.latitude.isnot(0)).all()
    return citation_list


@app.get("/search")
def search():
    return {"the results of your search": []}