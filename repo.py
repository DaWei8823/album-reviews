from contextlib import contextmanager
from models import Album, Artist, Publication, Review
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker, query
from typing import List 



class ReviewRepo:

    def __init__(self, connection_string:str):
        engine = create_engine(connection_string)
        self.Session = sessionmaker(engine)

    def get_reviews(self, artist_name, album_title) -> List[Review]:
        predicate = and_(Review.album.has(Album.title == album_title), 
            Review.album.has(Album.artist.has(Artist.artist_name == artist_name)))

        return list(self._get(Review, predicate))

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

        self._add(Review(publication_id = publication_id, album_id = album_id, 
            url = url, review_text = review_text, score = score))  

    def add_album(self, artist_name:str, album_title:str):
        """adds album and artist (if artist not already present). If album already present, it does nothing"""
        predicate = and_(Album.title == album_title, Album.artist.has(Artist.artist_name == artist_name))
        if self._check_exists(Album, predicate):
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