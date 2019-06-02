# -*- coding: utf-8 -*-
# Natural Language Toolkit Extensions: Interface to the Morphodita Tokenizer
#
# Copyright (C) 2019 Manuel Berrocal
# Authors: Manuel Berrocal
# Contributors: Martina Berrocal
#
# URL: <https://github.com/mbercas/psp_cz>
# For license information, see LICENSE.TXT

from nltk.tokenize.api import TokenizerI
from ufal.morphodita import *
from pathlib import Path
import os

DICT_FILENAME = os.path.join(os.path.dirname(__file__), 'czech-morfflex-161115.dict')
TAGGER_FILENAME = os.path.join(os.path.dirname(__file__), 'czech-morfflex-pdt-161115.tagger')

from nltk.corpus.reader import concat, TaggedCorpusReader

class MorphoditaNltkTokenizerException(Exception):
    """MorphoditaNtlkTokenizer exceptions"""
    pass

class MorphoditaNltkTokenizer(TokenizerI):
    """
    A class for word tokenization using Morphodita tokenizer model
    """
    def __init__(self, repp_dir='./', encoding='utf8'):
        # Set an encoding for the input strings.
        self.encoding = encoding

        self.dict_path = DICT_FILENAME
        self.tagger_path = TAGGER_FILENAME

       
        self.morpho = Morpho.load(self.dict_path)
        if None == self.morpho:
            raise MorphoditaNltkTokenizerException(
                "ERROR: Did not load the dictiorary")
        
        
        self.tagger = Tagger.load(self.tagger_path)
        
        self.forms = Forms()
        self.tokenRanges = TokenRanges()
        self.taggedLemmas = TaggedLemmas()

        self.tokenizer = self.morpho.newTokenizer()
        if self.tokenizer == None:
            raise MorphoditaNltkTokenizerException(
                "ERROR: could not open the tokenizer")

        self.text = ""

    def tokenize(self, text):
        if text == "":
            #raise ValueError("Text field is empty")
            self._init()
            
        self._tokenize(text)

        return self.tok_words

    def tokenize_sents(self, text):
        if text == "":
            raise ValueError("Text field is empty")

        self._tokenize(text)
        
        for sen in self.tok_sents:
            yield sen

    
    def span_tokenize(self, text):
        if text == "":
            raise ValueError("Text field is empty")

        self._tokenize(text)

        for word in self.tok_words_pos:
            yield word

    def span_tokenize_sents(self, text):
        if text == "":
            raise ValueError("Text field is empty")

        self._tokenize(text)

        for sen in self.tok_sens_pos:
            yield sen
            
    def _init(self):
        self.tok_words = []
        self.tok_words_pos = []
        self.tok_lemmas = []
        self.tok_sents = []
        self.tok_sents_pos = []
        self.tag_words = []
        self.tag_sents = []
            
    def _tokenize(self, text, tag=False):
        
        self.tokenizer.setText(text)

        self._init()

        sent_start = 0
        sent_end = 0
        sent = []
        sent_pos = []
        sent_tag = []
        while self.tokenizer.nextSentence(self.forms, self.tokenRanges):
            self.tagger.tag(self.forms, self.taggedLemmas)
            for i, (taggedLemma, tokenRange) in enumerate(zip(self.taggedLemmas, self.tokenRanges)):

                token_range_end = tokenRange.start + tokenRange.length

                word = f"{text[tokenRange.start : token_range_end]}"
                word_range = (tokenRange.start, token_range_end)
                
                self.tok_lemmas.append(taggedLemma.lemma)
                self.tag_words.append(taggedLemma.tag)
                self.tok_words.append(word)
                self.tok_words_pos.append(word_range)
                
                if i == 0:
                    sent_start = tokenRange.start
                    sent = [word]
                    sent_pos = [word_range]
                    sent_tag = [(word, taggedLemma.tag)]
                else:
                    sent.append(word)
                    sent_pos.append(word_range)
                    sent_tag.append((word, taggedLemma.tag))

                if i+1 == len(self.taggedLemmas):
                    self.tok_sents.append(sent)
                    self.tok_sents_pos.append(sent_pos)
                    self.tag_sents.append(sent_tag)

    def pos_tag(self, text):
        if text == "":
            raise ValueError("Text field is empty")

        self._tokenize(text)

        for word_tag in zip(self.tok_words, self.tag_words):
            yield word_tag

    def pos_tag_sents(self, text):
        if text == "":
            raise ValueError("Text field is empty")

        self._tokenize(text)

        for word_tag in self.tag_sents:
            yield word_tag

    def lemmatize(self, text):
        if text == "":
            raise ValueError("Text field is empty")

        self._tokenize(text)

        for lemma in zip(self.tok_words, self.tag_words, self.tok_lemmas):
            yield lemma
