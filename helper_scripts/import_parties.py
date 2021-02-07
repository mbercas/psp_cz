
#!/usr/bin/python

import pandas as pd


fn_1993 = './psp1993_1996/speakers_summary.tsv'
fn_1996 = './psp1996_1998/speakers_summary.tsv'
fn_1998 = './psp1998_2002/speakers_summary.tsv'
fn_2002 = './psp2002_2006/speakers_summary.tsv'
fn_2006 = './psp2006_2010/speakers_summary.tsv'



df1993 = pd.read_csv(fn_1993, sep='\t', encoding='utf-8', header=0)
df1996 = pd.read_csv(fn_1996, sep='\t', encoding='utf-8', header=0)
df1998 = pd.read_csv(fn_1998, sep='\t', encoding='utf-8', header=0)
df2002 = pd.read_csv(fn_2002, sep='\t', encoding='utf-8', header=0)
df2006 = pd.read_csv(fn_2006, sep='\t', encoding='utf-8', header=0)


found = 0
for idx, row in df1996.iterrows():
    print(f"{row['steno_name']=} - {df1996.loc[idx,'party']=}")

    if sum(df1993.steno_name == df1996.iloc[idx]["steno_name"]) > 0:
        df1993.at[df1993.steno_name == df1996.iloc[idx]["steno_name"],'name'] = df1996.loc[idx,"name"]
        df1993.at[df1993.steno_name == df1996.iloc[idx]["steno_name"],'titles'] = df1996.loc[idx, "titles"]
        df1993.at[df1993.steno_name == df1996.iloc[idx]["steno_name"],'party'] = df1996.loc[idx, "party"]
        df1993.at[df1993.steno_name == df1996.iloc[idx]["steno_name"],'birthdate'] = df1996.loc[idx, "birthdate"]

        found += 1
        print(f"{found=} - {df1993[df1993.name == df1996.loc[idx, 'name']]['party']}")


print(f"{found=}")


for idx, row in df1993.iterrows():
    if pd.isna(row["name"]):
        sn = row.steno_name.split()
        name = ""
        for w in sn[-2:]:
            name += w.capitalize() + " "
        name =  name.strip()
        df1993.at[idx, "name"] = name

for idx, row in df1993.iterrows():
    name = row["name"].lower()
    function = row.steno_name.replace(name, "").strip()
    df1993.at[idx, "function"]  = function




df1993.to_csv('speakers_summary_1993_1996.tsv', sep='\t', encoding='utf-8', header=True, index=False)
#print(df2002)
