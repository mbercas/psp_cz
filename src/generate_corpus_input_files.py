#!/usr/bin/env python 

from ufal.morphodita import *
from pathlib import Path

import argparse
import logging
import pandas as pd
import sys

from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom



dict_path = '../czech-morfflex-pdt-161115/czech-morfflex-161115.dict'
tagger_path = '../czech-morfflex-pdt-161115/czech-morfflex-pdt-161115.tagger'

output_dir = 'xml_output'

years = ["2017_2021", "2013_2017", "2010_2013", "2006_2010",
         "2002_2006", "1998_2002", "1996_1998", "1993_1996"]
year = "2017"

periods = {"1993-1996": "../../data/psp1993_1996.tsv.xz",
           "1996-1998": "../../data/psp1996_1998.tsv.xz",
           "1998-2002": "../../data/psp1998_2002.tsv.xz",
           "2002-2006": "../../data/psp2002_2006.tsv.xz",
           "2006-2010": "../../data/psp2006_2010.tsv.xz",
           "2010-2013": "../../data/psp2010_2013.tsv.xz",
           "2013-2017": "../../data/psp2013_2017.tsv.xz",
           "2017-2021": "../../data/psp2017_2021.tsv.xz"}


def process(period_list: list, output_directory: Path):
    """Process the data sets passed as arguments

    :param period_list: `list` of the periods to process
    :param output_directory: `Path` path to the output directory
    """
    morpho = Morpho.load(dict_path)
    if None == morpho:
        print("ERROR: Did not load the dictiorary")


    # TODO: load dataset
    # TODO: iterate dataset - for each line generate tagged file
    #    - use name of the original file with xml
    #    - text file or create XML structucture?
    #    - create header file; define fields
    # TODO: create metadatafile

    tagger = Tagger.load(tagger_path)

    # Load the forms, tokens and lemmas objects, they will be used to return
    # the values from the tagger


    for period in period_list:

        logging.info(f"Processing period {period}")
        
        forms = Forms()
        tokens = TokenRanges()
        lemmas = TaggedLemmas()


        tokenizer = tagger.newTokenizer()
        if tokenizer == None:
            logging.error("Could not open the tokenizer")
            sys.exit(-1)

        df_file = periods[period]

        df = pd.read_csv(df_file, sep='\t', header=0, encoding='utf-8', compression='xz')

        # Create one file for every session of the dataframe
        #
        output_path = output_directory / period
        output_path.mkdir(parents=True, exist_ok=True)

        # create a new field for the doc_id - use the file name with no extension
        # save the file as <doc_id>.xml
        #
        df["doc_id"] = df["file_name"].str.replace(".txt", "", regex=False)

        # open a metadata file in the output directory and copy the metadata
        #
        metadata_fields = ["doc_id", "session", "date", "topic_str", "topic_idx",
                           "order", "name", "birthyear","sex", "party"]


        df.to_csv( output_path / "metadata.csv", sep=',',
                   columns=metadata_fields, header=True, index=False, encoding='utf-8')

        morpho = tagger.getMorpho()
        converter = TagsetConverter_newStripLemmaIdConverter(morpho)

        for index, row in df.iterrows():

            text = row['text']
            tokenizer.setText(text)

            # TODO: add id to opus i.e. <period_<0000001>
            opus = Element('opus', {'period':period,
                                    'session':str(row['session']),
                                    'date':str(row['date']),
                                    'topic':row['topic_str'],
                                    'intervention_order':str(row['topic_idx']) + "." + str(row['order']),
                                    'speaker':row['name'],
                                    'party':row['party'],
                                    'srclang':"CZ"})


            output_file_name = Path(row['doc_id']).with_suffix(".xml")

            doc = SubElement(opus, 'doc', {'id':row['doc_id']})
            # for every sentence in file
            t = 0
            s_id = 0
            while tokenizer.nextSentence(forms, tokens):
                s_id += 1
                s = SubElement(doc, 's', {'id':str(s_id)})
                str_ = "\n"
                tagger.tag(forms, lemmas)
                for i, (lemma, token) in enumerate(zip(lemmas, tokens)):
                    converter.convert(lemma)
                    str_ += f"{text[token.start : token.start + token.length]}\t{lemma.lemma}\t{lemma.tag}\n"
                    t = token.start + token.length
                s.text = str_


            xmlstr = minidom.parseString(tostring(opus)).toprettyxml(indent="   ")
        #    print(xmlstr)

            # get filename from row, replace extension and save as xml
            with open( output_path / output_file_name,  "w") as f:
                f.write(xmlstr)


def check_period(period: str) -> bool:
    """Verifies that the period is in the period list
    :param preriod: `str` 
    :return" True is if the period is in the period list
    """
    return period in periods.keys()
    
            
def parse_args() -> set:
    """Parses the command line arguments"""
    
    parser = argparse.ArgumentParser(description="""Tags the steno datasets and creates files with Corpus structure""")

    parser.add_argument('-o', '--output-dir',action='store', default='./tmp',
                        dest='output_directory',
                        help='output directory')
    parser.add_argument('-y', '--year', action='store', default='2017-2021',
                        dest='year',
                        help=f'periods {periods.keys()}')
    parser.add_argument('-a', '--all', action='store_true', default=False,
                        dest='all_periods',
                        help=f'Create a corpus for all periods')


    args = parser.parse_args()

    

    if not check_period(args.year):
        print(f"Invalid preiod selected, valid years are {periods.keys()}")
        logging.error("(): Invalid period year".format(args.year))
        sys.exit(-1)


    process_periods = []
    if args.all_periods:
        process_periods = list(periods.keys())
    else:
        process_periods = [args.year]
        
    return (process_periods, Path(args.output_directory))
        

if __name__ == "__main__":

    FORMAT = "[%(lineno)s - %(funcName)20s() ] %(message)s"
    logging.basicConfig(format=FORMAT, filename='corpus_tagger.log', level=logging.INFO)

    process(*parse_args())

