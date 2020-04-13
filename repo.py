from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

connection_string = "mssql+pyodbc://localhost\\SQLEXPRESS/Music?driver=SQL+Server&trusted_connection=yes"

class MusicRepo:

    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)
        self.Session = sessionmaker(engine)

    def add_artist(name):
        session = self.Session()        
        artist = Artist(name = name)
        try:
            session.add(name)
        except:
            session.rollback()
            raise


class Album(Base):
    __tablename__ = "Album"
    album_id = Column("AlbumId", Integer, primary_key = True, autoincrement = True)
    title = Column("Title", String(100))
    artist_id = Column("ArtistId", Integer, ForeignKey("Artist.ArtistId"))

class Artist(Base):
    __tablename__ = "Artist"
    artist_id = Column("ArtistId", Integer, primary_key = True, autoincrement = True)
    name = Column("Name", String(100))
    albums = relationship("Album")

