#!/usr/bin/env python3

"""parses all the steneoprotocols of the parlament and creates
text files tagged the following way

s_[/d]*2_b[/d]*2_i[/d]*3_<str>.txt
         
s_[/d]*2    two digits indicating the session
b[/d]+      order of the day point index
i_[/d]*3    intervention index
<str>       name of the speaker
"""


import os
import re
import logging
from bs4 import BeautifulSoup
import requests
import argparse
from pathlib import Path

class SessionManager:
    __slots__ = ['valid', 'title', 'index', 'date', 'base_session_url']
    def __init__(self):
        valid = False
        index = ""
        date  = ""
        title = ""
        base_session_url = ""

    def __str__(self):
        str_ = "Title: {}".format(self.title)
        str_ += "Index: {}".format(self.index)
        str_ += "Date string: {}".format(self.date)
        str_ += "URL: {}".format(self.base_session_url)
        return str_
        
              



CzechMonths = {'ledna':1, 'února':2, 'března':3,'dubna':4,'května':5,
               'června':6,'července':7,'srpna':8, 'září':9,
               'října':10, 'listopadu':11, 'prosince':12 }

    
    

def get_all_stenos(res):
    """Gets the content page of PSP and returns all the links to the prococols"""
    soup_main = BeautifulSoup(res, 'html5lib')
    reg_ex_steno_main = re.compile(r'^.*schuz.*htm$')
    return [l.get('href') for l in soup_main.find_all('a') if None != reg_ex_steno_main.search(l.get('href'))]


class SessionParser:

    class Page:
        def __init__(self):
            self.link = ""
            self.date_string = ""
            self.content = ""
            self.soup = None
    
    def __init__(self, base_url, session_number, session_link):
        self.base_url = base_url
        self.sublinks = base_url + session_number + "schuz/"
        self.session_link = base_url + session_link
        self.session_number = session_number
        self.pages = {}    # pages link stenos and order them by topic
        self.stenos = {}
        self.topics = {}
        self.interventions = {}
        
    def parse_session(self):
        """
        The main page of the session contains all the links to all the subsessions,
        they are ordered by topic (topics can be split in different days (i.e. so
        they are stored in different pages), we will transverse the session following
        the links in the session record (Schuz)

        Returns False if ti fails processing the Schuz

        session -> topic -> intervention

        """

        logging.info("Parsing session %s", self.session_link)
        
        res = requests.get(self.session_link)
        if False == check_request(res):
            return False
        main_soup =  BeautifulSoup(res.text, 'html5lib')

        # All topics are between <p>...</p>
        for topic in main_soup.find_all('p'):
            # topics have <a> id="<identifier>" name="<identifier>"</a>
            # and a set of links
            links = topic.find_all('a')
            if len(links) == 0:
                continue

            try:
                topic_id = links[0]['id']
            except KeyError:
                logging.info("Ignoring: %s", links[0])
                continue
            
            if topic_id not in self.topics:
                self.topics[topic_id] = []

            
            for link in links[1:]:
                try:
                    sublink = link['href']
                        
                    q_id = self.get_qid_for_topic(sublink)
                    if None == q_id:
                        logging.warning("Can not find q_id in %s", sublink)
                        continue

                    if self.parse_sublink_order(q_id, sublink):
                        self.topics[topic_id].extend(self.interventions[q_id])
                except KeyError:
                    continue
                
        # All links to interventions are not in self.interventions
        # first download all individual pages into stenos dictionary
        #
        self.get_all_stenos()
        
    def get_all_stenos(self):
        """Iterate the interventions dictionary to download all the pages of
        the stenos, parse them and strore them in the stenos dictionary"""
        for topic in self.topics.values():
            if len(topic) == 0:
                continue

            for intervention in topic:
                if intervention[1] not in self.stenos:
                    link = self.sublinks + intervention[1] 
                    res = requests.get(link)

                    if False == check_request(res):
                        logging.error("Can not open steno page %s", link)
                        continue
                    soup =  BeautifulSoup(res.text, 'html5lib')
                    self.stenos[intervention[1]] = self.parse_steno(soup)
                    
    def parse_steno(self, steno):
        """All paragraphs with text are justified"""
        text_paragraphs = steno.find_all('p', attrs={'align':'justify'})
        r_id = ""
        text = ""
        speaker = ""
        interventions = {}
        for p in text_paragraphs:
            # ignore empty
            if p.text == '\xa0':
                continue
            speaker_link = p.find('a')
            if speaker_link:
                if r_id != "":
                    interventions[r_id] = (speaker, text)
                text = ""
                if speaker_link.has_attr('id'):
                    r_id = speaker_link['id']
                    speaker = speaker_link.text.replace(' ', '_')
                    speaker_link.extract()
                else:
                    speaker_link.extract()
                    
            text += self.filter_text(p.text)
        interventions[r_id] = (speaker, text)
        return interventions
    
    def filter_text(self, text):
        # remove : at beginning of paragraph
        if text[0] == ':':
            text = text[1:]
        # remove white spaces from beginning and end
        text = text.strip().rstrip()
        
        # replace '\xa0' with space
        text = text.replace('\xa0', ' ')
        return text
    
    def generate_files(self, output_directory=Path('.')):
        """Iterate the topics dictionary to get all the intrventions per
        topic, then go to the stenos dictionary to print get intervention"""
        if not output_directory.exists():
            output_directory.mkdir(parents=True)
        
        
        for topic_id, topic in self.topics.items():
            for idx, intervention in enumerate(topic):
                try:
                    steno = self.stenos[intervention[1]][intervention[2]]
                    file_name = output_directory.joinpath(
                        's_{0}_{1:0>2}_i_{2:0>2}_{3}.txt'.format(self.session_number,
                                                                 topic_id,
                                                                 idx+1, steno[0]))    
                    with file_name.open('w', encoding = 'utf-8') as fd:
                        fd.write(steno[1])
                except KeyError:
                    logging.error("Can not find key %s in steno %s",intervention[2],intervention[1])
 


    def parse_sublink_order(self, order_id, sublink):

        reg_ex_page = re.compile('^(.*.html).*')
        page_name = reg_ex_page.match(sublink)

        if None == page_name:
            logging.error("Can not find page name in sublink %s", sublink)
            return False

        page_idx = page_name.group(1)

        if page_idx not in self.pages:
            link = self.sublinks + sublink
            res = requests.get(link)
            if False == check_request(res):
                return False
            page = self.Page()
            page.link = link
            page.content = res.text
            page.soup = BeautifulSoup(res.text, 'html5lib')
            (rc, date) = self.get_steno_date(page.soup)
            if False == rc:
                logging.error("Can not find date in steno %s", link)
                return False
            page.date_string = date
            self.parse_interventions_page(page.soup)
            self.pages[page_idx] = page

        return True

    def parse_interventions_page(self, page_soup):
        """Get a list of all the q tags and all the a links below"""
        a_links = page_soup.find_all('a')
        
        intervention_link = re.compile('^(s[\d]*.htm)#(r[\d]*)$')
        
        
        q_id = ""
        for link in a_links:
            if link.has_attr('id'):
                q_id = link['id']
                if q_id not in self.interventions:
                    self.interventions[q_id] = []
            elif link.has_attr('href') and q_id != "":
                info = intervention_link.search(link['href'])
                if None != info:
                    self.interventions[q_id].append([info.group(0), info.group(1), info.group(2)])
                
                
                

    def get_qid_for_topic(self, link):

        # Find q# boundary <a id="q\d>, then find all the
        # <a href="s[\d]6.html#r[\d]+ until the next q\d
        # for all the links get the page if not allready in
        # stenos and extract the text for a given person

        reg_ex_topic = re.compile('^.*html#(q[\d]+)$')
        topic  = reg_ex_topic.match(link)
        if None == topic:
            logging.warning("Could not find 'q' topic separator in %s", link)
            return None
        
        return topic.group(1)
        
            
            
            
    
    def get_steno_date(self, soup):
        """Find metadata of the stenotype on the title.
        Returns a set containin valid if the title is valid,
        index of the session, and date in yyyymmdd format"""

        
        title = soup.find('title').string

        if len(title) == 0:
            return (False, "")

        title = title.replace('\xa0', ' ')

        reg_ex_title_date = re.compile(r'Stenografický zápis [\d]+. schůze, ([\d]+).\s(.*)\s(\d{4})')
        d = reg_ex_title_date.search(title)
        if d == None:
            logging.error("Can not find date in title: %s", title)
            return (False, "")

        date = "{0}{1:0>2}{2:0>2}".format(d.group(3), CzechMonths[d.group(2)], int(d.group(1)))
        return (True, date)


    
def check_request(res):
    """Returns False if the request failed"""
    rc = True
    if res.status_code == requests.codes.ok:
        logging.info("Connected to page %s", steno_page_url)
    else:
        logging.error("Unable to open page: %s", steno_page_url)
        rc = False
    return rc

if __name__ == "__main__":

    #logging.basicConfig(filename='download_steno.log', level=logging.DEBUG)
    
    base_page_url = 'http://public.psp.cz/eknih/2013ps/stenprot/'
    steno_page_url = base_page_url + 'index.htm'


    parser = argparse.ArgumentParser(description='Download steno-protocols in psp.cz')
    parser.add_argument('--index', action='store_true', default=False,
                        dest='generate_index',
                        help='generate an index for the files')
    parser.add_argument('-o', '--output-dir',action='store', default='.',
                        dest='output_directory',
                        help='output directory')
                        
    args = parser.parse_args()
    
    res = requests.get(steno_page_url)
    if check_request(res) == False:
        exit(-1)

    # get the links for all session pages
    #
    schuz_links = get_all_stenos(res.text)


    m = re.compile('^([\d]+)schuz/index.htm$')
    
    for link  in schuz_links:
        
        schuz_id = m.match(link)
        if schuz_id == None:
            logging.error("Can not get session number from link %s", link)
            continue
        
        session = SessionParser(base_page_url, schuz_id.group(1), link)
        session.parse_session()
        session.generate_files(Path(args.output_directory))
        break 
