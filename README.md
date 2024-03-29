# PSP-CZ parliament analysis tools

A bunch of tools to collect data from the Czech parlament and analize it.

## Collecting the data

The first step in every data analysis project is to get the data. For this project we will organize the data in data frames. Since doing it by hand is time consuming (and most important very boring) we have constructed a web crawler to get the data.

[psp_cz spyder](./doc/downloading_data.md)

The collected data is already stored in the `data` directory.

## Generate Pandas data frame

The generate_pandas script combines the text files and the medatata into a single Pandas data frame. The dataframe is stored as a compressed tsv (TAB sepparated values) that can be easily loaded with a single command.

GeneratePandas uses the metadata in the downloads directory, even though download_stenos.py tries to fill as much information as possible and correct errors in the downloaded data the metadata is far from perfect, corrected metadata files for each period can be found in the metadata directory.

Also the metadata files are not checked for correcteness, in principle only the fields, session it, session name, topic, order, speaker name, speaker function, function, tokens and text are meant to be used.

~~~~~~~~~~{.py}
    import pandas as pd

    df = pd.read_csv('tsv_file_name.tsv.xz', delimiter='\t', compression='xz')
~~~~~~~~~~

### Requirements

  - Pandas

### Usage

    usage: generate_pandas.py [-h] [-i INPUT_DIRECTORY] [-o OUTPUT_DIRECTORY]
                              [-f OUTPUT_FILE_NAME]

    Combine stenos and metadata into a Pandas data frame

    optional arguments:
      -h, --help             show this help message and exit
      -i INPUT_DIRECTORY,  --input-dir INPUT_DIRECTORY
                             output directory
      -o OUTPUT_DIRECTORY, --output-dir OUTPUT_DIRECTORY
                             output directory
      -f OUTPUT_FILE_NAME, --output-filename OUTPUT_FILE_NAME
                             output file name
