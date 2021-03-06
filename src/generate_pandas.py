#!/usr/bin/env python3

"""
.. module:: generate_pandas

   :synopsis: Classes and script to generate a Pandas data frame
              from the downloaded stenos

.. moduleauthor:: Manuel Berrocal <mbercas@gmail.com>

"""
"""
GNU General Public License v3.0
Permissions of this strong copyleft license are conditioned on making available complete source code of licensed works and modifications, which include larger works using a licensed work, under the same license. Copyright and license notices must be preserved. Contributors provide an express grant of patent rights.
"""

from pathlib import Path
import argparse

import pandas as pd
import numpy as np
import sys
import datetime

class GeneratePandasDataFrame:
    def __init__(self, input_path, output_path, pickle_name="pickled_df"):
        """Constructor
        :param input_path pathlib.Path: path ot input directory
        :param output_path pathlib.Path: path to output directory
        """
        self.df = None
        self.names = None
        self.input_path = input_path
        self.output_path = output_path
        self.pickle_name = pickle_name

    def read_summary(self):
        """Read the summary file in the input directory and create a data frame"""

        files_summary = self.input_path / "file_summary.tsv"
        names_summary = self.input_path / "speakers_summary.tsv"

        with files_summary.open() as fd:
            self.df = pd.read_csv(fd, sep='\t', header=0)

        with names_summary.open() as fd:
            self.names = pd.read_csv(fd, sep='\t', header=0)

    def read_file_contents(self):

        #files = {x for x in self.input_path.iterdir() if x.suffix == '.txt'}
        found_files = 0

        txt = []


        for file_name in self.df['file_name']:
            ifile = self.input_path.joinpath(file_name)

            if ifile.exists():
                found_files += 1

                #with self.input_path.joinpath(file_name).open() as fd:
                with ifile.open() as fd:
                    tmp_txt = ""
                    for line in fd.readlines():
                        if line[0] == ':':
                            line += line[1:].strip()
                        tmp_txt += line
                    txt.append(tmp_txt)
            else:
                print("Can not parse file: {}".format(file_name))
                txt.append("")

        self.df.loc[:,"text"] = pd.Series(txt, index=self.df.index)
        self.df.loc[:,"tokens"] = self.df["text"].apply(lambda x : len(x.split(sep=' ')))
        self.df.loc[:,"date"] = self.df["date"].apply(lambda x : pd.to_datetime(x, format="%Y%m%d"))
        self.df.steno_name = self.df.steno_name.apply(lambda x : x.replace('_', ' ').lower())
        self.df.steno_name = self.df.steno_name.apply(lambda x : x.replace('  ', ' '))

        if (not int == self.names.dtypes["birthdate"]) and (not float == self.names.dtypes["birthdate"]):
            self.names.birthdate = self.names.birthdate.apply(lambda x : x.replace('-', ''))
        self.names.birthdate = pd.to_datetime(self.names.birthdate, format="%Y%m%d")
        self.names["age"] =  (round((self.df.date.max() - self.names.birthdate)/datetime.timedelta(days=365)))
        self.names["name"] = self.names.name.apply(lambda x: x.strip())

        self.merge_names_information()


    def merge_names_information(self):
        """Create and populate new columns
           - age
           - sex
           - titles
           - function
           - replace name with filtered one
           -
        """
        self.df["function"] = ""
        self.df["birthyear"] = 0
        self.df["age"] = 0
        self.df["sex"] = ""
        self.df["titles"] = ""
        self.df["party"] = ""

        grp = self.df.groupby('steno_name')
        for nidx, steno_name in self.names.steno_name.iteritems():
            try:
                idx = grp.groups[steno_name.lower()]
                self.df.loc[idx, "function"] = self.names.loc[nidx, "function"]
                self.df.loc[idx,"birthyear"] = self.names.loc[nidx,"birthdate"].year
                self.df.loc[idx,"age"] = self.names.loc[nidx,"age"]
                self.df.loc[idx,"sex"] = self.names.loc[nidx,"sex"]
                self.df.loc[idx,"name"] = self.names.loc[nidx,"name"]
                self.df.loc[idx,"titles"] = self.names.loc[nidx,"titles"]
                self.df.loc[idx,"party"] = self.names.loc[nidx,"party"]
            except KeyError:
                print(f"KeyError: {nidx=} :: {steno_name=}")
                print(f"KeyError: {self.df.loc[nidx]=}")

        # Move the text column to the last column of the data frame
        column_names = ['session', 'date', 'topic_idx', 'topic_str', 'order', 'name',
                        'steno_name', 'function', 'file_name', 'tokens', 'birthyear', 'age', 'sex',
                        'titles', 'party', 'text']
        self.df = self.df[column_names]

    def transform_function(self, f):
        """Transform female function titles into male for easy searching"""
        if f[:6] == 'Poslan':
            return 'Poslanec'
        if f[:7] == 'Senátor':
            return 'Senátor'
        else:
            return f

    def remove_duplicates(self):
        self.df = self.df.drop_duplicates(['session', 'topic_idx', 'name', 'text'], keep='first')


    def save_tsv(self):

        if not self.output_path.exists():
            self.output_path.mkdir(parents = True)


        self.df.to_csv(str(self.output_path.joinpath(self.pickle_name + '.tsv.xz')),
                       encoding='utf-8',
                       sep='\t',
                       header=True,
                       compression='xz',
                       index=False)


    def report_problems(self):
        if not (self.df.sex.isnull() == False).all():
            print("WARNING: Rows with NULL is sex field\n\n")
            print(self.df[self.df.sex.isnull() == False])

        if not (self.df.text.isnull() == False).all():
            print("WARNING: Rows with NULL is text field\n\n")
            print(self.df[self.df.text.isnull() == False])

        if not ((self.df.birthyear == 0) == False).all():
            print("WARNING: Missing birthyears\n\n")
            print(set(self.df[self.df.birthyear == 0].steno_name))


        if not (self.df.name.isnull() == False).all():
            print("WARNING: names with NULL is text field\n\n")
            print(self.df[self.df.name.isnull() == False])
            


def parse_args():
    parser = argparse.ArgumentParser(description='Combine stenos and metadata into a Pandas data frame')
    parser.add_argument('-i', '--input-dir',action='store', default='.',
                        dest='input_directory',
                        help='input directory')
    parser.add_argument('-o', '--output-dir',action='store', default='.',
                        dest='output_directory',
                        help='output directory')
    parser.add_argument('-f', '--output-filename',action='store', default='pickled_df',
                        dest='output_file_name',
                        help='output file name')

    args = parser.parse_args()

    ipath = Path(args.input_directory)
    if not ipath.exists() or not ipath.joinpath("file_summary.tsv").exists():
        print("Error: no tsv file in path: {}".format(str(args.input_directory)))
        sys.exit(-1)

    return args


if __name__ == "__main__":

    args = parse_args()

    gen = GeneratePandasDataFrame(Path(args.input_directory),
                                  Path(args.output_directory),
                                  args.output_file_name)

    gen.read_summary()
    gen.read_file_contents()
    gen.remove_duplicates()
    gen.save_tsv()
    gen.report_problems()
