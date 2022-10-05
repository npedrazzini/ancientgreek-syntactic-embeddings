#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
--------------------
Merges parse trees generated from xml-to-parenth-agdt.py and xml-to-parenth-proiel.py
--------------------

Author: Nilo Pedrazzini (unless otherwise stated)

How to run:
    $ python mergetrees.py

Before running this script, you need to:
    - have run xml-to-parenth-agdt.py and xml-to-parenth-proiel.py as appropriate

Returns:
    ./outputs/nameofmodel/trees.txt (file): contains merged outparenth-proiel/agdt.txt files
    

"""

from glob import glob

modelname = input('Enter name of model (i.e. name of folder with preprocessed texts: ')

finaltrees = open('./outputs/{}/trees.txt'.format(modelname), 'w')

alltrees = glob('./outputs/{}/outparenth*.txt'.format(modelname))

for tree in alltrees:
    with open(tree, 'r') as intxt:
        for line in intxt.readlines():
            finaltrees.write(line)
