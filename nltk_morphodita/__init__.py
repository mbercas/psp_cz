# __init__.py
#
# Morphodita exetension for NLTK
#
# Copyright (C) 2019 - Manuel Berrocal
# Author: Manuel Berrocal
#
# URL: <https://github.com/mbercas/psp_cz/tree/master/nltk_morphodita>

"""
Compatibility exetensions for NLTK for Morphodita dictiorary and tagger.
"""

from .MorphoditaNltkTokenizer import MorphoditaNltkTokenizer
from .MorphoditaNltkTokenizer import MorphoditaNltkTokenizerException
from .MorphoditaNltkCorpusReader import MorphoditaNltkCorpusReader

__all__ = ['MorphoditaNltkTokenizer', 'MorphoditaNltkTokenizerException',
           'MorphoditaNltkCorpusReader']

morphodita_tokenizer = MorphoditaNltkTokenizer()
