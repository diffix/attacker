import random
import json
import os
import pandas as pd
import ineqTestsLib
import inequalities
import pprint
import matplotlib.pyplot as plt
pp = pprint.PrettyPrinter(indent=4)

'''
Goal in this attack is to try to guess the exact number of persons in any given
range.
'''

# index and value
I = 0
V = 1

def alreadyDone(resData,params):
    for i in range(len(resData['groupMin'])):
        failed = False
        for param,value in params.items():
            if resData[param][i] != value:
                failed = True
                break
        if not failed:
            return True
    return False

def updateResData(resData,params,resAttack):
    pp.pprint(resAttack)
    for param,value in params.items():
        resData[param].append(value)
    resData['P'].append(resAttack['all']['P'])
    resData['PI'].append(resAttack['all']['PI'])
    resData['singP'].append(resAttack['singles']['P'])
    resData['singPI'].append(resAttack['singles']['PI'])
    resData['groupP'].append(resAttack['grouped']['P'])
    resData['groupPI'].append(resAttack['grouped']['PI'])

def printEvalError(sb,edge,true,boxed):
    sb.print()
    edge.print()
    print(f"trueCount {len(true)}, boxedCount {len(boxed)}")
    print(f"true:  {true[:5]}")
    print(f"true:  {true[-5:]}")
    print(f"boxed: {boxed[:5]}")
    print(f"boxed: {boxed[-5:]}")

def setPandPI(thing):
    # Treat all predictions as positive predictions (i.e. we predict positively that the
    # victim is in or that the victim is out). 
    if thing['total'] == 0:
        thing['P'] = 0
        thing['PI'] = 0
    else:
        thing['P'] = round(100*(thing['correct']/thing['total']),2)
        # The following assumes that the baseline is always 50%
        thing['PI'] = round(100*((thing['P']-50)/(100-50)),2)

def buildAttack(bx,points):
    p = False
    print("------ buildAttack -------")
    start = points[0][V] - 1
    end = points[-1][V] + 1
    #end = start + 50
    # For now, let's just see what the boundaries look like
    val = start - 1
    counts = []
    vals = []
    lastCount = -1
    while True:
        edge = inequalities.edgeCompare(val,'<=')
        sb = bx.getBox(edge,points)
        boxed,true = bx.getMatchingValues(edge,sb,points)
        noise = sb.getNoise()
        noisy_count = len(boxed) + noise
        if noisy_count != lastCount:
            counts.append(noisy_count)
            vals.append(val)
            lastCount = noisy_count
        val += 0.5
        if val > end:
            break
    fileName = f"counts.png"
    plt.figure(figsize=(6, 3))
    plt.plot(counts,marker='.')
    plt.savefig(fileName)
    fileName = f"vals.png"
    plt.figure(figsize=(6, 3))
    plt.plot(vals,marker='.')
    plt.savefig(fileName)
    quit()

def makeSteps(points):
    ''' This makes edge values to try such that we make two steps with
        a non-matching value for each step with a matching value
    '''
    steps = [points[0][V]-5, points[0][V]]
    lastVal = points[0][V]
    for point in points:
        val = point[V]
        if val != lastVal:
            inc = round((val - lastVal) / 3,2)
            steps.append(lastVal + inc)
            steps.append(lastVal + (2 * inc))
            steps.append(val)
            lastVal = val
    steps.append(points[-1][V]+5)
    return steps

print("========================================================")
print("     Build Attacks")
print("========================================================")

tests = []

# Group 1
avgClusters = [2]
groupSizes = [[2,6]]
bases = [2]
points = list(range(500,510))        # For effect of random seeding
points = [500]
for cluster in avgClusters:
    for groupMin,groupMax in groupSizes:
        for base in bases:
            for numPoints in points:
                tests.append([numPoints,cluster,groupMin,groupMax,base])

'''
# Group 2
avgClusters = [1,2,5]
groupSizes = [[2,4],[2,6],[1,1],[4,8]]
bases = [5,2,1.9,1.5,1.01]
points = [500]
for cluster in avgClusters:
    for groupMin,groupMax in groupSizes:
        for base in bases:
            for numPoints in points:
                tests.append([numPoints,cluster,groupMin,groupMax,base])
'''

# Use this flag to force the given measure to be executed (i.e. ignore buildAttack.json)
force = False
if True:
    # General performance and correctness exercise
    if not force and os.path.exists('buildAttack.json'):
        with open('buildAttack.json', 'r') as f:
            resData = json.load(f)
    else:
        selected = {'groupMin':[],'groupMax':[],'cluster':[],
                    'base':[],'numPoints':[],
                    'P':[],'PI':[],'singP':[],'singPI':[],'groupP':[],'groupPI':[],}
        resData = {'bulk':[],'selected':selected}
    for [numPoints,cluster,groupMin,groupMax,base] in tests:
        random.seed(str(numPoints)+str(cluster)+str(groupMin)+str(groupMax)+str(base))
        vals = ineqTestsLib.makePointsCluster(numPoints,cluster)
        if False:
            ineqTestsLib.plotPoints(vals,cluster)
        # points is the basic dataset. From this we will remove (or not remove)
        # individual points
        points = ineqTestsLib.makePointsFromVals(vals)
        params = {
            'groupMin':groupMin,
            'groupMax':groupMax,
            'cluster':cluster,
            'base':base,
            'numPoints':numPoints,
        }
        print("Params:")
        pp.pprint(params)
        if alreadyDone(resData['selected'],params):
            print("    Already computed. Skipping.....")
            continue
        bx = inequalities.boxes(base=base,groupMin=groupMin,groupMax=groupMax)
        resAttack = buildAttack(bx,points)
        pp.pprint(resAttack)
        updateResData(resData['selected'],params,resAttack)
        resData['bulk'].append( {'params':params,'attack':resAttack} )
        if not force:
            with open('buildAttack.json', 'w') as outfile:
                json.dump(resData, outfile, indent=4)
    df = pd.DataFrame.from_dict(resData['selected'])
    print(df.to_markdown())
