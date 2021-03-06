#!/usr/bin/env python

""" Collect information from all speakers in all sessions and put it into a table 

    <speaker id="" name="" birthyear="">
        <legislature>
            <party> <\party>
            <role>  <\role>
        <\legislature>
    <\speaker_name>
"""

from pathlib import Path
import argparse
import sys
import re

import pandas as pd
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom




periods = [("1993-1996", "../data/psp1993_1996.tsv.xz") ,
           ("1996-1998", "../data/psp1996_1998.tsv.xz"),
           ("1998-2002", "../data/psp1998_2002.tsv.xz"),
           ("2002-2006", "../data/psp2002_2006.tsv.xz"),
           ("2006-2010", "../data/psp2006_2010.tsv.xz"),
           ("2010-2013", "../data/psp2010_2013.tsv.xz"),
           ("2013-2017", "../data/psp2013_2017.tsv.xz"),
           ("2017-2021", "../data/psp2017_2021.tsv.xz")]



def get_input_datasets(input_directory: str) -> 'list[str]':
    """Creates a list of input datasets of the form psp<period>.tsv.xz

    :params input_directory: `str` path to input directory
    :return: a list of valid input files - including full path
    """
    regex = re.compile(r'.*psp\d{4}_\d{4}.tsv.xz')
    ipath = Path(input_directory)
    ifiles = [str(f) for f in ipath.iterdir() if regex.match(str(f))]
    return ifiles
    

def get_role_from_steno_name(steno_name, name):
    """Removes the name from the steno name and normalizes the role"""
    role = steno_name
    for word in name.lower().split():
        role = role.replace(word, "").strip()
    return role

def get_periods(input_dataset_file_names:"list[str]") -> "list[str]":
    """Extracts the period from the dataset file name
       
       Input parameters
       :param input_datase_file_names: `list[str]` a list of string with the names of 
                                       the datasets
       :return" `list[str]` a list of strings with the period start-end years
    """
    regex = re.compile(r'.*psp(\d{4}_\d{4}).tsv.xz')
    return [regex.match(f).groups()[0].replace("_", "-") for f in input_dataset_file_names]

def get_speakers_dictionary(period_file_names: list) -> dict:
    """Parses the datasets passed in periords to extract the speakers field,
       adds the speaker, and attributes to a dictionary, the key to the dictionary
       is a tupple of the name and brith year.

       :param period_file_names: `list[str]1 is a list of the input files containing the datasets
                                  to process
       :return: a dictionary with the speakers and the attributes

    """
    speakers = {}
    user_id = 1
    periods = get_periods(period_file_names)
    for period_file, period_year in zip(period_file_names, periods):
        
        psp = pd.read_csv(period_file, compression="xz", sep="\t", header=0)
        groups = psp.groupby(["name", "birthyear"])

        # index is a tupple, [name, birthyear]
        for index, group in groups:
            steno_names = set(group.steno_name)
            roles = [get_role_from_steno_name(role, index[0]) for role in steno_names]

            if index not in speakers:
                speakers[index] = {"id": user_id,
                                   "sex": group.iloc[0].sex}
                user_id += 1
            speakers[index][period_year] = {"party": group.iloc[0].party,
                                            "role": roles}
    return speakers


def get_xml_element(speaker_dict: dict, periods: list) -> Element:
    """Convert the speaker dictionary into a DOM Element
       :param speaker_dict: `dict` a dictionary containing the speaker parsed info.
       :param periods" `list[str]` a list of strings contining the years

       :return: `Element`
       """
    doc = Element('parlament_speakers')
    
    for index in sorted(speaker_dict.keys()):
        info = speaker_dict[index]
        sk = SubElement(doc, 'speaker', {'id': str(info["id"]),
                                         'birth_year': str(index[1])})
        sk.text = index[0]

        for period in periods:
            if period in info.keys():
                p = SubElement(sk, 'period', {'years': period,
                                              'party': info[period]['party']})
                for role_id, role in enumerate(sorted(info[period]['role'])):
                    r = SubElement(p, 'role', {'id': str(role_id+1)})
                    r.text = role
    return doc

def parse_args():
    """Parse arguments in command line and clean up"""
    parser = argparse.ArgumentParser(description='Create XML database with information from speakers in steno DataFrames')
    parser.add_argument('-i', '--input-dir',action='store', default='.',
                        dest='input_directory',
                        help='input directory')
    parser.add_argument('-o', '--output-dir',action='store', default='.',
                        dest='output_directory',
                        help='output directory')
    parser.add_argument('-f', '--output-filename',action='store', default='psp_steno_speaker_db',
                        dest='output_file_name',
                        help='output file name')

    args = parser.parse_args()

    ipath = Path(args.input_directory)
    if not ipath.exists():
        print("Error: no input directory: {}".format(str(args.input_directory)))
        sys.exit(-1)

    return args

def write_output_file( output_directory: str, output_file_name: str, xmlstr: str):
    """Writes the output file in the specified path"""

    path = Path(output_directory)
    if not path.exists():
        path.mkdir(parents=True)
    
    with open( path / (output_file_name + ".xml"),  "w") as f:
        f.write(xmlstr)

    
if __name__ == "__main__":


    args = parse_args()

    input_datasets = get_input_datasets(args.input_directory)
    periods = get_periods(input_datasets)
    speakers = get_speakers_dictionary(input_datasets)

    doc =get_xml_element(speakers, periods)

    xmlstr = minidom.parseString(tostring(doc)).toprettyxml(indent="  ")

    write_output_file(args.output_directory, args.output_file_name, xmlstr)
    
    

