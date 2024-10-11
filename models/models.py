from sqlalchemy import Integer, String, DateTime, Column, Float, create_engine, MetaData, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from settings import engine
from pydantic import BaseModel


Session = sessionmaker(bind=engine)
metadata = MetaData()
metadata.reflect(engine)
Base = declarative_base()


class City(Base):
    __tablename__ = 'city'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    lat = Column(Float)
    lon = Column(Float)


class Log(Base):
    __tablename__ = 'log'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    command = Column(String)
    datetime = Column(DateTime)
    answer = Column(String)


class UserCity(Base):
    __tablename__ = 'user_city'
    id_user = Column(Integer, primary_key=True)
    id_city = Column(Integer, ForeignKey('city.id'))


Base.metadata.create_all(engine)


class LogResponse(BaseModel):
    user_id: int
    command: str
    datetime: str
    answer: str
