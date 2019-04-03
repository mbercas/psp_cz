# psp.cz steno downloader
A Python web crawler to download the steno-types of the Czech parliament

## Download stenos
Currently requires manual configuration of the output directory and start web-page

   WARNING: I have tried to limit the number of access to the web page
            but nevertheless this project may be accessing the web
            page very often, please do not overuse.
            
Future improvements planned is to limit the access rate to the page.

### Requirements
 - python3        // tested with 3.6
 - python3-bs4    // beautiful-soup
 
### Output files

The output directory can be specified with thee *-o* or *--output-directory* switch, if not specified all ouput will be written to the current directory.

The oput file format are text files, with names as follow:
  s_[/d]\*3_b[/d]\*2_i[/d]\*3_<name_str>.txt
         
  s_[/d]\*2      theee digits indicating the session
  b[/d]+         order of the day point index
  i_[/d]\*3      intervention index
  <name_str>     name of the speaker

