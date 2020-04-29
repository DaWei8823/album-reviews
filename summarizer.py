
from dataclasses import dataclass
import networkx as nx
import nltk
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
    raw_sentence:str
    sentence_embedding:List[float]

#ToDo: rename 
class TextRankSummarizer:

    def __init__(self, word_embeddings_file_path:str):
        self.stop_words = set(stopwords.words('english'))
        self.word_embeddings_file_path = "glove.6B/glove.6B.50d.txt"
        self.word_embeddings:Dict[str,np.array] = {}
        
    def load_word_embeddings(self):
        """Loads the word vectors into memory. This method must be called before object can perform any analysis"""
        with open(self.word_embeddings_file_path, encoding = "utf-8") as f:        
            for line in f:
                values = line.split(" ")
                word = values[0]
                coefs = np.asarray(values[1:],dtype="float32")
                self.word_embeddings[word] = coefs

    def get_top_sentences(self, review_text:str, n:int = None) -> List[str]:
        """Gets the top sentences from a review based on how closely they express the sentiment of other sentences in the review
        
        Args:
            text: text of the review

            n: the number of sentences to return. Larger values will return more sentences, further down the 
            ranking with less relevance to the entire body of reviews. Default will return all sentences
        
        Returns:
            The top n sentences, ordered from most relevant to least relevant
        """
        if(not self.word_embeddings):
            raise Exception("word_embeddings not loaded must call load_word_embeddings()")

        review_sentences = self._get_review_sentences(review_text)

        similarity_graph = TextRankSummarizer._get_similarity_graph(review_sentences)
        ranked_sentences = TextRankSummarizer._rank_sentences(similarity_graph)
        
        review_sentences_by_rank_desc = [review_sentences[i] for i, score 
            in sorted(ranked_sentences.items(), key = lambda tup: tup[1], reverse= True)]

        end_bound = min(len(review_sentences_by_rank_desc), n) if n else len(review_sentences_by_rank_desc)
        return [rs.raw_sentence for rs in review_sentences_by_rank_desc[0:end_bound]]

    def _get_review_sentences(self, text:str) -> List[ReviewSentence]:
        return [ReviewSentence(sentence, self._get_sentence_embedding(sentence)) 
            for sentence in sent_tokenize(text)]

    def _get_sentence_embedding(self, sentence: str) -> List[float]:
        words = self._sanitize_sentence(sentence) 

        if len(words) == 0:
            return np.zeros((50,))
       
        return sum([self.word_embeddings.get(w, np.zeros((50,))) for w in words])/len(words)

    def _sanitize_sentence(self, sentence: str) -> List[str]:
        words = word_tokenize(sentence)
        lowercase_words = map(lambda x: x.lower(), words)
        no_punctuation_words = filter(lambda x: x.isalpha(), lowercase_words)
        words = [w for w in no_punctuation_words if not w in self.stop_words]
        return words

    @staticmethod
    def _get_similarity_graph(review_sentences: List[ReviewSentence]) -> np.matrix:
        # G[i, j] is the measure of how close i,j are to eachother
        n_sentences = len(review_sentences)
        similarity_graph = np.asmatrix(np.zeros((n_sentences, n_sentences)))

        for i in range(n_sentences):
            for j in range(n_sentences):
                if i != j:
                    rs1, rs2 = review_sentences[i], review_sentences[j]
                    similarity_graph[i, j] = cosine_similarity(
                        [rs1.sentence_embedding], 
                        [rs2.sentence_embedding])[0,0]

        return similarity_graph

    @staticmethod
    def _rank_sentences(similarity_graph: np.matrix) -> List[int]:
        nx_graph = nx.from_numpy_matrix(similarity_graph)
        scores = nx.pagerank(nx_graph)
        return scores