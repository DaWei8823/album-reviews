import numpy as np
import pandas as pd
import nltk
from sklearn.metrics.pairwise import cosine_similarity
import codecs
import networkx as nx
from nltk.corpus import stopwords
import re
import time

from typing import List, Callable, Dict, Tuple

nltk.download('punkt')
nltk.download('stopwords')

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

class AlbumSummarizer:

    def __init__(self, word_vectors_file_path):
        self.stop_words = set(stopwords.words('english'))
        self.word_vectors_file_path = "glove.6B/glove.6B.50d.txt"
        self.word_vectors:Dict[str,np.array] = {}

        
    def load_word_vectors(self):
        with open(self.word_vectors_file_path, encoding = "utf-8") as f:        
            for line in f:
                values = line.split(" ")
                word = values[0]
                coefs = np.asarray(values[1:],dtype="float32")
                self.word_vectors[word] = coefs

    def get_top_n_sentences_from_reviews(self, reviews:Dict[str,str], n) -> List[Tuple[str,str]]:
        sentences, review_endpoints = _get_sentences_and_review_endpoints(reviews)
        get_review_source = _get_review_source_callable(review_endpoints) 

        sanitized_sentences = [_sanitize_sentence(sentence) for sentence in all_review_sentences]
        sentence_embeddings = _get_sentence_embeddings(sanitized_sentences)                   
        similarity_graph = _get_similarity_graph(sentence_embeddings, get_review_source)
        sentence_ranks = rank_sentences(similarity_graph)

        return extract_top_sentences_and_source(sentence_ranks, sentences, get_review_source, n)

    def _get_sentence_embeddings(self, sentences: List[List[str]]) -> np.matrix:

        if(not word_vectors):
            raise Exception("word_vectors not loaded must call load_word_vectors()")

        sentence_ventors = []

        for i in sentences:
            if i:
                v = sum([self.word_vectors.get(w, np.zeros((50,))) for w in i])/len(i)
            else:
                v = np.zeros((50,)) 
            sentence_ventors.append(v)
        
        return np.asmatrix(sentence_ventors)


def _get_sentences_and_review_endpoints(review:Dict[str,str]) -> Tuple[List[str],Dict[str,int]]:
    all_sentences = []
    review_endpoints:Dict[str,int] = {}
    interval_endpoint = 0

    for source, text in reviews:
        sentences = sent_tokenize(text)
        all_sentences.extend(sentences)
        interval_endpoint = interval_endpoint + len(sentences)
        review_endpoints[source] = interval_endpoint
    
    return (all_sentences, review_endpoints)


def _get_review_source_callable(review_endpoints:Dict[str,int]):
    return lambda i: next([source for source, endpoint in review_endpoints if i < endpoint])


def _sanitize_sentence(sentence: str) -> List[str]:
    words = word_tokenize(sentence)
    lowercase_words = map(lambda x: x.lower(), words)
    no_punctuation_words = filter(lambda x: x.isalpha(), lowercase_words)
    words = [w for w in no_punctuation_words if not w in stop_words]
    return words


def _get_similarity_graph(sentence_embeddings: List[np.matrix], get_review_source:callable) -> np.matrix:
    # G[i, j] is the measure of how close i,j are to eachother
    n_sentences = sentence_embeddings.shape[0]
    similarity_graph = np.asmatrix(np.zeros((n_sentences, n_sentences)))

    for i, sentence_vect_1 in enumerate(sentence_embeddings):
        for j, sentence_vect_2 in enumerate(compare_sentence_embeddings):
            if get_review_source(i) != get_review_source(j):
                similarity_graph[i, j] = cosine_similarity(sentence_vect_1,sentence_vect_2)[0,0]   

    return similarity_graph


def _rank_sentences(similarity_graph: np.matrix) -> List[int]:
    nx_graph = nx.from_numpy_matrix(similarity_graph)
    scores = nx.pagerank(nx_graph)
    return scores


def _extract_top_sentences_and_source(rank, orig_review_sentences, get_review_source, n):
    top_n = [index for index, score in sorted(rank.items(), key = lambda tp: tp[1], reverse = True)[:n]]
    return [(orig_review_sentences[index], get_review_source(index)) for index in sorted(top_n)]


if __name__ == "__main__":
    review_paths = [("pitchfork","album-review-pitchfork.txt"), 
                     ("guardian", "album-review-guardian.txt"),
                     ("nme", "album-review-nme.txt"),
                     ("resident advisor","album-review-resident-advisor.txt")]

    reviews = {}

    for source, path in review_paths:        
        with codecs.open(path, "r", "utf-8-sig") as f:
            reviews[source] = f.read()
    
    summarizer = AlbumSummarizer("glove.6B/glove.6B.50d.txt")
    summarizer.load_word_vectors()
    
    top_sentences = summarizer.get_top_n_sentences_from_reviews(reviews, 5)
    
    summary = "\n".join(map(lambda sent, source: f"{sentence} {source}" ,top_sentences))

    print(summary)
