import os
import re
import json
from stopwords import stop_words
from collections import Counter
import time
import scipy as sci
import numpy as np
from tqdm import tqdm
import scipy.sparse as sparse

extra_exclusions = {"To", "From", "Subject", "enron", "com"}

word_pattern = re.compile(r"(?!\b\w*(\w)\1{4,}\w*\b)\b[A-Z]?[a-z]{1,22}\b")

def get_all_words(filename):
    f = open(filename, errors="ignore")
    text_to_split = ""
    for line in f:
        if (not line.startswith("Message-ID") and not line.startswith("Date") and not line.startswith("Mime")
            and not line.startswith("Content-Type") and not line.startswith("Content-Transfer-Encoding")
            and not line.startswith("X-Folder") and not line.startswith("X-Origin") and not line.startswith("X-FileName")
            and not line.startswith("X-cc") and not line.startswith("X-bcc") and not line.startswith("X-From") 
            and not line.startswith("X-To")
        ):
            text_to_split += line
    f.close()
    split = [w.group(0).lower() for w in re.finditer(word_pattern, text_to_split) if w.group(0).lower() not in stop_words and w.group(0) not in extra_exclusions]
    return dict(Counter(split))

def create_bag_of_words(directory):
    main_dict = set()
    file_counts = {}
    i = 0
    avg = 0
    main_start = time.process_time()
    for root, directories, files in os.walk(directory):
        for file in files:
            filename = os.path.join(root, file)
            start = time.process_time()
            try:
                f_d = get_all_words(filename)
            except UnicodeDecodeError:
                continue
            end = time.process_time()
            avg = (avg*i + (end - start))/(i+1)
            i+=1
            print(i, filename)
            main_dict.update(f_d.keys())
            file_counts[filename] = f_d
    m_list = list(main_dict)
    main_end = time.process_time()
    t = open("terms.json", "w+")
    fv = open("file_vectors.json", "w+")
    print(f"Procesed {i} in {main_end-main_start}. Average time {avg}")
    save_s = time.process_time()
    json.dump(m_list, t)
    json.dump(file_counts, fv)
    t.close()
    fv.close()
    save_e = time.process_time()
    print(f"Saving data took {save_e-save_s}")

def create_pre_compute_file_vectors(terms, vectors):
    t = open(terms)
    v = open(vectors)
    term_list = json.load(t)
    ind = {term_list[i]:i for i in range(len(term_list))}
    v_dict = json.load(v)
    compressed = {p:{} for p in v_dict.keys()}
    for key in v_dict.keys():
        for word in v_dict[key].keys():
            compressed[key][ind[word]] = v_dict[key][word]
    t.close()
    v.close()
    b = open("vectors_computed.json", "w+")
    json.dump(compressed, b)
    b.close()

def compute_matrix(terms, pre_vectors):
    t = open(terms)
    a = json.load(t)
    t.close()
    term_amount = len(a)
    a.clear()
    i = 0
    v = open(pre_vectors)
    vectors_dict = json.load(v)
    v.close()
    #calculating iwf
    N = len(vectors_dict.keys())
    print(term_amount)
    iwf = {i:0 for i in range(term_amount)}
    for file in vectors_dict.keys():
        for w in vectors_dict[file].keys():
            iwf[int(w)] += 1
    
    for i in range(term_amount):
        iwf[i] = np.log(N/iwf[i])

    for file in vectors_dict.keys():
        for w in vectors_dict[file].keys():
            vectors_dict[file][w] *= iwf[int(w)]
    iwf.clear()
    # putting togheter the matrix
    f_dict = {}
    arrays = []
    for file in tqdm(vectors_dict.keys()):
        f_dict[i] = file
        i+=1
        coors = ([int(k) for k in vectors_dict[file].keys()],[0 for _ in range(len(vectors_dict[file].keys()))])
        data = list(vectors_dict[file].values())
        arrays.append(sci.sparse.coo_array((data, coors), shape=(term_amount,1)))
    big = sci.sparse.block_array([arrays])
    sci.sparse.save_npz("big", big)
    f = open("files.json", "w+")
    json.dump(f_dict, f)
    f.close()

def normalise_matrix(matrix):
    matrix = sci.sparse.load_npz(matrix)
    norms = sci.sparse.linalg.norm(matrix, axis=0)
    matrix = matrix / norms
    sci.sparse.save_npz("lab6/big_normalised", matrix)

def make_pre_svd(matrix):
    pre_svd_matrix = sci.sparse.csr_array(sci.sparse.load_npz(matrix), dtype=np.float32)
    SVD = sci.sparse.linalg.svds(pre_svd_matrix, 1000)
    U = sparse.csr_array(SVD[0])
    VT = sparse.csr_array(SVD[2])
    S = sparse.diags(SVD[1]).tocsr()
    m = U @ S @ VT
    sparse.save_npz("svd",m)

def preproces_data(directory):
    create_bag_of_words(directory)
    create_pre_compute_file_vectors("terms.json", "file_vectors.json")
    compute_matrix("terms.json", "vectors_computed.json")
    normalise_matrix("big.npz")
    make_pre_svd("big.npz")

"""if __name__ == "__main__":
    preproces_data("maildir")"""

make_pre_svd("big.npz")