from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Unique, create_engine
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


class Review(Base):
    __tablename__ = "Review"
    
    review_id = Column("ReviewId", Integer, primary_key = True, autoincrement = True)
    album_id = Column("AlbumId", Integer, ForeignKey("Album.AlbumId"))
    publication_id = Column("PublicationId", Integer, ForeignKey("Album.AlbumId"))
    review_url = Column("ReviewUrl", String(200), nullable=False)
    review_text = Column("ReviewText", String(), nullable=False)

    Unique("album_id","publication_id")


class Publication(Base):
    __tablename__ = "Publication"
    
    publication_id = Column("PublicationId", Integer, primary_key = True, autoincrement = True)
    publication_name = Column("PublicationName", String(100), nullable=False)

class Album(Base):
    __tablename__ = "Album"
    
    album_id = Column("AlbumId", Integer, primary_key = True, autoincrement = True)
    title = Column("Title", String(100), nullable = False)
    artist_id = Column("ArtistId", Integer, ForeignKey("Artist.ArtistId"))


class Artist(Base):
    __tablename__ = "Artist"
    
    artist_id = Column("ArtistId", Integer, primary_key = True, autoincrement = True)
    name = Column("Name", String(100))
    albums = relationship("Album")

