from dataclasses import dataclass
from flask import Flask 
import jsonpickle as jp
import logging
from logging.handlers import TimedRotatingFileHandler
from repo import ReviewRepo, Review
from summarizer import TextRankSummarizer
import settings

#TODO: handle misformed requests

app = Flask(__name__)

handler = TimedRotatingFileHandler("logs/PitchforkApi.log", when="midnight", interval=1)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
app.logger.addHandler(handler)

repo = ReviewRepo(settings.connection_string)
review_summarizer = TextRankSummarizer(settings.word_embeddings_path)

review_summarizer.load_word_embeddings()

@dataclass
class ReviewSummary:
    publication:str
    rating_desc:str
    top_sentence:str

@app.route('/review/<artist>/<album>', methods = ['GET'])
def get_review(artist = None, album = None):
    try:
        reviews = repo.get_reviews(artist, album)
        review_summaries = [get_reviews_summary(review) for review in reviews]
        return jp.encode(review_summaries)
    except Exception as e:
        app.logger.error(f"Exception getting review for artist: {artist} and album: {album}  {str(e)}")


def get_reviews_summary(review:Review) -> ReviewSummary:
    publication = review.publication.publication_name
    top_sentence = review_summarizer.get_top_sentences(review.review_text, 1)[0]
    rating_desc = f"{review.score}/{review.publication.max_score}"
    
    return ReviewSummary(publication,rating_desc, top_sentence)



