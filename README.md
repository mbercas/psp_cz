# PSP-CZ parliament analysis tools

A bunch of tools to collect data from the Czech parlament and analize it.

## Collecting the data

The first step in every data analysis project is to get the data. For this project we will organize the data in data frames. Since doing it by hand is time consuming (and most important very boring) we have constructed a web crawler to get the data.

[psp_cz spyder](./doc/downloading_data.md)

The collected data is already stored in the `data` directory.

## Generate Pandas data frame

The generate_pandas script combines the text files and the medatata into a single Pandas data frame. The dataframe is stored as a compressed tsv (TAB sepparated values) that can be easily loaded with a single command.

NOTE: The `download_stenos.py` program tries to collect as much information as possible from the speakers but the speakers table is not perfect and some fields have been completed manually.

  - not all the speakers have a birtday on their page (but most have a Wikipedia entry)
  - some speakers have several roles
  - some of the roles in the parliament [ministers](https://www.youtube.com/watch?v=w9XDUBDMNuk) have different spelling in their entries
  - some women changed their surnames after chanding marrital status.


~~~~~~~~~~{.py}
    import pandas as pd

    df = pd.read_pickle('pickle_file_name.tsv.xz', delimiter='\t', compression='xz')
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
