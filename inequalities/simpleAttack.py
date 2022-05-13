import random
import statistics
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import ineqTestsLib
import inequalities
import pprint
pp = pprint.PrettyPrinter(indent=4)

'''
This file contains a simple attack whereby the attacker knows that there is either
zero or one person with a given value. It tries to determine whether the person is there
using two queries, one with an inequality just above the value, and one just below. Then
it assumes the person is there if the answers differ.

This file also contains basic error measures. Output is stored in simpleAttack.json,
and simpleAttack.ipynb is a workbook displaying the results.
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

def updateResData(resData,params,res,resAttack):
    for param,value in params.items():
        resData[param].append(value)
    resData['trueErrAvg'].append(res['trueErrorAvg'])
    resData['trueErrStd'].append(res['trueErrorStd'])
    resData['noisyErrAvg'].append(res['noisyErrorAvg'])
    resData['noisyErrStd'].append(res['noisyErrorStd'])
    resData['noisyDiffsAvg'].append(res['noisyDiffsAvg'])
    resData['noisyDiffsStd'].append(res['noisyDiffsStd'])
    resData['zeroSame'].append(res['zeroPersonBoxSame'])
    resData['zeroChange'].append(res['zeroPersonBoxChange'])
    resData['oneSame'].append(res['onePersonBoxSame'])
    resData['oneChange'].append(res['onePersonBoxChange'])
    resData['P'].append(resAttack['P'])
    resData['PI'].append(resAttack['PI'])
    resData['baseline'].append(resAttack['baseline'])

def printEvalError(sb,edge,true,boxed):
    sb.print()
    edge.print()
    print(f"trueCount {len(true)}, boxedCount {len(boxed)}")
    print(f"true:  {true[:5]}")
    print(f"true:  {true[-5:]}")
    print(f"boxed: {boxed[:5]}")
    print(f"boxed: {boxed[-5:]}")

def simpleAttack(bx,points):
    p = False
    print("------ simpleAttack -------")
    # First find values to attack
    singletons = []
    empties = []
    VAL=0
    DIST=1
    IX=2
    GUESS=3
    for i in range(1,len(points)-1):
        lval = points[i-1][V]   # last value
        tval = points[i][V]     # this value
        nval = points[i+1][V]   # next value
        if lval != tval and nval != tval:
            # This is a singleton
            dist = min(tval-lval,nval-tval)
            singletons.append([tval,dist,i])
            #print(f"singleton vals:[{lval},{tval},{nval}], i {i}, dist {dist}")
        if tval - lval > 1:
            # There is an empty
            # This empty is the furthest distance from anything
            emptyVal = int(round(lval+(tval-lval)/2))
            dist = min(emptyVal-lval,tval-emptyVal)
            empties.append([emptyVal,dist,i-dist])
            #print(f"empties vals:[{lval},{emptyVal},{tval}], i {i-dist}, dist {dist}")
    for i in range(len(singletons)):
        val = singletons[i][VAL]
        guess,edge_in,sb_in,edge_out,sb_out = oneSimpleAttack(bx,val,points)
        if guess == 'victim in':
            if p: print('VICTIM IN CORRECT')
            singletons[i].append(1)
        else:
            if p: print('VICTIM IN WRONG')
            singletons[i].append(0)
        if p: edge_in.print()
        if p: sb_in.print()
        if p: edge_out.print()
        if p: sb_out.print()
    for i in range(len(empties)):
        val = empties[i][VAL]
        guess,_,_,_,_ = oneSimpleAttack(bx,val,points)
        if guess == 'victim in':
            empties[i].append(1)
        else:
            empties[i].append(0)
    sGuesses = [0]
    if len(singletons) > 0:
        _,_,_,sGuesses = zip(*singletons)
    eGuesses = [0]
    if len(empties) > 0:
        _,_,_,eGuesses = zip(*empties)
    res= {'singletons':{'correct':sum(sGuesses),'percent':0,'total':len(sGuesses)},
          'empties':{'correct':len(eGuesses)-sum(eGuesses),'percent':0,'total':len(eGuesses)},
          'baseline':0,'P':0,'PI':0,'baseline':0,
          }
    res['singletons']['percent'] = round(100*(sum(sGuesses)/len(sGuesses)),2)
    res['empties']['percent'] = round(100*((len(eGuesses)-sum(eGuesses))/len(eGuesses)),2)
    # Baseline is the precision of just guessing 'victimIn' every time
    baseline = 100 * (len(singletons)/(len(singletons)+len(empties)))
    # Actual precision is the true positivies over all positives
    positives = sum(sGuesses)+sum(eGuesses)
    P = 100 * (sum(sGuesses)/positives)
    # Precision improvement is:
    res['PI'] = round(100*((P-baseline)/(100-baseline)),2)
    res['baseline'] = round(baseline,2)
    res['P'] = round(P,2)
    return res

def oneSimpleAttack(bx,val,points):
    ''' In this attack, we assume that there is a higher probability of selecting
        a new box if the victim is present. So we use that as our signal.
    '''
    p = True
    # first query includes victim with value val
    edge_in = inequalities.edgeCompare(val+0.5,'<')
    sb_in = bx.getBox(edge_in,points)
    boxed_in,true_in,_ = bx.getMatchingValues(edge_in,sb_in,points)
    noise_in = sb_in.getNoise()
    noisy_count_in = len(boxed_in) + noise_in
    # second query excludes victim
    edge_out = inequalities.edgeCompare(val-0.5,'<')
    sb_out = bx.getBox(edge_out,points)
    boxed_out,true_out,_ = bx.getMatchingValues(edge_out,sb_out,points)
    noise_out = sb_out.getNoise()
    noisy_count_out = len(boxed_out) + noise_out
    if noisy_count_in != noisy_count_out:
        return 'victim in',edge_in,sb_in,edge_out,sb_out
    else:
        return 'victim out',edge_in,sb_in,edge_out,sb_out

def makeSteps(points):
    ''' This makes edge values to try such that we make two steps with
        a non-matching value for each step with a matching value. Do this
        just as an optimization.
    '''
    start = -0.5
    steps = []
    while start <= points[-1][V] + 1:
        steps.append(start)
        start += 1
    return steps
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

def evaluate(bx,operation,points,minVal,maxVal):
    '''
        We want to know:
          * When there is a change of box, how many persons were changed
          * When one person changes, how often does box change
    '''
    lastSb = None
    lastEdgeVal = None
    lastIndex = None
    totalTries = 0
    boxChangePersons = {}
    boxSamePersons = {}
    onePersonBoxChange = 0
    onePersonBoxSame = 0
    morePersonBoxChange = 0
    morePersonBoxSame = 0
    zeroPersonBoxChange = 0
    zeroPersonBoxSame = 0
    reverseOp = {'<':'>=','>':'<=','<=':'>','>=':'<'}
    data = {'trueError':[],'boxWidth':[],'boxLeft':[],'trueCount':[],'boxedCount':[],'noisyCount':[],
            'trueDiffs':[],'noisyDiffs':[],'noisyError':[],'hiddenVals':[],'visibleVals':[],
            'edgeVal':[],'boxMid':[],'nonSuppVals':[],
            }
    steps = makeSteps(points)
    trueDiff = None
    noisyDiff = None
    lastTrueCount = -1
    lastNoisyCount = 0
    hv = inequalities.getHiddenAndVisible(bx,points)
    data['hiddenVals'] = hv.hiddenVals
    data['visibleVals'] = hv.visibleVals
    print(data['visibleVals'])
    rb = ineqTestsLib.rememberBoxes()
    print(f"Num Hidden = {hv.numHidden}, Num Visible = {hv.numVisible}")
    for edgeVal in steps:
        totalTries += 1
        edge = inequalities.edgeCompare(edgeVal,operation)
        sb = bx.getBox(edge,points)
        rb.addBox(sb)
        if False:
            print('-----------------------')
            edge.print()
            sb.print()
        data['boxWidth'].append(sb.width)
        data['boxLeft'].append(sb.left)
        data['boxMid'].append(sb.midpoint())
        boxed,true,numNonSuppVals = bx.getMatchingValues(edge,sb,points)
        noise = sb.getNoise(hv)
        noisyCount = len(boxed) + noise
        if lastTrueCount == -1:
            lastTrueCount = len(true)
        if lastTrueCount != len(true):
            trueDiff = len(true) - lastTrueCount
            lastTrueCount = len(true)
            data['trueDiffs'].append(trueDiff)
            noisyDiff = noisyCount - lastNoisyCount
            lastNoisyCount = noisyCount
            data['noisyDiffs'].append(noisyDiff)
            pass
        data['noisyError'].append(len(true)-noisyCount)
        error = len(true)-len(boxed)
        data['trueError'].append(error)
        data['trueCount'].append(len(true))
        data['boxedCount'].append(len(boxed))
        data['noisyCount'].append(noisyCount)
        data['nonSuppVals'].append(numNonSuppVals)
        data['edgeVal'].append(edgeVal)
        if error > max(bx.suppressMax,bx.groupMax) * 3:
            print(f"Error {error} greater than {max(bx.suppressMax,bx.groupMax) * 3}")
            printEvalError(sb,edge,true,boxed)
            quit()
        if False:
            # Make sure we don't lose or duplicate points
            op_rev = reverseOp[operation]
            edge_rev = inequalities.edgeCompare(edgeVal,op_rev)
            sb_rev = bx.getBox(edge_rev,points)
            boxed_rev,true_rev,numNonSuppVals = bx.getMatchingValues(edge_rev,sb_rev,points)
            if len(true_rev) + len(true) != len(points):
                print(f"True counts error ({len(true_rev)}, {len(true)}, {len(points)})")
                print(f"Operation {operation}:")
                printEvalError(sb,edge,true,boxed)
                print(f"Operation {op_rev}:")
                printEvalError(sb_rev,edge_rev,true_rev,boxed_rev)
                quit()
            if len(boxed_rev) + len(boxed) != len(points):
                print(f"Boxed counts error ({len(boxed_rev)}, {len(boxed)}, {len(points)})")
                print(f"Operation {operation}:")
                printEvalError(sb,edge,true,boxed)
                print(f"Operation {op_rev}:")
                printEvalError(sb_rev,edge_rev,true_rev,boxed_rev)
                quit()

        index = bx.adjHint
        bx.adjHint -= 20
        bx.useHint = True
        if not lastSb:
            lastSb = sb
            lastEdgeVal = edgeVal
            lastIndex = index
            continue
        numChangedPersons = index - lastIndex
        if not sb.boxesAreEqual(lastSb):
            if numChangedPersons in boxChangePersons:
                boxChangePersons[numChangedPersons] += 1
            else:
                boxChangePersons[numChangedPersons] = 1
        else:
            if numChangedPersons in boxSamePersons:
                boxSamePersons[numChangedPersons] += 1
            else:
                boxSamePersons[numChangedPersons] = 1
        if numChangedPersons == 0:
            # Zero persons changed
            if sb.boxesAreEqual(lastSb):
                zeroPersonBoxSame += 1
            else:
                zeroPersonBoxChange += 1
        if numChangedPersons >= 2:
            # More than one persons changed
            if sb.boxesAreEqual(lastSb):
                morePersonBoxSame += 1
            else:
                morePersonBoxChange += 1
        if numChangedPersons == 1:
            # Only one person changed
            if sb.boxesAreEqual(lastSb):
                onePersonBoxSame += 1
            else:
                onePersonBoxChange += 1
                '''
                print("------------------------------")
                print(f"index {lastIndex} --> {index} ({numChangedPersons}), value {lastEdgeVal} --> {edgeVal}")
                print("last result")
                lastSb.print()
                print("this result")
                sb.print()
                '''
        lastSb = sb
        lastEdgeVal = edgeVal
        lastIndex = index
    print(data['nonSuppVals'])
    return {'boxChangedPersons':boxChangePersons,
            'boxSamePersons':boxSamePersons,
            'zeroPersonBoxSame':zeroPersonBoxSame,
            'zeroPersonBoxChange':zeroPersonBoxChange,
            'onePersonBoxSame':onePersonBoxSame,
            'onePersonBoxChange':onePersonBoxChange,
            'morePersonBoxSame':morePersonBoxSame,
            'morePersonBoxChange':morePersonBoxChange,
            'totalTries':totalTries,
            'numBoxes':rb.numBoxes(),
            'numVisible':hv.numVisible,
            'numHidden':hv.numHidden,
            'trueErrorAvg':statistics.mean(data['trueError']),
            'trueErrorStd':statistics.stdev(data['trueError']),
            'noisyErrorAvg':statistics.mean(data['noisyError']),
            'noisyErrorStd':statistics.stdev(data['noisyError']),
            'trueDiffsAvg':statistics.mean(data['trueDiffs']),
            'trueDiffsStd':statistics.stdev(data['trueDiffs']),
            'noisyDiffsAvg':statistics.mean(data['noisyDiffs']),
            'noisyDiffsStd':statistics.stdev(data['noisyDiffs']),
           }, data

def addToTests(tests,avgClusters,groupSizes,suppressSizes,bases,operations,points):
    for cluster in avgClusters:
        for groupMin,groupMax in groupSizes:
            for operation in operations:
                for base in bases:
                    for numPoints in points:
                        for suppressMin,suppressMax in suppressSizes:
                            if suppressMin is None:
                                suppressMin = groupMin
                                suppressMax = groupMax
                            tests.append([numPoints,cluster,groupMin,groupMax,suppressMin,suppressMax,operation,base])

print("========================================================")
print("     Perf tests")
print("========================================================")

tests = []

# Test
avgClusters = [1,10]
avgClusters = [10]
groupSizes = [[2,6],[20,30]]
groupSizes = [[20,30]]
suppressSizes = [[2,6],[20,30]]
suppressSizes = [[20,30]]
bases = [2]
operations = [ ['<','lt'] ]
points = [500]
addToTests(tests,avgClusters,groupSizes,suppressSizes,bases,operations,points)

if False:
    # Group 1
    avgClusters = [10]
    groupSizes = [[2,4],[2,6]]
    suppressSizes = [[None,None]]
    bases = [5,2,1.9,1.5]
    operations = [ ['<=','lte'] ]
    points = [5000]
    addToTests(tests,avgClusters,groupSizes,suppressSizes,bases,operations,points)

    # Group 2
    avgClusters = [1,2,5]
    groupSizes = [[2,4],[2,6],[1,1],[4,8]]
    suppressSizes = [[None,None]]
    bases = [5,2,1.9,1.5,1.01]
    operations = [ ['<=','lte'],['<','lt'],['>=','gte'],['>','gt'], ]
    points = [5000]
    addToTests(tests,avgClusters,groupSizes,suppressSizes,bases,operations,points)

    # Group 5 (more random seed testing)
    avgClusters = [1]
    groupSizes = [[4,8]]
    suppressSizes = [[None,None]]
    bases = [1.9, 2.0]
    operations = [ ['<=','lte'] ]
    # This effectively generates different seeds
    points = [600]
    addToTests(tests,avgClusters,groupSizes,suppressSizes,bases,operations,points)

# Use this flag to force the given measure to be executed (i.e. ignore simpleAttack.json)
force = True
if True:
    # General performance and correctness exercise
    if not force and os.path.exists('simpleAttack.json'):
        with open('simpleAttack.json', 'r') as f:
            resData = json.load(f)
    else:
        selected = {'groupMin':[],'groupMax':[],'cluster':[],
                    'suppressMin':[],'suppressMax':[],
                    'op':[],'base':[],'numPoints':[],
                    'trueErrAvg':[],'trueErrStd':[],'P':[],'PI':[],'baseline':[],
                    'noisyErrAvg':[],'noisyErrStd':[],'noisyDiffsAvg':[],'noisyDiffsStd':[],
                    'oneSame':[],'oneChange':[],'zeroSame':[],'zeroChange':[],
                    }
        resData = {'bulk':[],'selected':selected}
    for [numPoints,cluster,groupMin,groupMax,suppressMin,suppressMax,operation,base] in tests:
        random.seed(str(numPoints)+str(cluster)+str(groupMin)+str(groupMax)+str(suppressMin)+str(suppressMax)+str(operation)+str(base))
        vals = ineqTestsLib.makePointsCluster(numPoints,cluster)
        if False:
            ineqTestsLib.plotPoints(vals,cluster)
        points = ineqTestsLib.makePointsFromVals(vals)
        #print(points)
        params = {
            'groupMin':groupMin,
            'groupMax':groupMax,
            'suppressMin':suppressMin,
            'suppressMax':suppressMax,
            'cluster':cluster,
            'base':base,
            'numPoints':numPoints,
            'op':operation[1],
        }
        print("Params:")
        pp.pprint(params)
        if alreadyDone(resData['selected'],params):
            print("    Already computed. Skipping.....")
            continue
        bx = inequalities.boxes(base=base,groupMin=groupMin,groupMax=groupMax,suppressMin=suppressMin,suppressMax=suppressMax)
        res,data = evaluate(bx,operation[0],points,min(vals),max(vals))
        print("Results:")
        pp.pprint(res)
        if True:
            nonSupp = [a*10 for a in data['nonSuppVals']]
            fileName = ineqTestsLib.getNameFromParams(params)
            temp = fileName + 'boxedVsTrueCount' + '.png'
            plt.figure(figsize=(6, 3))
            plt.plot(data['edgeVal'][0:80],data['boxedCount'][0:80],linestyle='None',marker='.',alpha=0.5)
            plt.plot(data['edgeVal'][0:80],data['trueCount'][0:80],linestyle='None',marker='.',alpha=0.5)
            plt.plot(data['edgeVal'][0:80],nonSupp[0:80],linestyle='None',marker='.',alpha=0.5)
            plt.savefig(temp)
            temp = fileName + 'noisyVsTrueCount' + '.png'
            plt.figure(figsize=(6, 3))
            plt.plot(data['edgeVal'][0:80],data['noisyCount'][0:80],linestyle='None',marker='.',alpha=0.5)
            plt.plot(data['edgeVal'][0:80],data['trueCount'][0:80],linestyle='None',marker='.',alpha=0.5)
            plt.plot(data['edgeVal'][0:80],nonSupp[0:80],linestyle='None',marker='.',alpha=0.5)
            plt.savefig(temp)
            temp = fileName + 'noisyVsBoxedCount' + '.png'
            plt.figure(figsize=(6, 3))
            plt.plot(data['edgeVal'][0:80],data['noisyCount'][0:80],linestyle='None',marker='.',alpha=0.5)
            plt.plot(data['edgeVal'][0:80],data['boxedCount'][0:80],linestyle='None',marker='.',alpha=0.5)
            plt.plot(data['edgeVal'][0:80],nonSupp[0:80],linestyle='None',marker='.',alpha=0.5)
            plt.savefig(temp)
            temp = fileName + 'noisyVsMidCount' + '.png'
            plt.figure(figsize=(6, 3))
            plt.plot(data['edgeVal'][0:80],data['noisyCount'][0:80],linestyle='None',marker='.',alpha=0.5)
            plt.plot(data['edgeVal'][0:80],data['boxMid'][0:80],linestyle='None',marker='.',alpha=0.5)
            plt.plot(data['edgeVal'][0:80],nonSupp[0:80],linestyle='None',marker='.',alpha=0.5)
            plt.savefig(temp)
        if False:
            for key in data.keys():
                temp = fileName + key + '.png'
                plt.figure(figsize=(6, 3))
                plt.plot(data[key],linestyle='None',marker='.')
                plt.savefig(temp)
                if len(data[key]) == len(data['edgeVal']):
                    temp = fileName + key + 'VsEdge.png'
                    plt.figure(figsize=(6, 3))
                    plt.plot(data['edgeVal'],data[key],linestyle='None',marker='.')
                    plt.savefig(temp)
                    pass
        resAttack = simpleAttack(bx,points)
        pp.pprint(resAttack)
        updateResData(resData['selected'],params,res,resAttack)
        resData['bulk'].append( {'params':params,'perf':res,'attack':resAttack} )
        if not force:
            with open('simpleAttack.json', 'w') as outfile:
                json.dump(resData, outfile, indent=4)
    df = pd.DataFrame.from_dict(resData['selected'])
    print(df.to_markdown())