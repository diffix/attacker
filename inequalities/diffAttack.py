import random
import json
import os
import pandas as pd
import ineqTestsLib
import inequalities
import pprint
pp = pprint.PrettyPrinter(indent=4)

'''
This file mimics an attack whereby the attacker is able to remove the victim
from the answer. In other words, a difference attack where one query may or may
not contain the victim, and the other query definately excludes the victim.

In practice, LED prevents this, but here we just want to demonstrate the need for LED.
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

def diffAttack(bx,points):
    p = False
    print("------ diffAttack -------")
    # Separately keep track of how well the attack works on singleton victims
    # and victims where other persons match their value
    res = {'all':{'correct':0, 'total':0, 'P':0, 'PI':0,},
           'singles':{'correct':0, 'total':0, 'P':0, 'PI':0,},
           'grouped':{'correct':0, 'total':0, 'P':0, 'PI':0,},
           'victimIn':{
               'singles':{'correct':0, 'total':0, 'P':0, 'PI':0,},
               'grouped':{'correct':0, 'total':0, 'P':0, 'PI':0,}, },
           'victimOut':{
               'singles':{'correct':0, 'total':0, 'P':0, 'PI':0,},
               'grouped':{'correct':0, 'total':0, 'P':0, 'PI':0,}, },
          }
    for i in range(1,len(points)-1):
        lval = points[i-1][V]   # last value
        tval = points[i][V]     # this value
        nval = points[i+1][V]   # next value
        res['all']['total'] += 1
        if lval != tval and nval != tval:
            singlesType = 'singles'
        else:
            singlesType = 'grouped'
        edge = inequalities.edgeCompare(tval,'<=')
        # first query is on dataset with victim in
        sb_in = bx.getBox(edge,points)
        boxed_in,true_in = bx.getMatchingValues(edge,sb_in,points)
        noise_in = sb_in.getNoise()
        noisy_count_in = len(boxed_in) + noise_in
        # second query we randomly decide to include or exclude the victim
        reality = 'victimIn'
        if random.randint(0,1000) <= 500:
            # take the victim out
            reality = 'victimOut'
            popped = points.pop(i)
        sb_out = bx.getBox(edge,points)
        boxed_out,true_out = bx.getMatchingValues(edge,sb_out,points)
        noise_out = sb_out.getNoise()
        noisy_count_out = len(boxed_out) + noise_out
        res[singlesType]['total'] += 1
        res[reality][singlesType]['total'] += 1
        if reality == 'victimOut':
            # put the victim back
            points.insert(i,popped)
        if noisy_count_out == noisy_count_in:
            guess = 'victimIn'
        else:
            guess = 'victimOut'
        if guess == reality:
            res['all']['correct'] += 1
            res[singlesType]['correct'] += 1
            res[reality][singlesType]['correct'] += 1
        if p: print(f'i {i}, val {tval}, reality {reality}, guess {guess}, type {singlesType}')
        if p: edge.print()
        if p: sb_in.print()
        if p: sb_out.print()
    pass
    setPandPI(res['all'])
    setPandPI(res['singles'])
    setPandPI(res['victimIn']['singles'])
    setPandPI(res['victimOut']['singles'])
    setPandPI(res['grouped'])
    setPandPI(res['victimIn']['grouped'])
    setPandPI(res['victimOut']['grouped'])
    return res

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
print("     Diff Attacks")
print("========================================================")

tests = []

# Group 1
avgClusters = [2]
groupSizes = [[2,6]]
bases = [2]
points = list(range(500,510))        # For effect of random seeding
for cluster in avgClusters:
    for groupMin,groupMax in groupSizes:
        for base in bases:
            for numPoints in points:
                tests.append([numPoints,cluster,groupMin,groupMax,base])

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

# Use this flag to force the given measure to be executed (i.e. ignore diffAttack.json)
force = False
if True:
    # General performance and correctness exercise
    if not force and os.path.exists('diffAttack.json'):
        with open('diffAttack.json', 'r') as f:
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
        resAttack = diffAttack(bx,points)
        pp.pprint(resAttack)
        updateResData(resData['selected'],params,resAttack)
        resData['bulk'].append( {'params':params,'attack':resAttack} )
        if not force:
            with open('diffAttack.json', 'w') as outfile:
                json.dump(resData, outfile, indent=4)
    df = pd.DataFrame.from_dict(resData['selected'])
    print(df.to_markdown())
