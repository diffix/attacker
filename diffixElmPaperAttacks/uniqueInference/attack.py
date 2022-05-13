import sys
import os
import pandas as pd
import sqlite3
import pprint
import json

pp = pprint.PrettyPrinter(indent=4)

from pandas.core.accessor import register_index_accessor
filePath = __file__
parDir = os.path.abspath(os.path.join(filePath, os.pardir, os.pardir))
sys.path.append(parDir)
import tools.score
import tools.stuff

def getBasicStats(cur,res,col1,col2):
    sql = f'''
        SELECT count(DISTINCT {col1}),
            count(DISTINCT {col2})
        FROM rides
    '''
    cur.execute(sql)
    ans = cur.fetchall()
    res['distinctCol1'] = ans[0][0]
    res['distinctCol2'] = ans[0][1]
    sql = f'''
        SELECT count(*) FROM
            (SELECT DISTINCT {col1}, {col2}
            FROM rides) t
    '''
    cur.execute(sql)
    ans = cur.fetchall()
    res['totalDistinct'] = ans[0][0]

def getStrFromList(theList):
    theStr = ''
    for entry in theList:
        theStr += f"{entry[0]}, "
    theStr = theStr[:-2]
    return theStr

datasets = [
    {'csvFile':'taxi-one-day.csv',
     'col1':'trip_time_in_secs',
     'col2':'trip_distance',
     'runs': [
        {'file':'taxi-time-1-dist-1_anonymized.csv',
            'col1Bin':1,'col2Bin':1,
            'col2Null':0},
        {'file':'taxi-time-1-dist-5_anonymized.csv',
            'col1Bin':1,'col2Bin':5,
            'col2Null':0},
        {'file':'taxi-time-5-dist-5_anonymized.csv',
            'col1Bin':5,'col2Bin':5,
            'col2Null':0},
        ],
    },
    {'csvFile':'census_big.csv',
     'col1':'age',
     'col2':'len_mar_stat',
     'runs': [
        {'file':'census-age-mar_anonymized.csv',
            'col1Bin':1,'col2Bin':1,
            'col2Null':99},
        {'file':'census-age-mar_anonymized.csv',
            'col1Bin':1,'col2Bin':1,
            'swapCols':1},
        ],
    },
]

results = {}
for dataset in datasets:
    csvFile = dataset['csvFile']
    col1 = dataset['col1']
    col2 = dataset['col2']
    runs = dataset['runs']
    # First pull in the original data
    df = pd.read_csv(csvFile)
    #print(df.head())
    con = sqlite3.connect(':memory:')
    df.to_sql('rides',con,if_exists='replace',index=False)
    cur = con.cursor()
    results[csvFile] = {}

    results[csvFile]['original'] = {}
    getBasicStats(cur,results[csvFile]['original'],col1,col2)
    #pp.pprint(results)

    for run in runs:
        fileName = run['file']
        if 'swapCols' not in run:
            col1Bin = run['col1Bin']
            col2Bin = run['col2Bin']
        else:
            col2Bin = run['col1Bin']
            col1Bin = run['col2Bin']
            temp = col2
            col2 = col1
            col1 = temp
        if 'col2Null' in run:
            col2Null = run['col2Null']
        else:
            col2Null = None
        resName = f"{col1}-{col1Bin}_{col2}-{col2Bin}"
        results[csvFile][resName] = {}
        res = results[csvFile][resName]
        print(f"Run {fileName}, {resName}")
        df1 = pd.read_csv(fileName)
        #print(df1.head())
        con1 = sqlite3.connect(':memory:')
        df1.to_sql('rides',con1,if_exists='replace',index=False)
        cur1 = con1.cursor()

        getBasicStats(cur1,res,col1,col2)
        # Find all instances of unique values in anonyized data
        sql = f'''
            SELECT {col1}
            FROM rides
            GROUP BY 1
            HAVING count(*) = 1
        '''
        cur1.execute(sql)
        uniqueCol1 = cur1.fetchall()
        print(f"    {len(uniqueCol1)} {col1} with one {col2}")
        res['uniqueCol1'] = len(uniqueCol1)
        col1Str = getStrFromList(uniqueCol1)
        # Get a histogram of the number of unique values for each anon count
        sql = f'''
            SELECT count, count(*) AS num_uniques FROM
                (SELECT count
                FROM rides
                WHERE {col1} IN ({col1Str})) t
            GROUP BY 1
            ORDER BY 1,2
        '''
        cur1.execute(sql)
        cntHist = cur1.fetchall()
        res['anonCount:numUniques'] = cntHist

        # For each unique col1, I want to find out if a prediction of col2
        # is correct
        sql = f'''
            SELECT {col1}, {col2}, count
            FROM rides
            WHERE {col1} IN ({col1Str})
        '''
        cur1.execute(sql)
        anonCol1Col2List = cur1.fetchall()
        sql = f'''
            SELECT cast({col1}/{col1Bin} as integer)*{col1Bin},
                cast({col2}/{col2Bin} as integer)*{col2Bin}
            FROM rides
            WHERE {col1} IN ({col1Str})
        '''
        cur.execute(sql)
        origCol1Col2List = cur.fetchall()
        con1.close()

        compares = {}
        for thing in anonCol1Col2List:
            uCol1 = thing[0]
            uCol2 = thing[1]
            anonCnt = thing[2]
            compares[uCol1] = {'uCol2':uCol2,'numMatch':0,'numMiss':0,
                               'anonCnt':anonCnt,'NULL':0}
            if col2Null is not None and uCol2 == col2Null:
                compares[uCol1]['NULL'] = 1

        for thing in origCol1Col2List:
            uCol1 = thing[0]
            oCol2 = thing[1]
            if oCol2 == compares[uCol1]['uCol2']:
                compares[uCol1]['numMatch'] += 1
            else:
                compares[uCol1]['numMiss'] += 1
            if uCol1 not in compares:
                print(f"col1 {uCol1} not in compares!")
                quit()
            if 'oCol2s' not in compares[uCol1]:
                compares[uCol1]['oCol2s'] = {oCol2:1}
            else:
                if oCol2 in compares[uCol1]['oCol2s']:
                    compares[uCol1]['oCol2s'][oCol2] += 1
                else:
                    compares[uCol1]['oCol2s'][oCol2] = 1
        res['compare'] = compares

with open('results.json', 'w') as outfile:
    json.dump(results, outfile, indent=4)