from fastapi import FastAPI, status
from database import Base, engine, Citation
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import csv
import geocoder
from config import Config
from sqlalchemy.orm import Session
from shapely.wkt import loads

engine = create_engine("sqlite:///parking_pal_fastapi.db")
Base = declarative_base()
session = Session(bind=engine, expire_on_commit=False) 