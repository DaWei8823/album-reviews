
from collections import namedtuple
import dataclass
import networkx as nx
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
import numpy as np
import pandas as pd
import re
from sklearn.metrics.pairwise import cosine_similarity
import time
from typing import List, Callable, Dict, Tuple

nltk.download('punkt')
nltk.download('stopwords')

@dataclass
class ReviewSentence:
    publication:str
    raw_sentence:str
    sentence_vector:List[float]

    def __str__(self):
        return f"{raw_sentence} ({publication})"


class AlbumSummarizer:

    def __init__(self, word_vectors_file_path):
        self.stop_words = set(stopwords.words('english'))
        self.word_vectors_file_path = "glove.6B/glove.6B.50d.txt"
        self.word_vectors:Dict[str,np.array] = {}
        
    def load_word_vectors(self):
        """Loads the word vectors into memory. This method must be called before object can perform any analysis"""
        with open(self.word_vectors_file_path, encoding = "utf-8") as f:        
            for line in f:
                values = line.split(" ")
                word = values[0]
                coefs = np.asarray(values[1:],dtype="float32")
                self.word_vectors[word] = coefs

    def get_top_n_sentences_from_reviews(self, reviews:Dict[str,str], n) -> List[ReviewSentence]:
        """Gets the top sentences from a review based on how similarly they express the sentiments of reviews from other reviewers
        
        Args:
            reviews: a dictionary of the media outlet that published the review to the review text

            n: the number of sentences to return. Larger values will return more sentences, further down the 
            ranking with less relevance to the entire body of reviews
        
        Returns:
            A list of ReviewSentence
        """
        if(not self.word_vectors):
            raise Exception("word_vectors not loaded must call load_word_vectors()")

        review_sentences = self._get_review_sentences(reviews)
        review_sentences_by_rank_desc = AlbumSummarizer._get_review_sentences_by_rank(review_sentences)
        return review_sentences[0:min(len(review_sentences_by_rank_desc), n)]

    def _get_review_sentences(self, review:Dict[str,str]) -> List[ReviewSentence]:
        return [ReviewSentence(publication, sentence, self._get_sentence_embedding(sentence))
            for publication, text in review.items() 
            for sentence in sent_tokenize(text)]

    def _get_sentence_embedding(self, sentence: str) -> List[float]:
        words = self._sanitize_sentence(sentence)
        return np.zeros((50,)) if len(words) == 0
        else sum([self.word_vectors.get(w, np.zeros((50,))) for w in words])/len(words)

    def _sanitize_sentence(self, sentence: str) -> List[str]:
        words = word_tokenize(sentence)
        lowercase_words = map(lambda x: x.lower(), words)
        no_punctuation_words = filter(lambda x: x.isalpha(), lowercase_words)
        words = [w for w in no_punctuation_words if not w in self.stop_words]
        return words

    @staticmethod
    def _get_review_sentences_by_rank(review_sentences: List[ReviewSentence]) -> List[ReviewSentence]:
        similarity_graph = AlbumSummarizer._get_similarity_graph(review_sentences)
        ranked_sentences = AlbumSummarizer._rank_sentences(similarity_graph)
        return [review_sentences[i] for i in sorted(enumerate(ranked_sentences), lambda tup: tup[1], reverse= true)]

    @staticmethod
    def _get_similarity_graph(review_sentences: List[ReviewSentence]) -> np.matrix:
        # G[i, j] is the measure of how close i,j are to eachother
        n_sentences = len(review_sentences)
        similarity_graph = np.asmatrix(np.zeros((n_sentences, n_sentences)))
        embeddings = [rs.sentence_vector for rs in review_sentences]
        
        for i in range(n_sentences):
            for j in range(n_sentences):
                rs1 = review_sentences[i]
                rs2 = review_sentences[j]
                if rs1.publication != rs2.publication:
                    similarity_graph[i, j] = cosine_similarity(rs1.sentence_vector, rs2.sentence_vector)[0,0]   

        return similarity_graph

    @staticmethod
    def _rank_sentences(similarity_graph: np.matrix) -> List[int]:
        nx_graph = nx.from_numpy_matrix(similarity_graph)
        scores = nx.pagerank(nx_graph)
        return scores