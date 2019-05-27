
from MorphoditaNltkTokenizer import *
from nltk.corpus.reader.tagged import TaggedCorpusReader, TaggedCorpusView
import re



# Create a new corpus by specifying the parameters
# (1) directory of the new corpus
# (2) the fileids of the corpus
# NOTE: in this case the fileids are simply the filenames.
#corpus_dir = '/mnt/c/Users/manuel/projects/working/psp_cz/psp2017/'


class MorphoditaNltkCorpusReader(TaggedCorpusReader):

    def __init__(self,
                 root,
                 fileids,
                 tokenizer):

        self.tokenizer = tokenizer
        self._sep ='/'
        
        TaggedCorpusReader.__init__(self, root, fileids,
                                    word_tokenizer=tokenizer,
                                    sent_tokenizer=tokenizer)

    def tagged_words(self, fileids):
        if type(fileids) == str:
            fileids = [fileids]
        for fileid in fileids:
            for w in self.tokenizer.pos_tag(self.raw(fileid)):
                yield w
        

    def tagged_sents(self, fileids):
        if type(fileids) == str:
            fileids = [fileids]
        for fileid in fileids:
            for s in self.tokenizer.pos_tag_sents(self.raw(fileids)):
                yield s

