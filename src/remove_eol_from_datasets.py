#!/usr/bin/env python

"""A simple script to parse the text field of the data sets and replace the \n for space"""

import pandas as pd

periods = [("1993-1996", "../data/psp1993_1996.tsv.xz") ,
           ("1996-1998", "../data/psp1996_1998.tsv.xz"),
           ("1998-2002", "../data/psp1998_2002.tsv.xz"),
           ("2002-2006", "../data/psp2002_2006.tsv.xz"),
           ("2006-2010", "../data/psp2006_2010.tsv.xz"),
           ("2010-2013", "../data/psp2010_2013.tsv.xz"),
           ("2013-2017", "../data/psp2013_2017.tsv.xz"),
           ("2017-2021", "../data/psp2017_2021.tsv.xz")]


if __name__ == "__main__":

    for period, fn in periods[1:]:
      
        new_fn = fn.replace(".tsv.xz", "")
        new_fn = new_fn + "_no_eol.tar.xz"

        print(f"Removing EOL from {fn} creating new file: {new_fn}")
        
        data = pd.read_csv(fn, compression='xz', sep='\t', encoding='utf-8')
        data.text = data["text"].apply(lambda x : x.replace('\n', ' ').strip())
       

        data.to_csv(str(new_fn),
                    encoding='utf-8',
                    sep='\t',
                    header=True,
                    compression='xz',
                    index=False)
