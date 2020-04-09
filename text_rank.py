import numpy as np
import pandas as pd
import nltk
from sklearn.metrics.pairwise import cosine_similarity
import codecs
import networkx as nx
from nltk.corpus import stopwords
import re
import time

from typing import List, Callable, Dict

nltk.download('punkt')
nltk.download('stopwords')

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

stop_words = set(stopwords.words('english'))

word_vectors: Dict[str, np.array] = None

glove_file_path = "glove.6B/glove.6B.50d.txt"


def load_word_vectors():
    
    global word_vectors
    word_vectors = {}

    with open(glove_file_path, encoding = "utf-8") as f:        
        for line in f:
            values = line.split(" ")
            word = values[0]
            coefs = np.asarray(values[1:],dtype="float32")
            word_vectors[word] = coefs
        

def sanitize_sentence(sentence: str) -> List[str]:
    # Remove weird symbols.
    #sentence = re.sub(r"[^a-zA-Z\s]","", sentence)
    # Remove stop words
    words = word_tokenize(sentence)
    lowercase_words = map(lambda x: x.lower(), words)
    no_punctuation_words = filter(lambda x: x.isalpha(), lowercase_words)
    words = [w for w in no_punctuation_words if not w in stop_words]
    return words

def bag_of_words(sentences: List[List[str]]) -> np.matrix:

    unique_words = {word for sentence in sentences for word in sentence}
    word_to_index = {word: index for index, word in enumerate(unique_words)}

    sentence_embeddings = np.asmatrix(np.zeros((len(sentences), len(unique_words))))
    
    for sent_index, sentence in enumerate(sentences):
        for word in sentence:
            sentence_embeddings[sent_index, word_to_index[word]] = 1
    
    return sentence_embeddings

def get_sentence_embeddings(sentences: List[List[str]], review_lengths:List[int]) -> np.matrix:
    
    if(word_vectors == None):
        raise Exception("word_vectors not loaded must call load_word_vectors()")

    sentence_ventors = []

    for i in sentences:
        if i:
            v = sum([word_vectors.get(w, np.zeros((50,))) for w in i])/len(i)
        else:
            v = np.zeros((50,)) 
        sentence_ventors.append(v)
    
    return np.asmatrix(sentence_ventors)



def get_similarity_graph(sentence_embeddings: List[np.matrix], review_lengths) -> np.matrix:
    # G[i, j] is the measure of how close i,j are to eachother
    n_sentences = sentence_embeddings.shape[0]
    similarity_graph = np.asmatrix(np.zeros((n_sentences, n_sentences)))

    for i, sentence_vect_1 in enumerate(sentence_embeddings):
        for j, sentence_vect_2 in enumerate(compare_sentence_embeddings):
            if i!=j:
                similarity_graph[i, j] = cosine_similarity(sentence_vect_1,sentence_vect_2)[0,0]
    

    return similarity_graph

def rank(similarity_graph: np.matrix) -> List[int]:
    nx_graph = nx.from_numpy_matrix(similarity_graph)
    nx.from_numpy_array()
    scores = nx.pagerank(nx_graph)
    return scores

   

def get_top_n_sentences(rank, orig_review_sentences, n):
    top_n = [index for index, score in sorted(rank.items(), key = lambda tp: tp[1], reverse = True)[:n]]
    return [orig_review_sentences[index] for index in sorted(top_n)]


if __name__ == "__main__":

    load_word_vectors()

    review_paths = ["album-review-pitchfork.txt", "album-review-guardian.txt","album-review-nme.txt","album-review-resident-advisor.txt"]

    all_review_sentences = []
    review_lengths = []

    for path in review_paths:
        
        with codecs.open(path, "r", "utf-8-sig") as f:
            review = f.read()

        sentences = sent_tokenize(review)
        all_review_sentences.extend(sentences)
        review_lengths.append(len(sentences))

    sanitized_sentences = [sanitize_sentence(sentence) for sentence in all_review_sentences]
    sentence_embeddings = get_sentence_embeddings(sanitized_sentences)

    similarity_graph = get_similarity_graph(sentence_embeddings, review_lengths)

    rank(similarity_graph)

    sentence_ranks = rank(page_rank_graph, review_lengths)
    print("\n".join(get_top_n_sentences(sentence_ranks, all_review_sentences, 5)))