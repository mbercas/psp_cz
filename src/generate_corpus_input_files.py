#!/usr/bin/env python 

from ufal.morphodita import *
from pathlib import Path

import argparse
import logging
import pandas as pd
import sys
import xmltodict
import re

from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom



dict_path = '../nltk_morphodita/czech-morfflex-161115.dict'
tagger_path = '../nltk_morphodita/czech-morfflex-pdt-161115.tagger'

output_dir = 'xml_output'

years = ["2017_2021", "2013_2017", "2010_2013", "2006_2010",
         "2002_2006", "1998_2002", "1996_1998", "1993_1996"]
year = "2017"

periods = {"1993-1996": "../data/psp1993_1996.tsv.xz",
           "1996-1998": "../data/psp1996_1998.tsv.xz",
           "1998-2002": "../data/psp1998_2002.tsv.xz",
           "2002-2006": "../data/psp2002_2006.tsv.xz",
           "2006-2010": "../data/psp2006_2010.tsv.xz",
           "2010-2013": "../data/psp2010_2013.tsv.xz",
           "2013-2017": "../data/psp2013_2017.tsv.xz",
           "2017-2021": "../data/psp2017_2021.tsv.xz"}


def get_input_datasets(input_directory: Path) -> 'list[str]':
    """Creates a list of input datasets of the form psp<period>.tsv.xz

    :params input_directory: `str` path to input directory
    :return: a list of valid input files - including full path
    """
    regex = re.compile(r'.*psp\d{4}_\d{4}.tsv.xz')
    ipath = input_directory
    ifiles = [str(f) for f in ipath.iterdir() if regex.match(str(f))]
    return ifiles

def get_periods(input_dataset_file_names:"list[str]") -> "list[str]":
    """Extracts the period from the dataset file name
       
       Input parameters
       :param input_datase_file_names: `list[str]` a list of string with the names of 
                                       the datasets
       :return" `list[str]` a list of strings with the period start-end years
    """
    regex = re.compile(r'.*psp(\d{4}_\d{4}).tsv.xz')
    return [regex.match(f).groups()[0].replace("_", "-") for f in input_dataset_file_names]



def get_speakers(input_path: Path) -> dict:
    """Creates a dictionary with the speakers and their speaker IDs

       :param: `str` containing the path to the input files
       :return: dict, index is a tuple of speaker name aand brith_date
    """
    speakers_file = input_path / "psp_steno_speakers_db.xml"
    speakers_dict = {}
    with open(str(speakers_file), 'r') as fd:
        xml_dict = xmltodict.parse(fd.read())

        for speaker in xml_dict['parlament_speakers']['speaker']:
            speakers_dict[(speaker['#text'], speaker['@birth_year'])] = speaker["@id"]
            
    return speakers_dict

def process(period_list: list, input_directory: Path, output_directory: Path):
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
    morpho = tagger.getMorpho()
    converter = TagsetConverter_newStripLemmaIdConverter(morpho)

    # Load the forms, tokens and lemmas objects, they will be used to return
    # the values from the tagger


    speaker_ids = get_speakers(input_directory)
    period_files = get_input_datasets(input_directory)
    periods = get_periods(period_files)
    
    
    for period, period_file in zip(periods, period_files):

        # Process only for the periods in the period list
        if period not in period_list:
            continue
        
        logging.info(f"Processing period {period}")
        
        forms = Forms()
        tokens = TokenRanges()
        lemmas = TaggedLemmas()


        tokenizer = tagger.newTokenizer()
        if tokenizer == None:
            logging.error("Could not open the tokenizer")
            sys.exit(-1)

        df = pd.read_csv(period_file, sep='\t', header=0, encoding='utf-8', compression='xz')

        # Create one file for every session of the dataframe
        #
        output_path = output_directory / period
        output_path.mkdir(parents=True, exist_ok=True)


        # open a metadata file in the output directory and copy the metadata
        #
        #metadata_fields = ["doc_id", "session", "date", "topic_str", "topic_idx",
        #                   "order", "name", "function", "birthyear","sex", "party"]
        #df.to_csv( output_path / "metadata.csv", sep=',',
        #           columns=metadata_fields, header=True, index=False, encoding='utf-8')

        morpho = tagger.getMorpho()
        converter = TagsetConverter_newStripLemmaIdConverter(morpho)

        # group by seesion & topic,
        # create ID period_session_topic <- top level ; use this ID as file name
        #    store all the interventions from same session-topic group in one file
        #    for each intervention create speaker
        #        for each sentence create vertical

        groups = df.groupby(["session", "topic_idx"])

        for (session, topic_idx), group in groups:

            file_id = f"{period}_{session:03d}_{topic_idx:03d}"
            output_file_name = Path(file_id).with_suffix(".xml")

            doc = None
            for index, row in group.iterrows():

                # only do for the first row
                if doc == None:
                    doc = Element('doc', {'id':file_id,
                                          'period':period,
                                          'session':str(row['session']),
                                          'start_date':str(row['date']),
                                          'topic':row['topic_str']
                                          }
                                  )

                speaker_id = speaker_ids[(row['name'], str(row['birthyear']))]
                sp = SubElement(doc, 'sp', {'id': str(speaker_id),
                                            'speaker': row['name'],
                                            'role': row['function'],
                                            'date': str(row['date']),
                                            'intervention_order': str(row['order']),
                                            'party': row['party']
                                            }
                                )

                text = row['text']
                tokenizer.setText(text)
                
                # for every sentence in intervention
                t = 0
                s_id = 0
                while tokenizer.nextSentence(forms, tokens):
                    s_id += 1
                    s = SubElement(sp, 's', {'id':f"{s_id:05d}"})
                    str_ = "\n"
                    tagger.tag(forms, lemmas)
                    for i, (lemma, token) in enumerate(zip(lemmas, tokens)):
                        converter.convert(lemma)
                        str_ += f"{text[token.start : token.start + token.length]}\t{lemma.lemma}\t{lemma.tag}\n"
                        t = token.start + token.length
                    s.text = str_


            xmlstr = minidom.parseString(tostring(doc)).toprettyxml(indent="   ")
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

    parser.add_argument('-i', '--input-dir',action='store', default='./tmp',
                        dest='input_directory',
                        help='input directory')
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


    if not Path(args.input_directory).exists():
        print("Error: can not find input directory")
        logging.error(f"Invalid input directory: {args.input_directory}")
        sys.exit(-1)
    

    if not check_period(args.year):
        print(f"Invalid preiod selected, valid years are {periods.keys()}")
        logging.error("(): Invalid period year".format(args.year))
        sys.exit(-1)


    process_periods = []
    if args.all_periods:
        process_periods = list(periods.keys())
    else:
        process_periods = [args.year]
        
    return (process_periods, Path(args.input_directory), Path(args.output_directory))
        

if __name__ == "__main__":

    FORMAT = "[%(lineno)s - %(funcName)20s() ] %(message)s"
    logging.basicConfig(format=FORMAT, filename='corpus_tagger.log', level=logging.INFO)

    process(*parse_args())

