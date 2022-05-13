import random
import matplotlib.pyplot as plt
import pprint
pp = pprint.PrettyPrinter(indent=4)

'''
This software does something like the document inequalities.md.
Doesn't really work. Too many cases where moving an edge across a point
causes a change of box.
'''

class boxes():
    def __init__(self,params):
        self.groupMin = params['groupMin']
        self.groupMax = params['groupMax']
        self.numPoints = params['numPoints']
        self.boxMult = 1.4
        pass

    def printBoxSizes(self):
        boxSize = 1
        print("Box Sizes:")
        while True:
            print(f"{round(boxSize)}, ",end='')
            if round(boxSize) >= self.numPoints:
                break
            boxSize *= self.boxMult
        print('')

    def getBox(self,p,points):
        '''
            Goal is to find the smallest box that 1) includes the
            edge-most "in" point, and 2) includes enough AIDVs. Note
            that the AIDV-set does not itself need to include the
            edge-most "in" point.
        '''
        # Assumes that i and everything to the left is in
        # Everything to the right is out
        self.minIndex = 0
        self.maxIndex = len(points)-1
        self.edgeValue = points[p]
        self.getGroups(p,points)
        self.getBoxesFromGroups()
        bestBox, bestAidvs = self.getBestBox()
        aidvVals = [points[i] for i in bestAidvs]
        #pp.pprint(self.groups)
        return {'box':bestBox,'aidv':bestAidvs,'aidvVals':aidvVals}

    def getBestBox(self):
        minBoxSize = 10000000000
        for group in self.groups:
            #print(group)
            boxSize = group['box'][1] - group['box'][0]
            minBoxSize = min(minBoxSize,boxSize)
        bestBox = None
        bestAidvs = None
        for group in self.groups:
            boxSize = group['box'][1] - group['box'][0]
            if boxSize != minBoxSize:
                continue
            if not bestBox:
                bestBox = group['box']
                bestAidvs = group['aidvs']
                #print(f"    best box is {bestBox}, {bestAidvs}")
                continue
            if group['box'][0] < bestBox[0]:
                bestBox = group['box']
                bestAidvs = group['aidvs']
                #print(f"    even better best box is {bestBox}, {bestAidvs}")
        if not bestBox:
            print(f"getBestBox failed on {self.groups}")
            quit()
        return bestBox, bestAidvs

    def getPossibleBoxSizes(self,minPossible):
        # dumb brute force for now
        boxSize = 1
        while True:
            if round(boxSize) >= minPossible:
                break
            boxSize *= self.boxMult
        # we have the smallest box size. Now get 3 more, just to
        # avoid the above loop next time
        possibles = [round(boxSize)]
        for _ in range(3):
            boxSize *= self.boxMult
            possibles.append(round(boxSize))
        return list(set(possibles))

    def getBoxesFromGroups(self):
        '''
            We want a box that covers the group values as well as the
            edge-most value
        '''
        for i in range(len(self.groups)):
            group = self.groups[i]
            #print(f"do {group}")
            boxLeft = min(group['group'][0],self.edgeValue)
            boxRight = max(group['group'][-1],self.edgeValue)
            if boxLeft == boxRight:
                self.groups[i]['box'] = [boxLeft,boxRight]
                continue
            minBoxSize = boxRight - boxLeft
            #print(f"    left {boxLeft}, right {boxRight}, min size {minBoxSize}")
            possBoxSizes = self.getPossibleBoxSizes(minBoxSize)
            #print(f"    possible sizes: {possBoxSizes}")
            for boxSize in possBoxSizes:
                box = self.getFittingBox(boxLeft,boxRight,boxSize)
                if not box:
                    continue
                self.groups[i]['box'] = box
                break
            if 'box' not in self.groups[i]:
                print(f"Failed {i} of {self.groups}")
                quit()

    def getFittingBox(self,boxLeft,boxRight,boxSize):
        left = 0
        shiftSize = boxSize/2
        while True:
            right = left + boxSize
            #print(f"        try {left}, {right}")
            if right < boxRight:
                left += shiftSize
                continue
            if left > boxLeft:
                #print("        fail")
                return None
            if left <= boxLeft and right >= boxRight:
                #print(f"        [{left},{right}]")
                return [left,right]

    def passesLcf(self,aidvs):
        seed = 0
        mult = self.maxIndex
        for aidv in aidvs:
            seed += aidv * mult
            mult *= self.maxIndex
        random.seed(seed)
        thresh = random.randint(self.groupMin,self.groupMax)
        #print(thresh)
        if len(aidvs) >= thresh:
            return True
        return False

    def getGroups(self,p,points):
        '''
            Starting somewhat to the left of point p and working right, 
            create minimum-sized groups of AIDV-sets.
        '''
        self.groups = []
        leftPoint = max(p-self.groupMax,self.minIndex+self.groupMin-1)
        rightPoint = min(p+(self.groupMax*2),self.maxIndex)
        #print('--------------------------------')
        #print(p,leftPoint,rightPoint)
        for rEdge in range(leftPoint,rightPoint+1):
            # This loops through the set of AIDV-sets (groups)
            # the gEdge is the point at the right edge of the group
            # The group must have at least groupMin AIDVs
            initEdge = rEdge - self.groupMin + 1
            #print(initEdge,rEdge)
            group = None
            for extend in range(self.groupMax-self.groupMin+1):
                # This loops through increasingly larger AIDV sets in
                # search of the smallest set that passes LCF
                lEdge = initEdge - extend
                if lEdge < self.minIndex:
                    break
                aidvs = list(range(lEdge,rEdge+1))
                if self.passesLcf(aidvs):
                    group = points[lEdge:rEdge+1]
                    break
            #print(aidvs,group)
            if group:
                self.groups.append({'group':group,'aidvs':aidvs})

def makePoints(num,alpha,beta):
    points = []
    for _ in range(num):
        points.append(round(num * random.betavariate(alpha,beta)))
    points.sort()
    return points

def plotPoints(points,alpha,beta):
    fileName = f"{alpha}.{beta}.{len(points)}.png"
    plt.figure(figsize=(6, 3))
    plt.plot(points,marker='.')
    plt.savefig(fileName)

def evaluate(bx,points):
    '''
        We want to know:
          * When there is a change of box, how many persons were changed
          * When one person changes, how often does box change
    '''
    lastRes = None
    lastVal = None
    lastIndex = None
    totalTries = 0
    boxChangePersons = {}
    onePersonBoxChange = 0
    onePersonBoxSame = 0
    for i in range(len(points)-1):
        if points[i] == points[i+1]:
            continue
        totalTries += 1
        res = bx.getBox(i,points)
        if not lastRes:
            lastRes = res
            lastVal = points[i]
            lastIndex = i
            continue
        numChangedPersons = i - lastIndex
        if res['box'] != lastRes['box']:
            if numChangedPersons in boxChangePersons:
                boxChangePersons[numChangedPersons] += 1
            else:
                boxChangePersons[numChangedPersons] = 1
        if numChangedPersons == 1:
            # Only one person changed
            if res['box'] == lastRes['box']:
                onePersonBoxSame += 1
            else:
                onePersonBoxChange += 1
                print("------------------------------")
                print(f"index {lastIndex} --> {i} ({numChangedPersons}), value {lastVal} --> {points[i]}")
                print("last result")
                pp.pprint(lastRes)
                print("this result")
                pp.pprint(res)
        lastRes = res
        lastVal = points[i]
        lastIndex = i
    return {'boxChangedPersons':boxChangePersons,
            'onePersonBoxSame':onePersonBoxSame,
            'onePersonBoxChange':onePersonBoxChange,
           }

numPoints = 1000
alphBets = [[1,1],[0.5,2],[0.1,4]]
#alphBets = [[1,1]]
groupSizes = [[3,5]]
for groupMin,groupMax in groupSizes:
    for alpha,beta in alphBets:
        print(f"group min {groupMin}, max {groupMax}, alpha {alpha}, beta {beta}")
        points = makePoints(numPoints,alpha,beta)
        plotPoints(points,alpha,beta)
        params = {'groupMin':groupMin,'groupMax':groupMax,'numPoints':numPoints}
        bx = boxes(params)
        bx.printBoxSizes()
        res = evaluate(bx,points)
        print("Results:")
        pp.pprint(res)
        #evaluate(bx,list(reversed(points)))
