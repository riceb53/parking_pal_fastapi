from fastapi import FastAPI, status
from database import Base, engine, find_closest_coordinates, euclidean_distance, Citation, StreetSweepingPoint, StreetSweepingSegment
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import geocoder
import pdb

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
def read_root(q: str = '762 Fulton St, San Francisco, CA 94102'):    
    # untested
    session = Session(bind=engine, expire_on_commit=False)
    # get user address
    g = geocoder.osm(q)
    user_location = (g.json['lat'], g.json['lng'])    
    # find closest StreetSweepingPoint
    street_sweeping_points = session.query(StreetSweepingPoint).all()
    print('len(street_sweeping_points)')
    print(len(street_sweeping_points))
    closest_coordinates = find_closest_coordinates(user_location, street_sweeping_points)
    # find associated StreetSweepingSegment    
    street_sweeping_segment = session.query(StreetSweepingSegment).filter_by(id=closest_coordinates.street_sweeping_segment_id).first()
    print('street_sweeping_segment')
    print(street_sweeping_segment)
    # find all Citations associated with StreetSweepingSegment
    # return those citations
    
    # citation_list = session.query(Citation).filter(Citation.latitude.isnot(0)).all()
    citations = session.query(Citation).filter_by(street_sweeping_segment_id=street_sweeping_segment.id).all()
    
    return {
        'citations': citations, 
        'street_sweeping_segment': street_sweeping_segment, 
        'closest_coordinates': closest_coordinates
    }


@app.get("/search")
def search():
    return {"the results of your search": []}