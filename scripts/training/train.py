#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
--------------------
Main script to train Ancient Greek node2vec models from parenthetical/parse trees
--------------------

Author: Nilo Pedrazzini. 'SuperGraph' method (merging all parse trees into one big network prior to training node2vec) is adapted
        from the technique described in Ragheb Al-Ghezi and Mikko Kurimo. 2020. Graph-based Syntactic Word Embeddings. 
        In Proceedings of the Graph-based Methods for Natural Language Processing (TextGraphs), pages 72–78, 
        Barcelona, Spain (Online). Association for Computational Linguistics. DOI: 10.18653/v1/2020.textgraphs-1.8

How to run:
    $ python train.py

Before running this script, you need to:
    - have run xml-to-parenth-agdt.py and xml-to-parenth-proiel.py as appropriate
    - have merged any outparenth.txt files under ./outputs/modelname/ by running mergetrees.py

Returns:
    ./outputs/nameofmodel/model (model): node2vec model

"""

from nltk import Tree
from networkx.algorithms.operators.all import compose_all
import networkx as nx
import pandas as pd
from tqdm import tqdm
from node2vec import Node2Vec as n2v

modelname = input('Enter name of the model (i.e. the folder with the preprocessed/parenthetical texts: ')

trees = './outputs/{}/trees.txt'.format(modelname)

listofss = []
with open(trees,'r') as intxt:
    for line in tqdm(intxt.readlines()):
        listofss.append(Tree.fromstring(line))

def tree2graph(t):
    lst = []
    G = nx.Graph() # for each t initialize a graph object
    for branch in t.productions(): # NLTK method to return the grammar productions, filtered by the left-hand side or the first item in the right-hand side.
        leaf = str(branch).split('->') # arrows are in the t.production object by NLTK
        row = leaf[1].strip().split(' ')
        for r in row:
            lst.append((leaf[0].strip(), r.strip("'")))

    G.add_edges_from(lst)
    return G


forcomposeall = []
for s in tqdm(listofss):
    news = tree2graph(s)
    forcomposeall.append(news)

print('Now composing_all...')

supergraph = compose_all(forcomposeall)
# supergraph = compose_all([tree2graph(s) for s in listofss])

options = {
    'node_color': 'green',
    'node_size': 500,
    'arrowstyle': '-|>',
    'arrowsize': 5,
}

print('Now n2v...')

g_emb = n2v(supergraph, dimensions=16) # train node2vec model based on graph trees

WINDOW = 5 # Node2Vec fit window
MIN_COUNT = 1 # Node2Vec min. count
BATCH_WORDS = 4 # Node2Vec batch words

print('Now g_emb.fit...')

mdl = g_emb.fit(
    vector_size = 16,
    window=WINDOW,
    min_count=MIN_COUNT,
    batch_words=BATCH_WORDS
)

emb_df = (
    pd.DataFrame(
        [mdl.wv.get_vector(str(n)) for n in supergraph.nodes()],
        index = supergraph.nodes
    )
)

mdl.wv.save_word2vec_format('./outputs/{}/min{}-n2v-model.txt'.format(modelname,str(WINDOW)), binary=False) # Also save the vectors only (easier to work with) - Not necessary, of course

# mdl.save('./outputs/{}/min{}-n2v-model'.format(modelname,str(WINDOW))) # save model (can be queried the same as w2v)