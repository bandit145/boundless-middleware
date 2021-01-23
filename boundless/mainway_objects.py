from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import column_property, relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Float, Table, DateTime

Base = declarative_base()

location_poi = Table(
    "location_poi",
    Base.metadata,
    Column("location", Integer, ForeignKey("locations.id")),
    Column("poi", Integer, ForeignKey("pois.id")),
)


class Server(Base):
    __tablename__ = "servers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    server_type = Column(String, nullable=False)
    # depending on the service this could be int or whatever but store as string
    server_id = Column(String, nullable=False)
    subversive_word = relationship("SubversiveWord")


class Poi(Base):
    __tablename__ = "pois"
    id = Column(Integer, primary_key=True, autoincrement=True)
    discordid = Column(Integer, unique=True)
    pos_comments = Column(Float)
    neg_comments = Column(Float)
    flagged_comments = Column(Float)
    subversiveness = column_property(neg_comments / flagged_comments)
    locations = relationship("Location", secondary=location_poi, back_populates="pois")
    incidents = relationship("Incident")


class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    pois = relationship("Poi", secondary=location_poi, back_populates="locations")


class SubversiveWord(Base):
    __tablename__ = "subversive_words"
    word = Column(String, primary_key=True)
    server_id = Column(Integer, ForeignKey("servers.id"))


class Incident(Base):
    __tablename__ = "incidents"
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String, nullable=False)
    writeup = Column(String)
    poi = Column(Integer, ForeignKey("pois.id"))
    location = Column(Integer, ForeignKey("locations.id"))
    date = Column(DateTime, nullable=False)
