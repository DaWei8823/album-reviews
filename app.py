import review_scraper as rs
from flask import Flask 
from json import dumps
from logging.handlers import TimedRotatingFileHandler
import logging
import datetime as dt
import re
import jsonpickle as jp
from flask.ext.sqlalchemy

app = Flask(__name__)

handler = TimedRotatingFileHandler("logs/PitchforkApi.log", when="midnight", interval=1)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
app.logger.addHandler(handler)

app.config["SQLALCHEMY_DATABASE_URI"] = "mssql+pyodbc://localhost\\SQLEXPRESS/Music?driver=SQL+Server&trusted_connection=yes"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = SqlAlchemy(app)

@app.route('/')
def hello_asa():
    return "hi asa!"

@app.route('/review/<artist>/<album>', methods = ['GET'])
def get_review(artist = None, album = None):
    try:
        review = rs.get_album_review_from_artist_and_album(artist, album)
        return jp.encode(review)
    except Exception as e:
        app.logger.error(f"Exception getting review for artist: {artist} and album: {album}  {str(e)}")



