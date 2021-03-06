#!/bin/bash

cp ../metadata/speakers_summary_1993.tsv ../psp1993_1996/speakers_summary.tsv
python generate_pandas.py -i ../psp1993_1996 -o ../data -f psp1993_1996

cp ../metadata/speakers_summary_1996.tsv ../psp1996_1998/speakers_summary.tsv
python generate_pandas.py -i ../psp1996_1998 -o ../data -f psp1996_1998

cp ../metadata/speakers_summary_1998.tsv ../psp1998_2002/speakers_summary.tsv
python generate_pandas.py -i ../psp1998_2002 -o ../data -f psp1998_2002

cp ../metadata/speakers_summary_2002.tsv ../psp2002_2006/speakers_summary.tsv
python generate_pandas.py -i ../psp2002_2006 -o ../data -f psp2002_2006

cp ../metadata/speakers_summary_2006.tsv ../psp2006_2010/speakers_summary.tsv
python generate_pandas.py -i ../psp2006_2010 -o ../data -f psp2006_2010

cp ../metadata/speakers_summary_2010.tsv ../psp2010_2013/speakers_summary.tsv
python generate_pandas.py -i ../psp2010_2013 -o ../data -f psp2010_2013

cp ../metadata/speakers_summary_2013.tsv ../psp2013_2017/speakers_summary.tsv
python generate_pandas.py -i ../psp2013_2017 -o ../data -f psp2013_2017

cp ../metadata/speakers_summary_2017.tsv ../psp2017_2021/speakers_summary.tsv
python generate_pandas.py -i ../psp2017_2021 -o ../data -f psp2017_2021

python generate_speakers_db.py -i ../data -o ../data -f psp_steno_speakers_db

python generate_corpus_input_files.py  -i ../data -o ../data/corpus_input -a
