from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import csv
import geocoder
from config import Config
from sqlalchemy.orm import Session
from shapely.wkt import loads


def load_csv_into_dict(filename):
    result = []
    
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            result.append(dict(row))
    
    return result
engine = create_engine("sqlite:///parking_pal_fastapi.db")
Base = declarative_base()



class Citation(Base):    
    __tablename__ = 'citations'
    id = Column(Integer, primary_key=True)
    citation_number = Column(String(50))
    citation_number = Column(String(255))        
    citation_issued_datetime = Column(DateTime)
    violation = Column(String(255))
    violation_desc = Column(String(255))
    citation_location = Column(String(255))
    vehicle_plate_state = Column(String(255))
    vehicle_plate = Column(String(255))
    fine_amount = Column(Integer)
    date_added = Column(DateTime)
    type_of_citation = Column(String(255))
    latitude = Column(Float())
    longitude = Column(Float())
    computed_region_jwn9_ihcz = Column(String(255))
    computed_region_6qbp_sg9q = Column(String(255))
    computed_region_qgnn_b9vv = Column(String(255))
    computed_region_26cr_cadq = Column(String(255))
    computed_region_ajp5_b2md = Column(String(255))
    date_created = Column(DateTime, default=datetime.utcnow)


    def __repr__(self):
        return "Citation(id={}, citation_number={})".format(self.id, self.citation_number)


    @classmethod
    def seed_citations(self, filename):
        count = 0     
        data = load_csv_into_dict(filename)    
        session = Session(bind=engine, expire_on_commit=False)         
        for citation in data:
            coordinates_str = citation['geom']
            if coordinates_str:
                # Parse the WKT representation into a geometry object
                geometry = loads(coordinates_str)
                # Extract the latitude and longitude values
                calculated_longitude = geometry.x
                calculated_latitude = geometry.y
            else:  
                g = geocoder.google(citation['Citation Location'] + " San Francisco, CA", key=Config.API_KEY)
                count += 1
                if g.status == 'ZERO_RESULTS' or g.status == 'REQUEST_DENIED':
                    calculated_latitude = 0
                    calculated_longitude = 0
                else:
                    print('geocoder worked')
                    calculated_latitude = g.latlng[0]
                    calculated_longitude = g.latlng[1]

            calculated_citation_issued_datetime = datetime.strptime(citation['Citation Issued DateTime'], "%m/%d/%Y %I:%M:%S %p")
            calculated_date_added = datetime.strptime(citation['Date Added'], "%m/%d/%Y %I:%M:%S %p")            
            new_citation = Citation(
                citation_number=citation['Citation Number'],
                citation_issued_datetime=calculated_citation_issued_datetime,
                violation=citation['Violation'],
                violation_desc=citation['Violation Description'],
                citation_location=citation['Citation Location'],
                vehicle_plate_state=citation['Vehicle Plate State'],
                vehicle_plate=citation['Vehicle Plate'],
                fine_amount=citation['Fine Amount'],
                date_added=calculated_date_added,
                latitude=calculated_latitude,
                longitude=calculated_longitude,
                computed_region_jwn9_ihcz=citation['Neighborhoods'],
                computed_region_6qbp_sg9q=citation['SF Find Neighborhoods'],
                computed_region_qgnn_b9vv=citation['Current Police Districts'],
                computed_region_26cr_cadq=citation['Current Supervisor Districts'],
                computed_region_ajp5_b2md=citation['Analysis Neighborhoods'],                
            )
            session.add(new_citation)
            session.commit()
            print(count)





