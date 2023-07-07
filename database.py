from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, MetaData, Table, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import csv
import geocoder
from config import Config
from sqlalchemy.orm import Session
from shapely.wkt import loads
import pdb
import time
import math

def calculate_q1_q3(sorted_list):
    n = len(sorted_list)
    q1_index = (n + 1) // 4
    q3_index = (3 * (n + 1)) // 4
    q1 = sorted_list[q1_index - 1]
    q3 = sorted_list[q3_index - 1]
    return [q1.citation_issued_datetime.time().strftime("%H:%M"), q3.citation_issued_datetime.time().strftime("%H:%M")]


def euclidean_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def find_closest_coordinates(target_point, coordinates):
    closest_distance = float('inf')
    closest_coordinates = None

    for coordinate in coordinates:
        distance = euclidean_distance((target_point[0], target_point[1]), (coordinate.latitude, coordinate.longitude))
        if distance < closest_distance:
            closest_distance = distance
            closest_coordinates = coordinate
    return closest_coordinates


def load_csv_into_dict(filename):

    result = []
    
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            result.append(dict(row))
    
    return result
engine = create_engine("sqlite:///parking_pal_fastapidb.db")
Base = declarative_base()



class Citation(Base):
    __tablename__ = 'citations'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)    
    citation_number = Column(String(255))        
    citation_issued_datetime = Column(DateTime)
    violation = Column(String(255))
    violation_desc = Column(String(255))
    citation_location = Column(String(255))
    location_street = Column(String(255))
    location_number = Column(Integer)
    location_suffix = Column(String(255))
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
    street_sweeping_segment_id = Column(Integer)
    geocode_failed = Column(Boolean)
    bad_address = Column(Boolean)


    def __repr__(self):
        return "Citation(id={}, citation_number={}, latitude={}, longitude={}, location={}, citation_issued_datetime={})".format(self.id, self.citation_number, self.latitude, self.longitude, self.citation_location, self.citation_issued_datetime)


    @classmethod
    def seed_citations(self, filename):
        count = 0     
        data = load_csv_into_dict(filename)    
        session = Session(bind=engine, expire_on_commit=False)         
        for citation in data:
            calculated_citation_issued_datetime = datetime.strptime(citation['Citation Issued DateTime'], "%m/%d/%Y %I:%M:%S %p")
            calculated_date_added = datetime.strptime(citation['Date Added'], "%m/%d/%Y %I:%M:%S %p")                        
            coordinates_str = citation['geom']
            if coordinates_str:
                # Parse the WKT representation into a geometry object
                geometry = loads(coordinates_str)
                # Extract the latitude and longitude values
                calculated_longitude = geometry.x
                calculated_latitude = geometry.y
            else:  
                calculated_latitude = 0
                calculated_longitude = 0                

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
            count += 1
            # pdb.set_trace()
            print(count)
            if count % 10_000:
                print(count)

    @classmethod
    def filter_to_new_citations(self):
        count = 0
        print('starting method')
        with open('seeds/citations.csv', 'r') as csvfile:
            all_citations = csv.reader(csvfile)

            # Open the CSV file in write mode
            with open('seeds/2022_2023_citations.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                # Iterate through the data and write each row to the CSV file
                for row in all_citations:
                    if count == 0:
                        writer.writerow(row)                    
                        count += 1
                        continue
                                        
                    calculated_citation_issued_datetime = datetime.strptime(row[1], "%m/%d/%Y %I:%M:%S %p")                    
                    if calculated_citation_issued_datetime.year == 2022 or calculated_citation_issued_datetime.year == 2023:                    
                        writer.writerow(row)                    
                    count += 1
                    print(count)

            print("CSV file created and written successfully.")


    @classmethod
    # have not run this but will do later
    def geocode_citations(self):        
        # load in all citations

        engine = create_engine("sqlite:///parking_pal_fastapidb.db")        
        session = Session(bind=engine, expire_on_commit=False) 
        print('before getting citations')
        # citations = session.query(Citation).all()        
        # citations = session.query(Citation).filter(Citation.latitude == 0).all()        
        citations = session.query(Citation).filter(Citation.latitude == 0, Citation.geocode_failed.isnot(True)).all()
        print(len(citations))
        count = 0
        for citation in citations:
            count += 1
            if count % 100 == 0:
                print(count)
            # if lat is 0, geocode
            if citation.latitude == 0:
                # 76
                g = geocoder.osm(citation.citation_location + " San Francisco, CA")
                if g and g.json and g.json['lat']:
                    citation.latitude = g.json['lat']
                    citation.longitude = g.json['lng']
                    session.commit()
                else:
                    print(g)
                    citation.geocode_failed = True                    
                    session.commit()
                    # pdb.set_trace()  
            # print(citation)
    
    @classmethod
    def find_street_sweeping_segment(self):
        session = Session(bind=engine, expire_on_commit=False)                         
        citation_list = session.query(Citation).filter(Citation.latitude.isnot(0), Citation.street_sweeping_segment_id == None, Citation.geocode_failed.isnot(True)).all()
            
        street_sweeping_points = session.query(StreetSweepingPoint).all()
        count = 0


        for citation in citation_list:
            count += 1
            if count % 100 == 0:
                print(count)
            # print("right before finding closest coordinates")
            closest_coordinates = find_closest_coordinates((citation.latitude, citation.longitude), street_sweeping_points)
            # print("right after finding closest coordinates")            
            citation.street_sweeping_segment_id = closest_coordinates.street_sweeping_segment_id
            session.commit()
            # make new column for citation that has streetsweepingsegment id
    
    @classmethod
    def analysis(self, citations):
        # sort citations 
        sorted_citations = sorted(citations, key=lambda citation: citation.citation_issued_datetime.time())        
        data = {
            'types': {},
            'hours': {},            
            'street_sweeping_hours': {}
        }
        for citation in sorted_citations:            
            if citation.violation_desc not in data['types']:
                data['types'][citation.violation_desc] = 0            
            data['types'][citation.violation_desc] += 1
            beginning_of_hour = citation.citation_issued_datetime.replace(minute=0, second=0).strftime("%I:%M %p")
            if beginning_of_hour not in data['hours']:
                data['hours'][beginning_of_hour] = 0

            data['hours'][beginning_of_hour] += 1     
        # pdb.set_trace()       
        a = sorted(data['types'], key=lambda k: data['types'][k])
        data['types'] = sorted(data['types'].items(), key=lambda x:x[1], reverse=True)
        data['types'] = dict(data['types'])

      
        str_clean_citations = [citation for citation in sorted_citations if citation.violation_desc == 'STR CLEAN']
        q1_q3_str_clean = calculate_q1_q3(str_clean_citations)
        all_str_clean = [str_clean_citations[0].citation_issued_datetime.time().strftime("%H:%M"), str_clean_citations[-1].citation_issued_datetime.time().strftime("%H:%M")]
        q1_q3 = calculate_q1_q3(sorted_citations)        

        return {
            'q1_q3': {
                'q1_q3': q1_q3,
                'q1_q3_str_clean': q1_q3_str_clean,
                'all_str_clean': all_str_clean,
            },
            'data': data
        }
    
    @classmethod
    def split_location_for_search(self):
        # find all locations
        engine = create_engine("sqlite:///parking_pal_fastapidb.db")        
        session = Session(bind=engine, expire_on_commit=False) 
        print('before getting citations')
        number_of_segments = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0}
        ls = {}
        amp_count = 0
        count = 0
        convert_to_standard_suffix = {
            'ST': 'STREET',
            'AVE': 'AVENUE',
            'STREET': 'STREET',
            'AVENUE': 'AVENUE',
            'BLVD': 'BOULEVARD',
            'DR': 'DRIVE',
            'WAY': 'WAY',
            'TER': 'TERRACE',
            'CT': 'COURT',
            'PL': 'PLACE',
            'DRIVE': 'DRIVE',
            'PARK': 'PARK',
            'HWY': 'HIGHWAY',
            'HWY': 'HIGHWAY',
            'RD': 'ROAD',
            'LN': 'LANE',
            'STATION': 'STATION',
            'WEST': 'WEST',
            'EAST': 'EAST',
            'CIR': 'CIRCLE',
            'ROAD': 'ROAD',
            'ALY': 'ALLEY',
            'STA': 'STATION',
            'WY': 'WAY',
        }

        
        # citations = session.query(Citation).all()        
        # citations = session.query(Citation).filter(Citation.latitude == 0).all()        
        citations = session.query(Citation).filter(Citation.location_street == None, Citation.bad_address.isnot(True)).all()
        print(len(citations))
        for citation in citations:
            count += 1
            if count % 1000 == 0:
                print(count, citation)
            location = citation.citation_location.split()
            if '&' in citation.citation_location or len(location) == 1 or len(location) == 0:
                amp_count += 1   
                citation.bad_address = True
                session.commit()             
                continue                
            number_of_segments[len(location)] += 1            
         
            if len(location) == 2:
                citation.location_number = location[0]
                citation.location_street = location[1]                                                
                # try to geocode?
                if location[-1] == "STREET":
                    citation.bad_address = True
                    session.commit()     
                    continue
                elif "BROADWAY" in location[-1] or "EMBARCADERO" in location[-1]:
                    continue                
                g = geocoder.osm(citation.citation_location + " San Francisco, CA")                
                if g.json and g.json['raw'] and g.json['raw']['address'] and 'street' in g.json['raw']['address']:
                    address_segments = g.json['raw']['address']['road'].split()
                    citation.location_suffix = address_segments[-1].upper()   
                    session.commit()           
                else:
                    citation.bad_address = True
                    session.commit()     
                continue

            # ls == location suffix?
            if location[-1] in ls:
                ls[location[-1]] += 1
            else:
                ls[location[-1]] = 1

            #####
            # regular/3+
            # split into number name and suffix
                # 
            citation.location_number = location[0]
            citation.location_street = ''.join(location[1:-1])
            # CONVERT, wait on results   
            if location[-1] in convert_to_standard_suffix:
                citation.location_suffix = convert_to_standard_suffix[location[-1]]
            else:
                citation.location_suffix = location[-1]
            session.commit()
            # update cols
            # save

            
            # session.commit()
            # else:
    @classmethod
    def standardize_street_suffix(self):
        convert_to_standard_suffix = {
            'ST': 'STREET',
            'AVE': 'AVENUE',
            'STREET': 'STREET',
            'AVENUE': 'AVENUE',
            'BLVD': 'BOULEVARD',
            'DR': 'DRIVE',
            'WAY': 'WAY',
            'TER': 'TERRACE',
            'CT': 'COURT',
            'PL': 'PLACE',
            'DRIVE': 'DRIVE',
            'PARK': 'PARK',
            'HWY': 'HIGHWAY',
            'HWY': 'HIGHWAY',
            'RD': 'ROAD',
            'LN': 'LANE',
            'STATION': 'STATION',
            'WEST': 'WEST',
            'EAST': 'EAST',
            'CIR': 'CIRCLE',
            'ROAD': 'ROAD',
            'ALY': 'ALLEY',
            'STA': 'STATION',
            'WY': 'WAY',
        }

        engine = create_engine("sqlite:///parking_pal_fastapidb.db")        
        session = Session(bind=engine, expire_on_commit=False) 
        citations = session.query(Citation).filter(Citation.location_suffix.isnot(True), Citation.bad_address.isnot(True)).all()
        print(len(citations))
        count = 0
        for citation in citations:            
            count += 1
            if count % 1000 == 0:
                print(count, citation)
            location = citation.citation_location.split()            
            if len(location) > 2:
                original_suffix = location[-1].upper()
                # CONVERT, wait on results
                if original_suffix in convert_to_standard_suffix:
                    citation.location_suffix = convert_to_standard_suffix[original_suffix]
                else:
                    citation.location_suffix = original_suffix
                session.commit()
        
        


        # get citation_location
        # split into pieces
        # assign to different columns

class StreetSweepingPoint(Base):
    __tablename__ = 'street_sweeping_points'
    id = Column(Integer, primary_key=True)    
    latitude = Column(Float())
    longitude = Column(Float())
    street_sweeping_segment_id = Column(Integer)
    
            

class StreetSweepingSegment(Base):    
    __tablename__ = 'steet_sweeping_segments'
    id = Column(Integer, primary_key=True)    
    cnn = Column(String(255))        
    corridor = Column(String(255)) 
    limits = Column(String(255)) 
    cnn_right_left = Column(String(255))
    block_side = Column(String(255))
    full_name = Column(String(255))
    weekday = Column(String(255))    
    from_hour = Column(Integer)
    to_hour = Column(Integer)
    week1 = Column(Integer)    
    week2 = Column(Integer)    
    week3 = Column(Integer)    
    week4 = Column(Integer)    
    week5 = Column(Integer)    
    holidays = Column(Integer)
    block_sweep_id = Column(Integer)
    line = Column(String(255))    

    @classmethod
    def seed_street_sweeping_segments(self, filename):
        count = 0
        data = load_csv_into_dict(filename)    
        session = Session(bind=engine, expire_on_commit=False)         
        session.query(StreetSweepingSegment).delete()
        session.query(StreetSweepingPoint).delete()
        session.commit()
        for sss in data:
            # pdb.set_trace()
            # go through each, add normally but make new streetsweepingpoint model to handle all the street sweeping points
            # print(count)            

            new_sss = StreetSweepingSegment(
                cnn=sss['CNN'],
                corridor=sss['Corridor'],
                limits=sss['Limits'],
                cnn_right_left=sss['CNNRightLeft'],
                block_side=sss['BlockSide'],
                full_name=sss['FullName'],
                weekday=sss['WeekDay'],
                from_hour=sss['FromHour'],
                to_hour=sss['ToHour'],
                week1=sss['Week1'],
                week2=sss['Week2'],
                week3=sss['Week3'],
                week4=sss['Week4'],
                week5=sss['Week5'],
                holidays=sss['Holidays'],
                block_sweep_id=sss['BlockSweepID'],
                line=sss['Line'],           
            )
            session.add(new_sss)
            session.commit()
            # if count == 3132 or count == 3133:
            #     pdb.set_trace()
            if sss['Line']:
                linestring = loads(sss['Line'])
                coordinates = list(linestring.coords)                        
                for point in coordinates:
                    new_point = StreetSweepingPoint(
                        latitude=point[1],
                        longitude=point[0],
                        street_sweeping_segment_id=new_sss.id
                        
                    )
                    session.add(new_point)
                    session.commit()

            count += 1
            # pdb.set_trace()
            
            if count % 1000:
                print(count)