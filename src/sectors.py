import os
import re
import json
from os import listdir
from os.path import isfile, join
import pandas as pd

def write_sectors():
    mypath= 'data/Sectors'
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    sectors = {}
    file1 = open('allsectors.json', 'w')
    file1.writelines(
        json.dumps({ re.sub(r'\d+ - (.*) - .*', '\g<1>', k): v for k, v in
                    sectors.items() }))
    file1.close()

def read_sectors(sector):
    sectors = json.load(open('allsectors.json', 'r'))
    df = pd.read_json("allsectors.json")
    s1 = pd.Series(df.Transportation[0].split(","), name="Transportation2")
    newdf = pd.DataFrame(columns=df.columns)
    dfs = []
    for col in df.columns:
       dfs.append(pd.DataFrame(df[col].str.split(",").explode().reset_index(drop=True)))
    df2 = pd.concat(dfs, axis=1, ignore_index=True)
    df2.columns = df.columns
    if sector is not None:
        tsyms = df2[[sector]].dropna()[sector].str.split(":").str[-1].values
        tsyms = ",".join(list(tsyms[3:].astype(str)))
        return tsyms
    else:
        return df2

# drop anything that has ##INDEX in it


if __name__ == "__main__":
    # write_sectors()
    df = read_sectors(None)
    import pdbr; pdbr.set_trace()
