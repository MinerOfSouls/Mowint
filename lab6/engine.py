import scipy as sci
import re
import json
import numpy as np
from stopwords import stop_words
from collections import Counter

word_pattern = re.compile(r"(?!\b\w*(\w)\1{4,}\w*\b)\b[A-Z]?[a-z]{1,22}\b")

class AbstractEngine:
    def __init__(self, terms: str, files: str):
        f = open(files)
        self.file_reference = json.load(f)
        f.close()
        t = open(terms)
        self.terms = json.load(t)
        t.close()
        self.word_number = len(self.terms)
        self.file_number = len(self.file_reference)
        self.terms_reverse = {self.terms[i]:i for i in range(self.word_number)}

    def __tokenize(self, query):
        split = [w.group(0).lower() for w in re.finditer(word_pattern, query) if w.group(0).lower() not in stop_words]
        counts = Counter(split)
        data = []
        coords = ([], [])
        i = 0
        for word in counts.keys():
            if word in self.terms_reverse.keys():
                data.append(counts[word])
                coords[0].append(i)
                coords[1].append(0)
        return sci.sparse.csr_array((data, coords), shape=(self.word_number,1), dtype=np.float32)
    
    def process_query(self, query, k):
        pass

class Engine(AbstractEngine):
    def __init__(self, matrix: str, terms: str, files: str, mode: int):
        super.__init__(self, terms, files)
        self.mode = mode

        self.matrix = sci.sparse.csr_array(sci.sparse.load_npz(matrix), dtype=np.float32)
    
    def __tokenize(self, query):
        split = [w.group(0).lower() for w in re.finditer(word_pattern, query) if w.group(0).lower() not in stop_words]
        counts = Counter(split)
        data = []
        coords = ([], [])
        i = 0
        for word in counts.keys():
            if word in self.terms_reverse.keys():
                data.append(counts[word])
                coords[0].append(i)
                coords[1].append(0)
        return sci.sparse.csr_array((data, coords), shape=(self.word_number,1), dtype=np.float32)
    
    def __process_query_basic(self, query, k):
        token = self.__tokenize(query)
        correlation = sci.sparse.csr_array((1, self.file_number), dtype=np.float32)
        for i in range(self.file_number):
            data = [1]
            coords = ([i], [0])
            select = sci.sparse.csr_array((data, coords), shape=(self.file_number,1))
            correlation[i] = np.dot(token.T, np.dot(self.matrix, select))
        indexes = np.argpartition(correlation, k)
        l = []
        for i in indexes:
            l.append((correlation[i], i))
        l.sort(reverse=True)
        result = []
        for c, i in l:
            result.append((self.file_reference[i], c))
        return result
    
    def __proces_query_normalised(self, query, k):
        token = self.__tokenize(query)
        token = token / sci.sparse.norm(token)
        correlation = np.absolute(np.dot(token.T, self.matrix))
        indexes = np.argpartition(correlation, k)
        l = []
        for i in indexes:
            l.append((correlation[i], i))
        l.sort(reverse=True)
        result = []
        for c, i in l:
            result.append((self.file_reference[i], c))
        return result
    
    def process_query(self, query, k):
        if self.mode == 1:
            return self.__process_query_basic(query, k)
        elif self.mode == 2:
            return self.__proces_query_normalised(query, k)

class SVDEngine(AbstractEngine):
    def __init__(self, matrix: str, terms: str, files: str, k):
        super.__init__(self, terms, files)
        pre_svd_matrix = sci.sparse.csr_array(sci.sparse.load_npz(matrix), dtype=np.float32)
        SVD = sci.sparse.linalg.svds(pre_svd_matrix, k)
        self.matrix = np.dot(np.dot(SVD[0], sci.sparse.sparse.diags(SVD[1]), SVD[2].T))
    
    def process_query(self, query, k):
        token = self.__tokenize(query)

