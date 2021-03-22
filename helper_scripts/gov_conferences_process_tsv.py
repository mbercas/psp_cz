#!/usr/bin/env python


import pandas as pd
import re
import datetime as dt

""" Open the TSV file,
 - clean up the fields
 - add column ROLE : moderation, question, answer
"""



role_tag = ["mderator", "question", "answer"]

moderator = ["Jana Adamcová", "tisková mluvčí", "Vladimír Vořechovský",
             "Tomáš Medek", 'Michaela Minářová', 'Veronika Beníšková'] 

answer = ["ministr", "místopředseda", "předseda", "kancléř", "premiér",
          "Ministr", "Ministryně", "předsedkyně"
          "Richard Brabec", "Jan Blatný", "Karel Havlíček", "Andrej Babiš",
          "Adam Kulhánek",
          'Barbora Spáčilová,',
          'Denisa Hejlová',
          'Eva Gottvaldová',
          'Evžen Bouřa',
          'Helena Válková',
          'Jan Wiesner',
          'Jarmila Rážová',
          'Jarmila Vedralová',
          'Jaroslav Hanák',
          'Jaroslav Míl',
          'Klára Šimáčková Laurenčíková',
          'Marie Nejedlá',
          'Marián Hajdúch',
          'Michal Žurovec',
          'Pavel Březovský',
          'Petr Procházka',
          'Petr Valdman',
          'Petr Šnajdárek',
          'Radek Mátl',
          'Radka Hrdinová',
          'Rastislav Maďar',
          'Roman Prymula',
          'Stanislav Křeček',
          'Vendula Kodetová',
          'Veronika Beníšková',
          'Vladimír Dzurilla',
          'Vladimír Valenta',
          'Vladimír Vořechovoský',
          'Vít Dočkal',
          'Wolfgang Wittl',
          'Zdeňka Jágrová',
          'Ángel Gurría']

# 'Videomedailonek, Prof. RNDr. Václav Hořejší, CSc.',


          

question = ["Robert Müller", 
            "televize", "Nova", "ČTK", "ČT", "Prima", "Echo", "RTVS",
            "Polsatnews", "Novinář", "Novinky", "Blesk",
            "Český rozhlas", "Reuters", "Seznam", "iDNES", "iDnes", "idnes", 
            "Deník", "noviny", "rozhlas",  "Televize", "TA3", "Rádio",  "Impuls"
            "CNN", "Aktuálně", "Televizió", "Rundfunk", "deník Sport", "Právo",
            "DNES", "Associated Press", "DPA", "Aktualne", "DVTV", "E15"]


# Add new colunm for row
#

def add_role_to_dataframe(data):

    data["role"] = "other"
    
    for (index, row) in data.iterrows():
        for str_ in moderator:
            if str_ in row.speaker:
                data.loc[index, "role"] = "moderator"
                break

        for str_ in question:
            if str_ in row.speaker:
                data.loc[index, "role"] = "question"
                break

        for str_ in answer:
            if str_ in row.speaker:
                data.loc[index, "role"] = "answer"
                break

    return data


CzechMonths = {'ledna':1, 'února':2, 'března':3,'dubna':4,'května':5,
               'června':6,'července':7,'srpna':8, 'září':9,
               'října':10, 'listopadu':11, 'prosince':12 }



def correct_wrong_dates(data):
    for (month_str, month_nb) in CzechMonths.items():
        index_for_correction = data.title.str.contains(month_str) & (data.date.dt.month != month_nb)
        data.loc[index_for_correction, "date"] = data.loc[index_for_correction, "date"].apply(
            lambda x: dt.datetime.strptime(x.strftime("%Y-%d-%m %H:%M:%S"), "%Y-%m-%d %H:%M:%S"))        
    return data
 
if __name__ == "__main__":

    data = pd.read_csv("../data/conferences_2020.tsv.xz", sep='\t', header=0, parse_dates=["date"], compression="xz", encoding="utf-8")

    data = add_role_to_dataframe(data)
    data = correct_wrong_dates(data)

    data.to_csv("press_conferences_2020_cdate.tsv.xz", encoding='utf-8',
                sep='\t', header=True, index=False, compression='xz')
    
