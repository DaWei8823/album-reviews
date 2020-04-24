from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, Numeric, UniqueConstraint, literal
from sqlalchemy.orm import sessionmaker, relationship, query
from contextlib import contextmanager

Base = declarative_base()

connection_string = "mssql+pyodbc://localhost\\SQLEXPRESS/Music?driver=SQL+Server&trusted_connection=yes"

class MusicRepo:

    def __init__(self, connection_string):
        engine = create_engine(connection_string)
        self.Session = sessionmaker(engine)


    def add_artist(self, name:str):
        """Adds artist if it doesn't exist else does nothing"""   
        if self._check_exists(Artist, Artist.artist_name == name):
            return

        artist = Artist(artist_name = name)
        self._add(artist)
    

    def add_publication(self, name:str, max_score:float):  
        """Adds publication if it doesn't exist else does nothing"""  
        if self._check_exists(Publication, Publication.publication_name == name):
            return

        publication = Publication(publication_name = name, max_score = max_score)
        self._add(publication)   


    # def add_album(self, album_name:str, artist_name:str):
    #     """adds album and artist (if artist not already present). If album already present, it does nothing"""
    #     artist_name_pred = Artist.artist_name == artist_name
    #     if not self._check_exists(Artist, artist_name_pred):
    #         self.add_artist(artist_name)
        
        # check if album exists
        # add album if doesn't exist 



    def _get(self, table, predicate = None) -> query.Query:
        predicate = predicate if not predicate is None else True
        with self._session_scope() as session:
            return session.query(table).filter(predicate) 

    def _check_exists(self, table, predicate):
        with self._session_scope() as session:
            q = session.query(table).filter(predicate)
            return session.query(literal(True)).filter(q.exists()).scalar()

    
    def _add(self, object):
        with self._session_scope() as session:
            session.add(object)
    

    @contextmanager
    def _session_scope(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()


class Review(Base):
    __tablename__ = "Review"
    
    review_id = Column("ReviewId", Integer, primary_key = True, autoincrement = True)
    album_id = Column("AlbumId", Integer, ForeignKey("Album.AlbumId"))
    publication_id = Column("PublicationId", Integer, ForeignKey("Publication.PublicationId"))
    url = Column("Url", String(200), nullable=False)
    review_text = Column("ReviewText", String(), nullable=False)
    score = Column("Score", Numeric(4,2))

    UniqueConstraint("AlbumId","PublicationId")


class Publication(Base):
    __tablename__ = "Publication"
    
    publication_id = Column("PublicationId", Integer, primary_key = True, autoincrement = True)
    publication_name = Column("PublicationName", String(100), nullable=False)
    max_score = Column("MaxScore", Integer)

    UniqueConstraint("PublicationName")

class Album(Base):
    __tablename__ = "Album"
    
    album_id = Column("AlbumId", Integer, primary_key = True, autoincrement = True)
    title = Column("Title", String(100), nullable = False)
    artist_id = Column("ArtistId", Integer, ForeignKey("Artist.ArtistId"))
    reviews = relationship("Review")

    UniqueConstraint("Title","ArtistId")


class Artist(Base):
    __tablename__ = "Artist"
    
    artist_id = Column("ArtistId", Integer, primary_key = True, autoincrement = True)
    artist_name = Column("ArtistName", String(100))
    albums = relationship("Album")
    UniqueConstraint("ArtistName")

