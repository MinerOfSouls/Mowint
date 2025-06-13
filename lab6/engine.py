import scipy as sci
import scipy.sparse as sparse
import re
import json
import numpy as np
from stopwords import stop_words
from collections import Counter
from tqdm import tqdm

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

    def process_query(self, query, k):
        pass

class Engine(AbstractEngine):
    def __init__(self, matrix: str, terms: str, files: str, mode: int):
        super().__init__(terms, files)
        self.mode = mode
        if mode == 1:
            self.matrix = sci.sparse.csc_array(sci.sparse.load_npz(matrix), dtype=np.float32)
        else:
            self.matrix = sci.sparse.csr_array(sci.sparse.load_npz(matrix), dtype=np.float32)
    
    def __tokenize(self, query):
        split = [w.group(0).lower() for w in re.finditer(word_pattern, query) if w.group(0).lower() not in stop_words]
        counts = Counter(split)
        data = []
        coords = ([], [])
        for word in counts.keys():
            if word in self.terms_reverse.keys():
                data.append(counts[word])
                coords[0].append(self.terms_reverse[word])
                coords[1].append(0)
        return sci.sparse.csr_array((data, coords), shape=(self.word_number,1), dtype=np.float32)
    

    def __process_query_basic(self, query, k):
        token = self.__tokenize(query)
        tn = sci.sparse.linalg.norm(token)
        norms = sci.sparse.linalg.norm(self.matrix, axis=0)
        dot = token.T.dot(self.matrix)
        correlation = dot/(tn*norms)
        correlation = correlation.tocsr()
        values = correlation.data      # the nonzero values
        indices = correlation.indices
        l = list(zip(values, indices))
        l.sort(reverse=True)
        result = []
        for c, i in l[:k]:
            result.append((self.file_reference[str(i)], c))
        return result
    
    def __proces_query_normalised(self, query, k):
        token = self.__tokenize(query)
        print(token)
        token = token / sci.sparse.linalg.norm(token)
        correlation = np.absolute(token.T.dot(self.matrix))
        correlation = correlation.tocsr()
        values = correlation.data      # the nonzero values
        indices = correlation.indices
        l = list(zip(values, indices))
        l.sort(reverse=True)
        result = []
        for c, i in l[:k]:
            result.append((self.file_reference[str(i)], c))
        return result
    
    def process_query(self, query, k):
        if self.mode == 1:
            return self.__process_query_basic(query, k)
        elif self.mode == 2:
            return self.__proces_query_normalised(query, k)

class SVDEngine(AbstractEngine):
    def __init__(self, matrix: str, terms: str, files: str, k):
        super().__init__(terms, files)
        pre_svd_matrix = sci.sparse.csr_array(sci.sparse.load_npz(matrix), dtype=np.float32)
        SVD = sci.sparse.linalg.svds(pre_svd_matrix, k)
        self.U = sparse.csr_array(SVD[0])
        self.VT = sparse.csr_array(SVD[2])
        self.S = sparse.diags(SVD[1]).tocsr()
        self.norms = sparse.linalg.norm(self.S @ self.VT)
        self.US = self.U.dot(self.S)
    
    def __tokenize(self, query):
        split = [w.group(0).lower() for w in re.finditer(word_pattern, query) if w.group(0).lower() not in stop_words]
        counts = Counter(split)
        data = []
        coords = ([], [])
        for word in counts.keys():
            if word in self.terms_reverse.keys():
                data.append(counts[word])
                coords[0].append(self.terms_reverse[word])
                coords[1].append(0)
        return sci.sparse.csr_array((data, coords), shape=(self.word_number,1), dtype=np.float32)
    
    
    def process_query(self, query, k):
        token = self.__tokenize(query)
        tn = sci.sparse.linalg.norm(token)
        dot = token.T @ self.U @ self.S @ self.VT
        correlation = dot/(tn*self.norms)
        correlation = correlation.tocsr()
        values = correlation.data      # the nonzero values
        indices = correlation.indices
        l = list(zip(values, indices))
        l.sort(reverse=True)
        result = []
        for c, i in l[:k]:
            result.append((self.file_reference[str(i)], c))
        return result


class PreCompSVDEngine(AbstractEngine):
    def __init__(self, matrix, terms, files):
        super().__init__(terms, files)
        self.matrix = sci.sparse.csr_array(sci.sparse.load_npz(matrix), dtype=np.float32)
    
    def process_query(self, query, k):
        token = self.__tokenize(query)
        tn = sci.sparse.linalg.norm(token)
        norms = sci.sparse.linalg.norm(self.matrix, axis=0)
        dot = token.T.dot(self.matrix)
        correlation = dot/(tn*norms)
        correlation = correlation.tocsr()
        values = correlation.data      # the nonzero values
        indices = correlation.indices
        l = list(zip(values, indices))
        l.sort(reverse=True)
        result = []
        for c, i in l[:k]:
            result.append((self.file_reference[str(i)], c))
        return result