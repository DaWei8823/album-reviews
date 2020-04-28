from sqlalchemy import Column, Integer, String, NVARCHAR, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, 

Base = declarative_base()

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