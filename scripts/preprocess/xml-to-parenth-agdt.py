#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
--------------------
Converts Ancient Greek treebanks in the AGDT format to parenthetical/parse tree
--------------------

Author: Nilo Pedrazzini (unless otherwise stated)

Converts Ancient Greek treebanks in the AGDT format to parenthetical/parse tree, without the dependency tag (needed as input to node2vec). 
NB: we use lemmas, not token forms, and we remove stopwords. Multiple empty parentheses are kept because they indicate 
an empty node and create a distance in the graph between words which would otherwise end up close to each other when in reality they aren't

How to run:
    $ python xml-to-parenth-agdt.py

Before running this script, you need to:
    - have all .xml treebanks in the AGDT format in a folder named 'AGDT_treebanks' under the main directory.
    - alternatively, you can customize the variable allagdt, as long as the latter is a list of paths to each xml file

Returns:
    outputs/ (dir): ./outputs/ folder where all models will be saved.
    outputs/modelname/ (dir): Dedicated folder under outputs/ where all outputs 
                                  from a specific test run will be saved.
    outputs/modelname/outparenth-agdt.txt (file): text file with one parenthetical tree per line (e.g. ( εἰσαπόλλυμι ( μικρός ) ( νή ( Ζεύς ) ) )))
    outputs/modelname/outstring-agdt.txt (file): text file with the same as the above, without parenthesis
    outputs/modelname/leftout-agdt.txt (file): text file with paths to all files which couldn't be processed because of some error
"""

from bs4 import BeautifulSoup
import re
from re import search
from glob import glob
from tqdm import tqdm
import os

modelname = input('Choose a name for your model: ')

if not os.path.exists('./outputs/{}'.format(modelname)):
    os.mkdir('./outputs/{}'.format(modelname))


# The list of stop-words, compiled by Alessandro Vatri based on the Perseus Hopper source, is available at https://figshare.com/articles/Ancient_Greek_stop_words/9724613.
# This list comes from the Perseus Hopper source [http://sourceforge.net/projects/perseus-hopper],
# found at "/sgml/reading/build/stoplists", though this only contained acute accents on the ultima.
# There has been added to this grave accents to the ultima of each.
# Perseus source is made available under the Mozilla Public License 1.1 (MPL 1.1) [http://www.mozilla.org/MPL/1.1/].
# 	__author__ = ['Kyle P. Johnson <kyle@kyle-p-johnson.com>']
# 	__license__ = 'GPL License.'
# Vatri: added support for tonos vs oxia acute accent
# Martina Astrid Rodda: added 'None'
# Nilo Pedrazzini added λέγω,'εἰμί#1','καί#1','οὕτω(ς)','γίγνομαι','ἔχω','εἰ#1',ὅτι#1, νῦν#1, νῦν, εἰς


STOPS_LIST = ['αὐτὸς',
            'αὐτός',
            'γε',
            'γὰρ',
            'γάρ',
            "δ'",
            'δαὶ',
            'δαὶς',
            'δαί',
            'δαίς',
            'διὰ',
            'διά',
            'δὲ',
            'δέ',
            'δὴ',
            'δή',
            'εἰ',
            'εἰμὶ',
            'εἰμί',
            'εἰς',
            'εἴμι',
            'κατὰ',
            'κατά',
            'καὶ',
            'καί',
            'μετὰ',
            'μετά',
            'μὲν',
            'μέν',
            'μὴ',
            'μή',
            'οἱ',
            'οὐ',
            'οὐδεὶς',
            'οὐδείς',
            'οὐδὲ',
            'οὐδέ',
            'οὐκ',
            'οὔτε',
            'οὕτως',
            'οὖν',
            'οὗτος',
            'παρὰ',
            'παρά',
            'περὶ',
            'περί',
            'πρὸς',
            'πρός',
            'σὸς',
            'σός',
            'σὺ',
            'σὺν',
            'σύ',
            'σύν',
            'τε',
            'τι',
            'τις',
            'τοιοῦτος',
            'τοὶ',
            'τοί',
            'τοὺς',
            'τούς',
            'τοῦ',
            'τὰ',
            'τά',
            'τὴν',
            'τήν',
            'τὶ',
            'τὶς',
            'τί',
            'τίς',
            'τὸ',
            'τὸν',
            'τό',
            'τόν',
            'τῆς',
            'τῇ',
            'τῶν',
            'τῷ',
            "ἀλλ'",
            'ἀλλὰ',
            'ἀλλά',
            'ἀπὸ',
            'ἀπό',
            'ἂν',
            'ἄλλος',
            'ἄν',
            'ἄρα',
            'ἐγὼ',
            'ἐγώ',
            'ἐκ',
            'ἐξ',
            'ἐμὸς',
            'ἐμός',
            'ἐν',
            'ἐπὶ',
            'ἐπί',
            'ἐὰν',
            'ἐάν',
            'ἑαυτοῦ',
            'ἔτι',
            'ἡ',
            'ἢ',
            'ἤ',
            'ὁ',
            'ὃδε',
            'ὃς',
            'ὅδε',
            'ὅς',
            'ὅστις',
            'ὅτι',
            'ὑμὸς',
            'ὑμός',
            'ὑπὲρ',
            'ὑπέρ',
            'ὑπὸ',
            'ὑπό',
            'ὡς',
            'ὥστε',
            'ὦ',
            'ξύν',
            'ξὺν',
            'σύν',
            'σὺν',
            'τοῖς',
            'τᾶς',
            'αὐτός',
            'γάρ',
            'δαί',
            'δαίς',
            'διά',
            'δέ',
            'δή',
            'εἰμί',
            'κατά',
            'καί',
            'μετά',
            'μέν',
            'μή',
            'οὐδείς',
            'οὐδέ',
            'παρά',
            'περί',
            'πρός',
            'σός',
            'σύ',
            'σύν',
            'τοί',
            'τούς',
            'τά',
            'τήν',
            'τί',
            'τίς',
            'τό',
            'τόν',
            'ἀλλά',
            'ἀπό',
            'ἐγώ',
            'ἐμός',
            'ἐπί',
            'ἐάν',
            'ὑμός',
            'ὑπέρ',
            'ὑπό',
            'λέγω',
            'εἰμί#1',
            'καί#1',
            'οὕτω(ς)',
            'γίγνομαι',
            'ἔχω',
            'εἰ#1',
            'ὅτι#1', 
            'νῦν#1', 
            'νῦν', 
            'εἰς'
            'None']


# If your treebanks are organized in subfolders, then you can use the following syntax instead (uncomment and comment relevant lines):
# gorman = glob('./TREEBANKS/gorman-treebank/*')
# papyri = glob('./TREEBANKS/papygreek-treebank/*')
# pedalion = glob('./TREEBANKS/pedalion-treebank/*')
# perseus = glob('./TREEBANKS/perseus-treebank/*')
# allagdt = gorman + papyri + pedalion + perseus
allagdt = glob('./AGDT_treebanks/*xml')

leftbehind = '' # we start a string containing the paths to all files which returned errors, to keep track of what's left behind

with open('./outputs/{}/outparenth-agdt.txt'.format(modelname), 'w') as outtxt: # This will be where the parenthetical parse trees will be written
    with open('./outputs/{}/outstring-agdt.txt'.format(modelname),'w') as outtxt2: # This will be where the above without the parentheses will be written
        for file in tqdm(allagdt):
            with open(file, 'r') as tei:
                # print('Now checking {}...'.format(file))
                soup = BeautifulSoup(tei, "lxml")
                sentences = soup.find_all('sentence')
                for sentence in sentences:
                    words = sentence.find_all('word')
                    # print(file)
                    # print(sentence.get('id'))
                    tokens = []
                    parenth = ''
                    depsall = 0
                    rootids = []
                    for word in words:
                        if str(word.get('head')) != '0': # Only to check if there are any dependants at all (some trees are one-token only)
                            depsall += 1
                        if str(word.get('head')) == '0': # Find out what the head is
                            # if word.get('relation') != 'parpred' and word.get('relation') != 'voc':
                            # rootid = word.get('id')
                            rootids.append(str('id' + str(word.get('id')) + 'id'))
                    # print('ROOTIDS',rootids)
                    if len(rootids) != 0:
                        bottoms = []
                        for word in words:
                            deps = sentence.find_all('word',attrs={"head": word.get('id')})
                            if len(deps) == 0:
                                if str(str('id' + str(word.get('id')) + 'id')) not in rootids: # to avoid taking a child like token id 1238559 as both root and bottom
                                    bottoms.append(str('id' + str(word.get('id')) + 'id'))
                        # print('bottoms',bottoms)
                        allrest = []
                        for word in words:
                            if str('id' + str(word.get('id')) + 'id') not in rootids and str('id' + str(word.get('id')) + 'id') not in bottoms:
                                allrest.append(str('id' + str(word.get('id')) + 'id'))
                        # print('allrest',allrest)
                        rootheads = []
                        for id in rootids:
                            idword = sentence.find('word',attrs={"id": id.split('id')[1]})
                            head = 'Root'
                            rootheads.append((head,id))
                        # print('ROOTHEADS',rootheads) 
                        bottomsheads = []
                        for id in bottoms:
                            # print(id)
                            idword = sentence.find('word',attrs={"id": id.split('id')[1]})
                            if idword.get('head') != '':
                                head = str('id' + str(idword.get('head')) + 'id')
                                bottomsheads.append((head,id))
                            else:
                                head = 'Root'
                                rootheads.append((head,id))
                            # print(bottomsheads)
                        # print('bottomsheads',bottomsheads)
                        allrestheads = []
                        for id in allrest:
                            idword = sentence.find('word',attrs={"id": id.split('id')[1]})
                            if idword.get('head') != '':
                                head = str('id' + str(idword.get('head')) + 'id')
                                allrestheads.append((head,id))
                            else:
                                head = 'Root'
                                rootheads.append((head,id))
                        # print('allrestheads',allrestheads)
                        final = rootheads + bottomsheads + allrestheads
                        result = {}
                        # print('final', final)
                        for i in final:
                            result.setdefault(i[0],[]).append(i[1])
                        # print(result)
                        # print('RESULT', result)
                        finalstring = ''
                        if depsall != 0:
                            # print('Now creating the final string')
                            finalstring += str('Root')
                            finalstring += ' ('
                            finalstring += ' '.join(result['Root'])
                            finalstring += ')'
                            result.pop('Root')
                            infin = 0
                            while len(result) != 0:
                                if infin != len(result):
                                    infin = len(result)
                                    # print(result)
                                    # print(sentence)
                                    ids = []
                                    for i in result:
                                        if search(i, finalstring):
                                            ids.append(i)
                                            finalstring = re.sub(str(i),str(str(i) + ' '.join('({})'.format(x) for x in result[i])), finalstring)
                                    for id in ids:
                                        result.pop(id)
                                else:
                                    break
                        if infin != len(result):
                            finalstring = re.sub('Root \(', '(', finalstring)
                            # print(finalstring)
                            words = sentence.find_all('word')
                            for word in words:
                                # print(word.get('lemma'))
                                try:
                                    # print(word.get('lemma'))
                                    pattern = re.compile("\[[0-9]+\]")
                                    if word.get('lemma') == '':
                                        finalstring = re.sub(str('id' + str(word.get('id')) + 'id'),'',finalstring)
                                    elif pattern.match(word.get('lemma')):
                                        finalstring = re.sub(str('id' + str(word.get('id')) + 'id'),word.get('artificial'),finalstring)
                                    elif word.get('postag').startswith('m'):
                                        finalstring = re.sub(str('id' + str(word.get('id')) + 'id'),'',finalstring)
                                    elif word.get('postag').startswith('x'):
                                        finalstring = re.sub(str('id' + str(word.get('id')) + 'id'),'',finalstring)
                                    elif word.get('postag').startswith('u'):
                                        finalstring = re.sub(str('id' + str(word.get('id')) + 'id'),'',finalstring)
                                    else:
                                        finalstring = re.sub(str('id' + str(word.get('id')) + 'id'),word.get('lemma'),finalstring)
                                except AttributeError:
                                    finalstring = re.sub(str('id' + str(word.get('id')) + 'id'),word.get('artificial'),finalstring)
                                except TypeError:
                                    finalstring = re.sub(str('id' + str(word.get('id')) + 'id'),word.get('artificial'),finalstring)
                            finalstring = re.sub('punc1',' ', finalstring)
                            finalstring = re.sub('\.',' ', finalstring)
                            finalstring = re.sub(',',' ', finalstring)
                            finalstring = re.sub(';',' ', finalstring)
                            finalstring = re.sub(' +',' ', finalstring)
                            # finalstring = re.sub('\) \)','))', finalstring) 
                            finalstring = re.sub('\(',' ( ', finalstring) 
                            finalstring = re.sub('\)',' ) ', finalstring) 
                            finalstring = re.sub('elliptic',' ', finalstring) 
                            finalstring = re.sub('\[','', finalstring)
                            finalstring = re.sub('\]','', finalstring)
                            finalstring = re.sub('[0-9]',' ', finalstring)
                            for word in STOPS_LIST:
                                finalstring = re.sub(' {} '.format(word),' ',finalstring)
                                finalstring = re.sub(' +',' ', finalstring)
                                finalstring = re.sub('\( \)','',finalstring)
                                finalstring = re.sub('\(\)','',finalstring)
                                finalstring = re.sub(' +',' ', finalstring)
                            finalstring = finalstring.strip()
                            finalstring = finalstring.split("\n")
                            finalstring = [line for line in finalstring if line.strip() != ""]
                            finalstring2 = ""
                            for line in finalstring:
                                finalstring2 += line + "\n"
                            # print('FINALSTRING', finalstring2)
                            outtxt.write(finalstring2)
                            stringonly = ' '.join(finalstring2.split('('))
                            stringonly = ' '.join(stringonly.split(')'))
                            stringonly = re.sub(' +',' ',stringonly)
                            outtxt2.write(stringonly)
                            outtxt2.write('\n')
                        else:
                            leftbehind += str(sentence.get('id'))
                            leftbehind += str(' ' + file + '\n')
                    else:
                        continue

with open('./outputs/{}/leftbehind-agdt.txt'.format(modelname), 'w') as outtxt:
    outtxt.write(leftbehind)