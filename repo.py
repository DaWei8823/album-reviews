from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, NVARCHAR, ForeignKey, create_engine, Numeric, UniqueConstraint, literal, and_
from sqlalchemy.orm import sessionmaker, relationship, query
from contextlib import contextmanager

Base = declarative_base()

#TODO: Change review text to NVarchar and move models to own file

class MusicRepo:

    def __init__(self, connection_string:str):
        engine = create_engine(connection_string)
        self.Session = sessionmaker(engine)

    def add_review(self, album_title:str, artist_name, publication_name:str, url:str, review_text:str, score:float):
        """adds review if it no review for that publication and album exist else does nothing. Adds the artist and
           album if not present. Uses crude heuristic to add publication and max score if not present"""
        
        predicate = and_(Review.album.has(Album.title == album_title), 
            Review.album.has(Album.artist.has(Artist.artist_name == artist_name)),
            Review.publication.has(Publication.publication_name == publication_name))

        if self._check_exists(Review, predicate):
            return

        #crude heuristic for determining max score 
        max_score = (100 if score > 50 else (10 if score > 5 else 5)) if score else None

        self.add_publication(name = publication_name, max_score = max_score)
        self.add_album(artist_name = artist_name, album_title = album_title)

        publication_id = self._get(Publication, Publication.publication_name == publication_name).one().publication_id
        album_id = self._get(Album, Album.title == album_title).one().album_id        

        self._add(Review(publication_id = publication_id, album_id = album_id, url = url, review_text = review_text, score = score))  


    def add_album(self, artist_name:str, album_title:str):
        """adds album and artist (if artist not already present). If album already present, it does nothing"""
        if self._check_exists(Album, and_(Album.title == album_title, Album.artist.has(Artist.artist_name == artist_name))):
            return
        
        self.add_artist(artist_name)
        
        artist_id = self._get(Artist, Artist.artist_name == artist_name).one().artist_id
        self._add(Album(artist_id = artist_id, title = album_title))

    def add_publication(self, name:str, max_score:float):  
        """Adds publication if it doesn't exist else does nothing"""  
        if self._check_exists(Publication, Publication.publication_name == name):
            return

        publication = Publication(publication_name = name, max_score = max_score)
        self._add(publication)

    def add_artist(self, name:str):
        """Adds artist if it doesn't exist else does nothing"""   
        if self._check_exists(Artist, Artist.artist_name == name):
            return

        artist = Artist(artist_name = name)
        self._add(artist)
    
    def _get(self, table, predicate = None) -> query.Query:
        predicate = predicate if not predicate is None else True
        with self._session_scope() as session:
            return session.query(table).filter(predicate) 

    def _check_exists(self, table, predicate):
        with self._session_scope() as session:
            q = session.query(table).filter(predicate)
            return True if session.query(literal(True)).filter(q.exists()).scalar() else False

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


class Publication(Base):
    __tablename__ = "Publication"
    
    publication_id = Column("PublicationId", Integer, primary_key = True, autoincrement = True)
    publication_name = Column("PublicationName", String(100), nullable=False)
    max_score = Column("MaxScore", Integer)

    reviews = relationship("Review", back_populates="publication")

    UniqueConstraint("PublicationName")


class Artist(Base):
    __tablename__ = "Artist"
    
    artist_id = Column("ArtistId", Integer, primary_key = True, autoincrement = True)
    artist_name = Column("ArtistName", String(100))
    
    albums = relationship("Album", back_populates="artist")
    
    UniqueConstraint("ArtistName")


class Album(Base):
    __tablename__ = "Album"
    
    album_id = Column("AlbumId", Integer, primary_key = True, autoincrement = True)
    title = Column("Title", String(100), nullable = False)
    artist_id = Column("ArtistId", Integer, ForeignKey("Artist.ArtistId"))
    
    artist = relationship("Artist", back_populates="albums")
    reviews = relationship("Review", back_populates="album")

    UniqueConstraint("Title","ArtistId")


class Review(Base):
    __tablename__ = "Review"
    
    review_id = Column("ReviewId", Integer, primary_key = True, autoincrement = True)
    album_id = Column("AlbumId", Integer, ForeignKey("Album.AlbumId"))
    publication_id = Column("PublicationId", Integer, ForeignKey("Publication.PublicationId"))
    url = Column("Url", String(200), nullable=False)
    review_text = Column("ReviewText", NVARCHAR(), nullable=False)
    score = Column("Score", Numeric(4,2))

    publication = relationship("Publication", back_populates = "reviews")
    album = relationship("Album", back_populates="reviews")

    UniqueConstraint("AlbumId", "PublicationId")