
%load_ext autoreload
%autoreload 2
from fastapi import FastAPI, status
from database import Base, engine, Citation, StreetSweepingPoint, StreetSweepingSegment
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, MetaData
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import csv
import geocoder
from config import Config
from sqlalchemy.orm import Session
from shapely.wkt import loads

engine = create_engine("sqlite:///parking_pal_fastapidb.db")
Base = declarative_base()
session = Session(bind=engine, expire_on_commit=False)
# Citation.geocode_citations()
# Citation.seed_citations('seeds/citations.csv')


# delete all citations session.query(Citation).delete()
# session.commit()

# uvicorn main:app --reload
# alembic revision — autogenerate -m "First commit"
# alembic upgrade head

