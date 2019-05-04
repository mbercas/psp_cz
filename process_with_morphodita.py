#!/usr/bin/env python3


from ufal.morphodita import *
from pathlib import Path
import sys
from collections import namedtuple
import re
import numpy as np
import pandas as pd


Tag = namedtuple('Tag', ['word', 'lemma', 'tag'])
FeaturesCounter = namedtuple('FeaturesCounter',
                             ['tokens',
                              'nouns', 'adjectives', 'adverbs', 'verbs_pf', 'verbs_past',
                              'ja_singular', 'ja_plural', 'ja',
                              'clovek_singular', 'clovek_plural'])

def tag_text(tagger, text):
    """Tag text with tagger passed as argument

    Returns a list of tags. 
    Each tag is a named tupple containing the original word being
    tagged, the lemma for that word and the resulting tag.
    """

    output_list = []
    forms = Forms()
    tokens = TokenRanges()
    lemmas = TaggedLemmas()
    lemmas_forms = TaggedLemmasForms()  

    tokenizer = tagger.newTokenizer()
    if tokenizer == None:
        print ("ERROR: could not open the tokenizer")
        sys.exit(-1)

    # Tag
    tokenizer.setText(text)

    t = 0
    while tokenizer.nextSentence(forms, tokens):
        tagger.tag(forms, lemmas)
        for i, (lemma,token) in enumerate(zip(lemmas,tokens)):

            output_list.append(Tag(word = text[token.start : token.start + token.length],
                                   lemma = lemma.lemma,
                                   tag = lemma.tag))
            """
            print('{}{}<token lemma="{}" tag="{}">{}</token>{}'.format(
                text[t : token.start],
                "<sentence>" if i == 0 else "",
                lemma.lemma,
                lemma.tag,
                text[token.start : token.start + token.length],
                "</sentence>" if i + 1 == len(lemmas) else ""))
            """
            t = token.start + token.length
    return output_list



def matches_tag(regex, tag):
    """Returns true is the regex matches the tag"""
    return (None != regex.match(tag.tag))

def is_noun(tag):
    """Returns true if the lemma is a noun"""
    regex = re.compile('N.*')
    return matches_tag(regex, tag)
            
def is_adjective(tag):
    """Returns true if the lemma is an adjective"""
    regex = re.compile('A.*')
    return matches_tag(regex, tag)

def is_adverb(tag):
    """Returns true if the lemma is an adverb"""
    regex = re.compile('D.*')
    return matches_tag(regex, tag)

def is_verb_present_or_future(tag):
    """Returns true if the lemma is a verb in present or future"""
    regex = re.compile('VB.*')
    return matches_tag(regex, tag)

def is_verb_past(tag):
    """Returns true if the lemma is a verb in past tense"""
    regex = re.compile('Vp.*')
    return matches_tag(regex, tag)

def is_pronoun_ja_singular(tag):
    """Returns true if the lemma is a singular pronoun ja"""
    if is_lemma(tag, 'já'):
        regex = re.compile("P..S.*")
        return matches_tag(regex, tag)
    else:
        return False

def is_pronoun_ja_plural(tag):
    """Returns true if the lemma is a plural pronoun ja"""
    if is_lemma(tag, 'já'):
        regex = re.compile("P..P.*")
        return matches_tag(regex, tag)
    else:
        return False

def is_clovek_plural(tag):
    """Returns true if the forms are plural forms of lemma člověk"""
    if is_lemma(tag, 'člověk'):
        regex = re.compile("N..P.*")
        return matches_tag(regex, tag)
    else:
        return False

def is_clovek_singular(tag):
    """Returns true if the forms are singular forms of lemma člověk"""
    if is_lemma(tag, 'člověk'):
        regex = re.compile("N..S.*")
        return matches_tag(regex, tag)
    else:
        return False

    
def is_lemma(tag, lemma):
    """Returns True is the tag contains the lemma passed as argument"""
    regex = re.compile(lemma)
    return (None != regex.match(tag.lemma))



def count_features(tag_list):
    """Returns a namedtuple with the counter for the features in the tag list"""

    # Initialize the counters
    noun_cnt = 0
    adjective_cnt = 0
    adverb_cnt = 0
    verb_present_or_future_cnt = 0
    verb_past_cnt = 0

    ja_cnt = 0
    ja_singular_cnt = 0
    ja_plural_cnt = 0
    clovek_plural_cnt = 0
    clovek_singular_cnt = 0

    # search for the features
    #
    for t in tag_list:
        # mutually exclusive search
        if is_noun(t):
            noun_cnt += 1
        elif is_adjective(t):
            adjective_cnt += 1
        elif is_adverb(t):
            adverb_cnt += 1
        elif is_verb_present_or_future(t):
            verb_present_or_future_cnt += 1
        elif is_verb_past(t):
            verb_past_cnt += 1
        elif is_pronoun_ja_plural(t):
            ja_plural_cnt += 1
        elif is_pronoun_ja_singular(t):
            ja_singular_cnt += 1
        
            
        if is_lemma(t, 'já'):
            ja_cnt += 1
        elif is_clovek_plural(t):
            clovek_plural_cnt += 1
        elif is_clovek_singular(t):
            clovek_singular_cnt += 1

    # Return the tuple
    return FeaturesCounter(tokens = len(tag_list),
                           nouns = noun_cnt,
                           adjectives = adjective_cnt,
                           adverbs = adverb_cnt,
                           verbs_pf = verb_present_or_future_cnt,
                           verbs_past = verb_past_cnt,
                           ja_singular = ja_singular_cnt,
                           ja_plural = ja_plural_cnt,
                           ja = ja_cnt,
                           clovek_singular = clovek_singular_cnt,
                           clovek_plural = clovek_plural_cnt)

def add_tagger_params_to_dataframe(df, tagger):
    """Takes a dataframe with the text and adds columns for the parameters"""
    # Add a new column for each new feature if it is not
    # already in the dataframe, initialize with NaN so we can easily
    # detect if a counter did not run
    #
    for field in FeaturesCounter._fields:
        if field not in df.columns:
            df[field] = np.nan

    # for each speach in the data set run it through the tagger and
    # add the counts to the column
    cnt = 0
    for idx, row in df.iterrows():
        # calculate the counters
        counters = count_features(
            tag_text(tagger, row.text))
        # Update the dataframe
        for field in counters._fields:
            df.loc[idx, field] = getattr(counters, field)

        if 0 ==  cnt % 100:
            print("processed {}/{} rows\n".format(cnt,df.shape[0]), end='')
        cnt += 1
        

    # return the extended data frame
    #
    return df
    
