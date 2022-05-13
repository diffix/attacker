import random
import json
import os
import pandas as pd
import ineqTestsLib
import statistics
import inequalities
import pprint
pp = pprint.PrettyPrinter(indent=4)

'''
This attack tries to identify edges that otherwise are meant to be hidden
(i.e. are otherwise suppressed).

It proceeds by stepping through the number space and identifying points where
there is a large count jump.

errImp is the percent relative improvement in absolute distance from guessed
hidden point to the nearest hidden point, versus the distance from all
non-points to the nearest hidden point. The larger the value, better the improvement.

errAvg is the average distance from guessed hidden point to nearest actual
hidden point, where distance forward is postive and distance backwards is negative.
errAvgAbs is the same, but with absolute value of distance. errAvg is useful for
seeing if there is a positive or negative bias (which the attacker could try to
exploit). 
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
    for param,value in params.items():
        resData[param].append(value)
    resData['visibleP'].append(resAttack['guesses']['visible']['P'])
    resData['visiblePI'].append(resAttack['guesses']['visible']['PI'])
    resData['hiddenP'].append(resAttack['guesses']['hidden']['P'])
    resData['hiddenPI'].append(resAttack['guesses']['hidden']['PI'])
    errDiff = resAttack['error']['fromNoPoint']['absAvg'] - resAttack['error']['fromHidden']['absAvg']
    errFrac = errDiff/resAttack['error']['fromNoPoint']['absAvg']
    resData['errImp'].append(round(100*errFrac,1))
    resData['errAvg'].append(round(resAttack['error']['fromHidden']['avg'],1))
    resData['errAbsAvg'].append(round(resAttack['error']['fromHidden']['absAvg'],1))
    resData['errStd'].append(round(resAttack['error']['fromHidden']['stdev'],1))

def printEvalError(sb,edge,true,boxed):
    sb.print()
    edge.print()
    print(f"trueCount {len(true)}, boxedCount {len(boxed)}")
    print(f"true:  {true[:5]}")
    print(f"true:  {true[-5:]}")
    print(f"boxed: {boxed[:5]}")
    print(f"boxed: {boxed[-5:]}")

def setPandPI(res,thing):
    # Treat all predictions as positive predictions
    guess = res['guesses'][thing]
    real = res['reality'][thing]
    baseline = 100*(real/res['totalTries'])
    if guess['total'] == 0:
        guess['P'] = 0
    else:
        guess['P'] = round(100*(guess['correct']/guess['total']),2)
        guess['PI'] = round(100*((guess['P']-baseline)/(100-baseline)),2)

def getDistToClosestHidden(val,hv):
    for i in range(1,10000000):
        if hv.pointIsHidden(val+i):
            return i
        if hv.pointIsHidden(val-i):
            return -i
    pp.pprint(hv.hidVis)
    print("ERROR")
    quit()

def findEdgesAttack(bx,points):
    p = False
    # Above visibleThresh we assume 1) there is a point, and 2) it is visible
    visibleThresh = bx.groupMax
    # Above hiddenThresh, we assume 1) there is a point, and 2) it is hidden
    # At hiddenThresh and below, we assume nothing
    hiddenThresh = bx.groupMin
    # In the following, 'total' means total number of positive predictions
    #    'correct' means true positives
    # The error is the distance to the nearest hidden point (for all noPoint vals,
    # and for all false positive hidden guesses)
    print(f"------ findEdgesAttack ({visibleThresh}, {hiddenThresh}) -------")
    res = {'guesses': {'hidden':{'correct':0, 'total':0, 'P':0, 'PI':0,},
                       'visible':{'correct':0, 'total':0, 'P':0, 'PI':0,},
                       'noPoint':{'correct':0, 'total':0, 'P':0, 'PI':0,},
                      },
           'reality': {'hidden':0, 'visible':0, 'noPoint':0},
           'totalTries':0,
           'error':{ 'fromNoPoint':{'avg':0,'stdev':0,'absAvg':0},
                     'fromHidden':{'avg':0,'stdev':0,'absAvg':0},
                   }
          }
    errorFromNoPoint = []
    errorFromHiddenGuess = []
    hv = inequalities.getHiddenAndVisible(bx,points)
    if p: print(f"{hv.numHidden} hidden points, {hv.numVisible} visible points")
    if p: pp.pprint(hv.hidVis)
    if p: pp.pprint(points)
    for val in range(points[0][V]-1,points[-1][V]+1):
        lval = val - 0.5   # left of value
        rval = val + 0.5   # right of value

        edgeLeft = inequalities.edgeCompare(lval,'<')
        sbLeft = bx.getBox(edgeLeft,points)
        boxedLeft,trueLeft,_ = bx.getMatchingValues(edgeLeft,sbLeft,points)
        noiseLeft = sbLeft.getNoise()
        noisyCountLeft = len(boxedLeft) + noiseLeft

        edgeRight = inequalities.edgeCompare(rval,'<')
        sbRight = bx.getBox(edgeRight,points)
        boxedRight,trueRight,_ = bx.getMatchingValues(edgeRight,sbRight,points)
        noiseRight = sbRight.getNoise()
        noisyCountRight = len(boxedRight) + noiseRight

        # Aha, most of these noise values are identical left and right...

        diff = noisyCountRight - noisyCountLeft
        diffTrue = len(trueRight) - len(trueLeft)
        if not hv.pointExists(val):
            status = 'noPoint'
            distToClosestHidden = getDistToClosestHidden(val,hv)
            errorFromNoPoint.append(distToClosestHidden)
        elif hv.pointIsVisible(val):
            status = 'visible'
        else:
            status = 'hidden'
        if diff > visibleThresh:
            guess = 'visible'
        elif diff > hiddenThresh:
            guess = 'hidden'
        else:
            guess = 'noPoint'

        if status == 'noPoint' and guess == 'hidden':
            errorFromHiddenGuess.append(distToClosestHidden)

        if p: print(f"val {val}, is {status}, guess {guess} (noisy diff {diff}, true diff {diffTrue})")

        res['totalTries'] += 1
        res['guesses'][guess]['total'] += 1
        res['reality'][status] += 1
        if guess == status:
            res['guesses'][guess]['correct'] += 1
            if p:
                if status != 'noPoint':
                    print("   HIT")
    setPandPI(res,'hidden')
    setPandPI(res,'visible')
    setPandPI(res,'noPoint')
    if len(errorFromHiddenGuess) > 0:
        res['error']['fromHidden']['avg'] = statistics.mean(errorFromHiddenGuess)
        res['error']['fromHidden']['stdev'] = statistics.stdev(errorFromHiddenGuess)
        res['error']['fromHidden']['absAvg'] = statistics.mean([abs(x) for x in errorFromHiddenGuess])
    if len(errorFromNoPoint) > 0:
        res['error']['fromNoPoint']['avg'] = statistics.mean(errorFromNoPoint)
        res['error']['fromNoPoint']['stdev'] = statistics.stdev(errorFromNoPoint)
        res['error']['fromNoPoint']['absAvg'] = statistics.mean([abs(x) for x in errorFromNoPoint])
    return res

def addToTests(tests,avgClusters,groupSizes,suppressSizes,bases,points):
    for cluster in avgClusters:
        for groupMin,groupMax in groupSizes:
            for base in bases:
                for numPoints in points:
                    for suppressMin,suppressMax in suppressSizes:
                        if suppressMin is None:
                            suppressMin = groupMin
                            suppressMax = groupMax
                        tests.append([numPoints,cluster,groupMin,groupMax,suppressMin,suppressMax,base])

print("========================================================")
print("     Find Edges Attacks")
print("========================================================")

tests = []

# Test
avgClusters = [1,5,10]
#avgClusters = [10]
groupSizes = [[2,6],[20,30]]
#groupSizes = [[20,30]]
suppressSizes = [[2,6],[20,30]]
#suppressSizes = [[20,30]]
bases = [2,5,10]
points = [5000]
addToTests(tests,avgClusters,groupSizes,suppressSizes,bases,points)

# Use this flag to force the given measure to be executed (i.e. ignore findEdgesAttack.json)
force = False
if True:
    # General performance and correctness exercise
    if not force and os.path.exists('findEdgesAttack.json'):
        with open('findEdgesAttack.json', 'r') as f:
            resData = json.load(f)
    else:
        selected = {'groupMin':[],'groupMax':[],'cluster':[],'suppressMin':[],'suppressMax':[],
                    'base':[],'numPoints':[],
                    'hiddenP':[],'hiddenPI':[],'visibleP':[],'visiblePI':[],
                    'errImp':[],'errAvg':[],'errAbsAvg':[],'errStd':[],
                    }
        resData = {'bulk':[],'selected':selected}
    for [numPoints,cluster,groupMin,groupMax,suppressMin,suppressMax,base] in tests:
        random.seed(str(numPoints)+str(cluster)+str(groupMin)+str(groupMax)+str(suppressMin)+str(suppressMax)+str(base))
        vals = ineqTestsLib.makePointsCluster(numPoints,cluster)
        if False:
            ineqTestsLib.plotPoints(vals,cluster)
        # points is the basic dataset. From this we will remove (or not remove)
        # individual points
        points = ineqTestsLib.makePointsFromVals(vals)
        params = {
            'groupMin':groupMin,
            'groupMax':groupMax,
            'suppressMin':suppressMin,
            'suppressMax':suppressMax,
            'cluster':cluster,
            'base':base,
            'numPoints':numPoints,
        }
        print("Params:")
        pp.pprint(params)
        if alreadyDone(resData['selected'],params):
            print("    Already computed. Skipping.....")
            continue
        bx = inequalities.boxes(base=base,groupMin=groupMin,groupMax=groupMax,suppressMin=suppressMin,suppressMax=suppressMax)
        resAttack = findEdgesAttack(bx,points)
        updateResData(resData['selected'],params,resAttack)
        resData['bulk'].append( {'params':params,'attack':resAttack} )
        #pp.pprint(resData)
        if not force:
            with open('findEdgesAttack.json', 'w') as outfile:
                json.dump(resData, outfile, indent=4)
    df = pd.DataFrame.from_dict(resData['selected'])
    print(df.to_markdown())