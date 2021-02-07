import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path

# Create a dataset in pandas with the following columns

columns = ["date", "title", "order", "speaker", "text"]

df = pd.DataFrame(columns=columns)


URL="https://www.vlada.cz/scripts/detail.php?pgid=218&conn=1339&pg=0"


soup = []

r = requests.get(URL)

if r.ok:
    soup.append(BeautifulSoup(r.text, 'html5lib'))
else:
    print(f"Failed URL: {page}")

base_addr = "https://www.vlada.cz"

# Clean text of funny symbols
def clean(text):
    subs = {u"\xa0": u" "}

    for err, sub in subs.items():
        text = text.replace(err, sub)

    return text

# Split the text into a list of pairs containing names
# of the speaker and what they say
def split_interventions(paragraphs):
    rgx = re.compile(u"^(.+?):\s+([A-ZČ].*)$", re.UNICODE) # force capital after : to reduce prob of bad
                                                           # match, still a problem since re does not do unicode
    interventions = []
    for p in paragraphs:
        name = p.find("strong")
        text = clean(p.text)


        if name != None:
            m = rgx.match(text)
            if m != None:
                interventions.append((m.groups()[0], m.groups()[1]))
                continue

        if len(interventions) > 0:
            interventions[-1] = (interventions[-1][0], interventions[-1][1] + " " + text)
    return interventions


cache = Path(".") / '.conferences_cache'

def get_request(link):

    if not cache.exists():
        cache.mkdir(parents=True)

    file_str = link.replace('https://www.vlada.cz/cz/media-centrum/tiskove-konference/', '')

    cached_file_name = cache / file_str
    text = ""


    if cached_file_name.exists():
        print(f"{cached_file_name} ...reusing")
        text = cached_file_name.read_text(encoding='utf-8')
    else:
        res = requests.get(link)

        if res.status_code != requests.codes.ok:
            print(f"Unable to download {link}")
            raise Exception()

        cached_file_name.parents[0].mkdir(parents=True, exist_ok=True)
        cached_file_name.write_text(res.text, encoding='utf-8')
        text = res.text
    return text


for s in soup[0:1]:
    dates = [p.text for p in s.find_all('p') if p.has_attr("class") and p["class"][0]=="info"]
    links = [base_addr + p.find('a')["href"] for p in s.find_all('p') if p.has_attr("class") and p["class"][0]=="more"]
    titles = [p.find('a').text for p in s.find_all('h2') if p.has_attr("class") and p["class"][0]=="nomargin"]

    # check that all links are consistent with the titles and the dates
    assert(len(dates)==len(links))
    assert(len(dates)==len(titles))

    for date, link, title in zip(dates, links, titles):

        if -1 == date.find("2020"):
            continue

        print(f" -> link: {link}")

        text = ""
        try:
            text = get_request(link)
        except:
            continue

        if text != "":
            soup_text = BeautifulSoup(text, 'html5lib')
            text = [d for d in soup_text.find_all("div") if d.has_attr("class") and d["class"][0]=="detail"][0]
            para = [p for p in text.find_all('p')]
            inter = split_interventions(para)
        else:
            print(f"URL: {link} is mepty or could not parse it")
            continue

        # check that everything went OK
        for idx, i in enumerate(inter):
            print(f"splitting interventions - {idx}")
            if len(i) != 2:
                print("There was a problem parsing the text")
                assert(False)
            else:
                d = {"date": date, "title": title, "order": idx, "speaker": i[0], "text": i[1]}
                df = df.append(d, ignore_index=True)

df.date = pd.to_datetime(df.date)
df.to_csv("conferences_2020.tsv.xz", encoding='utf-8', sep='\t', header=True, index=False, compression='xz')
