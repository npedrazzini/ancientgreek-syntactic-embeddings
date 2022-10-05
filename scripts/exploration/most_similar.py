#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from gensim.models import KeyedVectors
from gensim.test.utils import datapath

# Change following to path to your vectors (ending in 'model.txt')
w2vmodel = KeyedVectors.load_word2vec_format(datapath("./outputs/final_graph_all/win1-min1-n2v-vectors.txt"),binary=False)

# Add any words to find 15 most similar
# See normal gensim-implemented operations here: https://radimrehurek.com/gensim/models/keyedvectors.html

print('\n')
print('κακός')

print(w2vmodel.most_similar('κακός',topn=15))

print('\n')
print('πατήρ')

print(w2vmodel.most_similar('πατήρ',topn=15))