# psp.cz steno downloader
A Python web crawler to download the steno-types of the Czech parliament and some tools to organize the data

## Download stenos
A Python web crawler that gets all the steno protocols from a given parlamentary season and stores them as text files with the corresponding metadata.


### Requirements
 - python3        // tested with 3.6
 - python3-bs4    // beautiful-soup
 - request        // connect to web pages
 - html5lib       // html parser library
 
### Usage

    usage: download_stenos.py [-h] [--index] [-o OUTPUT_DIRECTORY] [-y YEAR]

    Download steno-protocols in psp.cz

    optional arguments:
        -h, --help            show this help message and exit
        --index               generate an index for the files
        -o OUTPUT_DIRECTORY, --output-dir OUTPUT_DIRECTORY output directory
        -y YEAR, --year YEAR  session year (2013 or 2017), default 2017
        -n, --new-report      creates a new report for data dowdloaded if already
                              exists, otherwise creates a new one

### Output files

The output directory can be specified with thee *-o* or *--output-directory* switch, if not specified all ouput will be written to the current directory.

#### Text files

The steno protocols get stored as utf-8 text files, the name convention for the files is as follows, each file represents an individual intervention:

    s_<ddd>_<yyyymmdd>_t_<ddd>_i_<ddd>_<name_str>.txt
         
    - s_<ddd>        theee digits indicating the session
    - <yyyymmdd>     date of the intervention
    - t_<ddd>        topic for order of the day point index
    - i_<ddd>        intervention index
    - <name_str>     name of the speaker

#### Metadata files

The metadata is stored in two files, the fields are separated by TABS, the first column enumerates the fields and each row contains the metadata for one of the generated text files.

`file_summary.tsv`

    session	date	topic_idx	topic_str	order	steno_name	file_name

`speakers_summary.tsv`

    name	titles	function	steno_name	sex   party   birthdate  web_page

## Generate Pandas data frame

The generate_pandas script combines the text files and the medatata into a single Pandas data frame. The dataframe is stored as a compressed pickle that can be easily loaded with a single command

~~~~~~~~~~{.py}
    import pandas as pd

    df = pd.read_pickle("pickle_file_name.pkl.xz", compression='xz')
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
