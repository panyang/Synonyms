#!/usr/bin/env python
# -*- coding: utf-8 -*-
#===============================================================================
#
# Copyright (c) 2017 <> All Rights Reserved
#
#
# File: /Users/hain/ai/Synonyms/synonyms/__init__.py
# Author: Hai Liang Wang
# Date: 2017-09-27
#
#===============================================================================

"""
Chinese Synonyms for Natural Language Processing and Understanding.
"""
from __future__ import print_function
from __future__ import division

__copyright__ = "Copyright (c) 2017 . All Rights Reserved"
__author__    = "Hu Ying Xi<>, Hai Liang Wang<hailiang.hl.wang@gmail.com>"
__date__      = "2017-09-27"


import os
import sys
curdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(curdir)

if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding("utf-8")
    # raise "Must be using Python 3"

import gzip
import thulac # http://thulac.thunlp.org/
from collections import defaultdict
wn_raw_data=gzip.open(os.path.join(curdir, 'data', 'words.nearby.gz'),'rt', encoding='utf-8', errors = "ignore")

_vocab = defaultdict(lambda: [[], []])
_size = 0
_thulac = thulac.thulac() #默认模式

def add_word_to_vocab(word, nearby, nearby_score):
    '''
    Add word into vocab by word, nearby lis and nearby_score lis
    '''
    global _size
    if not word is None:
        _vocab[word] = [nearby, nearby_score]
        _size += 1

def _build_vocab():
    '''
    Build vocab
    '''
    c = None # current word
    w = []   # word nearby 
    s = []   # score of word nearby
    for v in wn_raw_data.readlines():
        v = v.strip()
        if v is None or len(v) == 0: continue
        if v.startswith("query:"):
            add_word_to_vocab(c, w, s)
            o = v.split(":")
            c = o[1].strip()
            w, s = [], []
        else:
            o = v.split()
            assert len(o) == 2, "nearby data should have text and score"
            w.append(o[0].strip())
            s.append(float(o[1]))
    add_word_to_vocab(c, w, s) # add the last word
    print(">> Synonyms vocabulary size: %s" % _size)

# build on load
print(">> Synonyms on loading ...")
_build_vocab()

def nearby(word):
    '''
    Nearby word
    '''
    return _vocab[word]

def _segment_words(sen):
    '''
    segment words
    '''
    text = _thulac.cut(sen, text=True)  #进行一句话分词
    words, tags = [], []
    data = [x.rsplit('_', 1) for x in text.split()]
    for _ in data:
        assert len(_) == 2, "seg len should be 2"
        words.append(_[0])
        tags.append(_[1])
    return words, tags

def _similarity(w1, t1, w2, t2, explain = False):
    '''
    compute similarity
    '''
    vocab_space = dict()
    
    for (k,v) in enumerate(t2):
        vocab_space[w2[k]] = 1
        for k2,v2 in enumerate(nearby(w2[k])[0]):
            vocab_space[v2] = nearby(w2[k])[1][k2]
        
    if explain: print(vocab_space)
    total = 0
    overlap = 0
    for (k,v) in enumerate(t1):
        if v.startswith("n") or v.startswith("v"): # 去停，去标，去副词、形容词、代词 etc.
            total += 1
            if w1[k] in vocab_space:
                # overlap += word2_weight_vocab[word1[k]]
                overlap += 1 # set 1 to all included word
    return float("{:1.2f}".format(overlap/total))

def compare(s1, s2):
    '''
    compare similarity
    '''
    w1, t1 = _segment_words(s1)
    w2, t2 = _segment_words(s2)
    return max(_similarity(w1, t1, w2, t2), _similarity(w2, t2, w1, t1))

def main():
    print("人脸", nearby("人脸"))
    print("识别", nearby("识别"))
    print("OOV", nearby("NOT_EXIST"))

if __name__ == '__main__':
    main()