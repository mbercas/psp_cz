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
import sys

class GeneratePandasDataFrame:
    def __init__(self, input_path, output_path, pickle_name="pickled_df"):
        """Constructor
        :param input_path pathlib.Path: path ot input directory
        :param output_path pathlib.Path: path to output directory
        """
        self.df = None
        self.input_path = input_path
        self.output_path = output_path
        self.pickle_name = pickle_name

    def read_summary(self):
        """Read the summary file in the input directory and create a data frame"""

        summary_file = self.input_path / "file_summary.tsv"

        with summary_file.open() as fd:
            self.df = pd.read_csv(fd, sep='\t', header=0)

    def read_file_contents(self):

        files = {x for x in self.input_path.iterdir() if x.suffix == '.txt'}
        found_files = 0

        txt = []


        for file_name in self.df['file_name']:
            ifile = self.input_path.joinpath(file_name)

            if ifile.exists():
                found_files += 1
                      
                with self.input_path.joinpath(file_name).open() as fd:
                    txt.append( fd.readline() )
            else:
                print("Can not parse file: {}".format(file_name))
                txt.append("")


        self.df.loc[:,"text"] = pd.Series(txt, index=self.df.index)
        self.df.loc[:,"tokens"] = self.df["text"].apply(lambda x : len(x.split(sep=' ')))

    def save_pickle(self):

        if not self.output_path.exists():
            self.output_path.mkdir(parents = True)


        self.df.to_pickle(
            str(self.output_path.joinpath(self.pickle_name + '.pkl.xz')),
            compression='xz')

        


def parse_args():
    parser = argparse.ArgumentParser(description='Download steno-protocols in psp.cz')
    parser.add_argument('-i', '--input-dir',action='store', default='.',
                        dest='input_directory',
                        help='output directory')
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
    
    generator = GeneratePandasDataFrame( Path(args.input_directory),
                                         Path(args.output_directory),
                                         args.output_file_name)

    generator.read_summary()
    generator.read_file_contents()
    generator.save_pickle()
        
