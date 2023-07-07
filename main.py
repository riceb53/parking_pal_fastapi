import uvicorn
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


@app.get("/")
def read_root(q: str = '1500 FULTON STREET, San Francisco, CA'):    
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

    analysis = Citation.analysis(citations)
    return {
        'citations': citations, 
        'street_sweeping_segment': street_sweeping_segment, 
        'closest_coordinates': closest_coordinates,
        'analysis': analysis,
    }


@app.get("/search")
def search():    
    return {"the results of your search": []}

@app.get("/address_search")
def address_search(q: str = '1500 FULTON STREET, San Francisco, CA'):
    # pdb.set_trace()
    # based on input address
    trimmed_address = q.split(", ")[0].split()
    street_number = int(trimmed_address[0])
    street_name = ''.join(trimmed_address[1:-1])
    street_suffix = trimmed_address[-1]
    even_or_odd = int(street_number) % 2

    beginning_of_block = ((street_number // 100) * 100)
    end_of_block = (((street_number // 100) + 1) * 100) - 1


        # find citations on that same block
    session = Session(bind=engine, expire_on_commit=False)
    citations = session.query(Citation).filter(
        Citation.location_number.between(beginning_of_block, end_of_block),
        Citation.location_street.ilike(f'%{street_name}%'),
        Citation.location_suffix.ilike(f'%{street_suffix}%'),
        Citation.location_number % 2 == even_or_odd,
        Citation.geocode_failed.isnot(True),
        Citation.latitude.isnot(0)
    ).all()

        # return those citations
    print(len(citations))
    analysis = Citation.analysis(citations)
    g = geocoder.osm(q)
    user_location = {'latitude': g.json['lat'], 'longitude': g.json['lng']}
    return {
        'citations': citations, 
        # 'street_sweeping_segment': street_sweeping_segment, 
        'closest_coordinates': user_location,
        'analysis': analysis,
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
