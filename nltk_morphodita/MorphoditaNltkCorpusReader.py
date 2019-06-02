
from .MorphoditaNltkTokenizer import *
from nltk.corpus.reader.tagged import TaggedCorpusReader, TaggedCorpusView
from nltk.corpus.reader.util import read_blankline_block
import re


class MorphoditaNltkCorpusReader(TaggedCorpusReader):
    """
    Reader for corpora that consist of plaintext documents.  Paragraphs
    are assumed to be split using blank lines.  Sentences and words can
    be tokenized using the Morphodita tokenizer passed in the constructor.
    """
    def __init__(self,
                 root,
                 fileids,
                 tokenizer,
                 para_block_reader=read_blankline_block):
        """
        Construct a new plaintext corpus reader for a set of documents
        located at the given root directory.  Example usage:

            >>> root = './'
            >>> reader = MorphoditaNltkCorpusReader(root, '.*\.txt', morphodita_tokenizer) # doctest: +SKIP

        :param root: The root directory for this corpus.
        :param fileids: A list or regexp specifying the fileids in this corpus.
        :param tokenizer: The Morphodita tokenizer.
        :param para_block_reader: The block reader used to divide the
            corpus into paragraph blocks.
        """
        self.tokenizer = tokenizer
        self._sep ='/'
        
        TaggedCorpusReader.__init__(self, root, fileids,
                                    word_tokenizer=tokenizer,
                                    sent_tokenizer=tokenizer)
        self._para_block_reader=para_block_reader


    def _words(self, fileids):
        """
        :return: the given file(s) as a list of words and punctuation symbols.
        :rtype: generator(str)
        """
        if type(fileids) == str:
            fileids = [fileids]
        for fileid in fileids:
            for w in self.tokenizer.tokenize(self.raw(fileid)):
                yield w
        
    def words(self, fileids):
        """
        :return: the given file(s) as a list of words and punctuation symbols.
        :rtype: list(str)
        """
        return list(self._words(fileids))

    def _sents(self, fileids):
        """
        :return: the given file(s) as a genertor of
            sentences or utterances, each encoded as a list of word
            strings.
        :rtype: generator(list(str))
        """
        if type(fileids) == str:
            fileids = [fileids]
        for fileid in fileids:
            for s in self.tokenizer.tokenize_sents(self.raw(fileids)):
                yield s

    
    def sents(self, fileids):
        """
        :return: the given file(s) as a list of
            sentences or utterances, each encoded as a list of word
            strings.
        :rtype: list(list(str))
        """
        return list(self._sents(fileids))
        
    def _tagged_words(self, fileids, lemma=False):
        """
        :return: the given file(s) as a list of tagged
            words and punctuation symbols, encoded as tuples
            ``(word,tag)``.
        :rtype: generator(tuple(str,str))

        :param lemma: If true, then use word lemmas instead of word strings.
        """
        if type(fileids) == str:
            fileids = [fileids]
        for fileid in fileids:
            for w in self.tokenizer.lemmatize(self.raw(fileid)):
                if lemma:
                    yield (w[2],w[1])
                else:
                    yield (w[0],w[1])
                    

    def tagged_words(self, fileids, lemma=False):
        """
        :return: the given file(s) as a list of tagged
            words and punctuation symbols, encoded as tuples
            ``(word,tag)``.
        :rtype: list(tuple(str,str))

        :param lemma: If true, then use word stems instead of word strings.
        """
        return [w for w in self._tagged_words(fileids, lemma)]
    

    def _tagged_sents(self, fileids, lemma=False):
        """
        :return: the given file(s) as a generator of sentences or utterances, 
            each encoded as a list of tagged words and punctuation symbols, 
            encoded as tuples ``(word,tag)``.
        :rtype: generator(tuple(str,str))

        :param lemma: If true, then use word stems instead of word strings.
        """
        if type(fileids) == str:
            fileids = [fileids]
        for fileid in fileids:
            for s in self.tokenizer.pos_tag_sents(self.raw(fileids)):
                yield s


    def tagged_sents(self, fileids, lemma=False):
        """
        :return: the given file(s) as a list of sentences or utterances, 
            each encoded as a list of tagged words and punctuation symbols, 
            encoded as tuples ``(word,tag)``.
        :rtype: list(tuple(str,str))

        :param lemma: If true, then use word stems instead of word strings.
        """
        return [s for s in self._tagged_sents(fileids, lemma)]
