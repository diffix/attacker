import random
import math
import pprint
pp = pprint.PrettyPrinter(indent=4)

'''
Contains the basic classes for simulation of the "snapped boxes" approach to inequalities.
'''

# index and value
I = 0
V = 1

class edgeCompare():
    def __init__(self,val,op):
        self.val = val     # edge value
        self.op = op       # edge operation

    def print(self):
        print(f"Edge: value: {self.val}, operation: {self.op}")

    def inside(self,val):
        ''' val is inside the range defined by the edge/operation '''
        if math.isclose(self.val,val): 
            if self.op in ['<=','>=']:
                return True
            if self.op in ['<','>']:
                return False
        if val < self.val and self.op in ['<=','<']:
            return True
        if val > self.val and self.op in ['>=','>']:
            return True
        return False

    def eq(self,val):
        if math.isclose(self.val,val):
            return True
        return False

    def lt(self,val):
        ''' Edge is less than val'''
        if math.isclose(self.val,val):
            return False
        if self.val < val:
            return True
        return False

    def gt(self,val):
        ''' Edge is greater than val '''
        if math.isclose(self.val,val):
            return False
        if self.val > val:
            return True
        return False

    def lte(self,val):
        ''' Edge is less than or equal to val '''
        if math.isclose(self.val,val):
            return True
        if self.val < val:
            return True
        return False

    def gte(self,val):
        ''' Edge is greater than or equal to val '''
        if math.isclose(self.val,val):
            return True
        if self.val > val:
            return True
        return False

class snappedBox():
    def __init__(self,left,width,base=2,right=None):
        ''' Operations on a snapped box. If called with left and right
            specified, then it means that we need to find a snapped
            box that encompasses left and right inclusive.
        '''
        self.base = base
        if right is not None:
            self.getEncompassingBox(left,right)
            if self.width == 0:
                pass
        else:
            self.left = left
            self.width = width
            self.right = left + width

    def getNoise(self,hv=None):
        ''' One noise layer is based purely on the box parameters
            IMPORTANT: Note the rounding here. This is because machine representation
                differences cause the seed to be different for otherwise "identical"
                boxes. The specific mechanism here (precision of 8) will fail if the
                boxes are incredibly tiny. (Probably not an issue in practice.)
            Additional noise layers are based on the visible points
        '''
        seed = str(round(self.left,8)) + str(round(self.width,8))
        random.seed(seed)
        noiseBox = round(random.gauss(0,1.5))
        return noiseBox

    def getEncompassingBox(self,low,high):
        ''' Gets box encompassing the low-high range.
            Note that this is only called with respect to the set of points above
            and below the edge. We don't care here what the operation is, because in
            any event we have grabbed more points than necessary.
        '''
        if low == high:
            self.left = low
            self.right = high
            self.width = 0
            return
        width = high-low
        #print(f"width {width}, base {self.base}")
        logged = math.log(width, self.base)
        #print(f"logged {logged}")
        if logged >= 0:
            if math.isclose(logged,int(logged)):
                # case when width is snapped
                flooredLog = int(logged)
            else:
                flooredLog = int(logged+1)
            self.width = self.base**flooredLog
        else:
            flooredLog = int(abs(logged))
            self.width = self.base**(-flooredLog)
        while True:
            #print(f"flooredLog {flooredLog}, snappedWidth {self.width}")
            self.left = low - (low%self.width)
            #print(f"snappedLeft {self.left}")
            if self.left <= low and (self.left+self.width) >= high:
                self.right = self.left + self.width
                return
            # At this point, self.left is a non-shifted boundary. We want to test
            # if the corresponding left- and right-shifted box will work
            # Shift left
            newLeft = self.left - (self.width/2)
            if newLeft <= low and (newLeft+self.width) >= high:
                self.left = newLeft
                self.right = self.left + self.width
                return
            # ... and shift right
            newLeft = self.left + (self.width/2)
            if newLeft <= low and (newLeft+self.width) >= high:
                self.left = newLeft
                self.right = self.left + self.width
                return
            self.width *= self.base

    def midpoint(self):
        return self.left + ((self.right - self.left) / 2)

    def valIsInBox(self,val):
        ''' I don't believe we need to take the edge's operation into account
            here. The reason is that we want a given edge to generate the same
            box consistently so that when we have a histogram, we'll be able to
            ensure that all points are included in one and only one bucket.
        '''
        if val >= self.left and val <= self.right:
            return True
        return False

    def getSmallerBox(self,edge):
        newWidth = self.width/self.base
        snappedLeft = edge.val - (edge.val%newWidth)
        return snappedBox(snappedLeft,newWidth,base=self.base)

    def getLeftShifted(self):
        snappedLeft = self.left - (self.width/2)
        return snappedBox(snappedLeft,self.width,base=self.base)

    def getRightShifted(self):
        snappedLeft = self.left + (self.width/2)
        return snappedBox(snappedLeft,self.width,base=self.base)

    def boxesAreEqual(self,sb):
        if math.isclose(sb.left,self.left) and math.isclose(sb.width,self.width):
            return True
        return False

    def print(self):
        print(f"snappedBox: left {self.left}, right {self.right}, width {self.width}, base {self.base}")


class boxes():
    def __init__(self,base=2,groupMin=2,groupMax=6,suppressMin=2,suppressMax=6):
        self.base = base
        # Group min and max are the inclusive bounds on suppression (meaning that
        # anything matching or within these bounds may or may not be suppressed)
        self.groupMin = groupMin
        self.groupMax = groupMax
        self.suppressMin = suppressMin
        self.suppressMax = suppressMax
        # The following is just an optimization
        self.adjHint = 0
        self.useHint = False
        pass

    def print(self):
        print(f"boxes: base {self.base}, group min/max {self.groupMin},{self.groupMax}")

    def findAdjacentPoints(self,edge,points):
        ''' Finds groupMax*2 points above and below edge. Just brute force.
            The *2 is to get enough values so that we can recognize when a value
            has by itself >LCF AIDVs (so we know to include or exclude when we finally
            generate data values for output)
        '''
        reach = self.groupMax * 2
        start = 0
        if self.useHint:
            self.adjHint = max(0,self.adjHint)
            start = self.adjHint
            if points[start][V] > edge.val:
                start = 0
        leftPoints = []
        rightPoints = []
        leftIndex = None
        # Corner cases where edge is to the left or right of all points
        if (  (edge.op in ['<','>='] and edge.lte(points[0][V])) or
              (edge.op in ['<=','>'] and edge.lt(points[0][V])) ):
            # This is the case where there are no values that would be included on
            # the left side of the edge
            rightPoints = points[:reach]
            self.adjHint = 0
            return {'i':-1,'left':leftPoints,'right':rightPoints,
                    'min':rightPoints[0][V],'max':rightPoints[-1][V]}
        if (  (edge.op in ['<=','>'] and edge.gte(points[-1][V])) or
              (edge.op in ['<','>='] and edge.gt(points[-1][V])) ):
            # This is the case where there are no values that would be included on
            # the right side of the edge
            leftPoints = points[-reach:]
            self.adjHint = len(points)-1
            return {'i':len(points)-1,'left':leftPoints,'right':rightPoints,
                    'min':leftPoints[0][V],'max':leftPoints[-1][V]}
        for i in range(start,len(points)-1):
            if ((not edge.inside(points[i][V]) and edge.inside(points[i+1][V])) or
                (edge.inside(points[i][V]) and not edge.inside(points[i+1][V]))):
                # The first expression captures the case where the left point (i) is
                # not inside but the right point is, and the second expression is
                # vice versa. Either way, the two points are on opposite sides of the edge.
                # Note that we don't get here if points[i] == points[i+1]
                # This is in order to make sure we include all identical
                # points on the left
                leftIndex = i
                rightIndex = i+1
                break
        leftStart = max(0,leftIndex-reach)
        leftPoints = points[leftStart:leftIndex+1]
        rightEnd = min(len(points),rightIndex+reach)
        rightPoints = points[rightIndex:rightEnd]
        self.adjHint = i
        return {'i':i,'left':leftPoints,'right':rightPoints,
                'min':leftPoints[0][V],'max':rightPoints[-1][V]}

    def getMatchingValues(self,edge,sb,points):
        ''' This returns two lists. The first is the list of matching values based on
            the box threshold, and the second is the true list. The latter is just
            for performance measurements.
        '''
        p = False
        if p: print(f"getMatchingValues:")
        if p: edge.print()
        if p: sb.print()
        # Let's count the number of distinct non-suppressed values
        nonSuppVals = {}
        valsOnLeft = 0
        valsOnRight = 0
        boxed = []
        true = []
        perValueAidvs = {}
        for point in points:
            # First take care of the true comparison operation
            if edge.inside(point[V]):
                true.append(point)
            # Now take care of the box-based comparison operation
            if not sb.valIsInBox(point[V]):
                # If the point is outside of the box, then we can simply use the edge itself
                # as the threshold
                if edge.inside(point[V]):
                    boxed.append(point)
            else:
                # The point is inside of the box, so the computation gets a little more complex
                # For now, just record the AIDVs associated with each point inside the box
                if point[V] in perValueAidvs:
                    perValueAidvs[point[V]].append(point[I])
                else:
                    perValueAidvs[point[V]] = [point[I]]
        if p: pp.pprint(perValueAidvs)
        # Create an edge from the midpoint. We use this for suppressed values.
        if edge.op in ['<=','<']:
            edgeMid = edgeCompare(sb.midpoint(),'<')
        else:
            edgeMid =  edgeCompare(sb.midpoint(),'>=')
        if p: edgeMid.print()
        for val in perValueAidvs.keys():
            if self.pointIsNotSuppressed(perValueAidvs[val]):
                # The value is a non-suppressed value. Use the edge itself to determine
                # if the value is in or out
                if p: print(f"    val {val} is not suppressed")
                if edge.inside(val):
                    if p: print(f"   add {val} to boxed")
                    for aidv in perValueAidvs[val]:
                        boxed.append([aidv,val])
            else:
                # The value is suppressed, so use the midpoint
                if val not in nonSuppVals:
                    nonSuppVals[val] = 1
                    if val < edgeMid.val:
                        valsOnLeft += 1
                    if val > edgeMid.val:
                        valsOnRight += 1
                if p: print(f"    val {val} is suppressed")
                if edgeMid.inside(val):
                    if p: print(f"   add {val} to boxed")
                    for aidv in perValueAidvs[val]:
                        boxed.append([aidv,val])
        # let's sort boxed
        bothSides = 0
        if valsOnLeft and valsOnRight:
            bothSides = 5
        boxed.sort(key=lambda tup: tup[V])
        return boxed,true,bothSides

    def getBox(self,edge,points):
        '''
            Goal is to find the smallest non-suppressed box that includes
            the point to the left of the edge. Points is ordered. Note that
            the edge operation ('<', '>', etc.) does not matter here.
            As a side-effect, getBox() also detects when there is a non-suppressed
            point inside the box.
        '''
        p = False
        # A box that encompases outer will definately not be LCF
        # outer['i'] is the index of the rightmost included (left) point
        # outer['min'] and outer['max'] are the edges of outer
        outer = self.findAdjacentPoints(edge,points)
        if p: print('------ getBox -------')
        if p: edge.print()
        if p: pp.pprint(outer)
        # make the snapped box that encompasses outer
        sb = snappedBox(outer['min'],None,base=self.base,right=outer['max'])
        if p: sb.print()
        if sb.width == 0:
            # The box is a single point, so no need to search for smaller box
            return sb
        # sbNonSupp is the candidate best snapped box.
        sbNonSupp = sb
        outerAll = outer['left']+outer['right']
        aidvs,values = self.getAidvsFromPoints(sbNonSupp, outerAll)
        if p: print(aidvs)
        if p: print(values)
        if not self.boxIsBigEnough(aidvs):
            print(f"ERROR: This should never happen!")
            print(f"Edge: {edge}")
            pp.pprint(outer)
            sbNonSupp.print()
            quit()
        # Note that edge could be very far to the left or right of all points.
        # Because of the way we find
        # smaller boxes (requiring that the edge be within the smallest box),
        # this could lead to a larger box than necessary. So here we artifically
        # adjust the edge to be only slightly to the left of the lowest point
        # (The constant 50 here is arbitrary. 2 or 1000 could just as well work.)
        if len(outer['left']) == 0:
            edge.val = outer['right'][0][V] - (sbNonSupp.width / 50)
        elif len(outer['right']) == 0:
            edge.val = outer['left'][-1][V] + (sbNonSupp.width / 50)
        if p: sbNonSupp.print()
        # Find the largest suppressed box
        while True:
            sbSupp = sbNonSupp.getSmallerBox(edge)
            if p: sbSupp.print()
            aidvs,values = self.getAidvsFromPoints(sbSupp, outerAll)
            if p: print(aidvs)
            if p: print(values)
            if not self.boxIsBigEnough(aidvs):
                # Ok, found the suppressed box
                if p: print("    found suppressed box")
                break
            sbNonSupp = sbSupp
            sbZero = self.zeroWidthBox(values,edge)
            if sbZero:
                # Box is not suppressed, but the width is zero (because all values in
                # the box are the same). This only happens when the edge is identical
                # to the non-suppressed point
                if p: print("    found zero width box")
                return sbZero
            # The smaller box is not suppressed, so keep digging
            continue
        '''
            At this point there are three possibilities.
            First, the suppressed box sbSupp might be non-suppressed if shifted. If
            so, we want to use this (cause smallest width).
            Second, we use sbNonSupp (non-shifted box, so less distortion)
            Third, sbNonSupp shifted right or left is a better choice because it puts
            the edge closer to the midpoint (less distortion).
        '''
        # First determine if we can used the shifted suppressed box sbSupp
        sbShiftLeft = sbSupp.getLeftShifted()
        aidvs,values = self.getAidvsFromPoints(sbShiftLeft, outerAll)
        if p: print(aidvs)
        if p: print(values)
        if self.boxIsBigEnough(aidvs) and sbShiftLeft.valIsInBox(edge.val):
            if p: print("    Use left shifted suppressed")
            if p: sbShiftLeft.print()
            return sbShiftLeft
        sbShiftRight = sbSupp.getRightShifted()
        aidvs,values = self.getAidvsFromPoints(sbShiftRight, outerAll)
        if p: print(aidvs)
        if p: print(values)
        if self.boxIsBigEnough(aidvs) and sbShiftRight.valIsInBox(edge.val):
            if p: print("    Use right shifted suppressed")
            if p: sbShiftRight.print()
            return sbShiftRight
        # Couldn't, so try shifting the non-suppressed box
        distanceToMidpoint = abs(edge.val - sbNonSupp.midpoint())
        if p: print(f"   distance to mid {distanceToMidpoint}")
        sbShiftLeft = sbNonSupp.getLeftShifted()
        aidvs,values = self.getAidvsFromPoints(sbShiftLeft, outerAll)
        if p: print(aidvs)
        if p: print(values)
        if self.boxIsBigEnough(aidvs) and sbShiftLeft.valIsInBox(edge.val):
            newDistance = abs(edge.val - sbShiftLeft.midpoint())
            if p: print(f"    New distance (left shift) {newDistance}")
            if newDistance < distanceToMidpoint:
                if p: print("    Use left shifted non-suppressed")
                if p: sbShiftLeft.print()
                return sbShiftLeft
        sbShiftRight = sbNonSupp.getRightShifted()
        aidvs,values = self.getAidvsFromPoints(sbShiftRight, outerAll)
        if p: print(aidvs)
        if p: print(values)
        if self.boxIsBigEnough(aidvs) and sbShiftRight.valIsInBox(edge.val):
            newDistance = abs(edge.val - sbShiftRight.midpoint())
            if p: print(f"    New distance (right shift) {newDistance}")
            if newDistance < distanceToMidpoint:
                if p: print("    Use right shifted non-suppressed")
                if p: sbShiftRight.print()
                return sbShiftRight
        if p: print("    Use non-shifted non-suppressed")
        if p: sbNonSupp.print()
        return sbNonSupp

    def getAidvsFromPoints(self,sb,points):
        ''' Here we don't need to be too careful about edges in or out, because this
            is only for the purpose of LCF, which is somewhat random anyway.
        '''
        aidvs = []
        values = []
        for point in points:
            if point[V] >= sb.left and point[V] <= sb.right:
                aidvs.append(point[I])
                values.append(point[V])
        return aidvs,values
    
    def zeroWidthBox(self,values,edge):
        p = False
        value = values[0]
        if p: print(f"    compare point {value} with edge {edge.val}")
        if not math.isclose(value,edge.val):
            if p: print(f"    exit 1")
            return False
        for i in range(len(values)):
            val = values[i]
            if p: print(f"        compare point {value} with {val}")
            if value != val:
                if p: print(f"    exit 2")
                return False
        sb = snappedBox(value,0)
        sb.nonSuppressedEdge = edgeCompare(value,edge.op)
        return sb

    def boxIsBigEnough(self,aidvs):
        return self.lcfWork(aidvs,self.groupMin,self.groupMax)

    def pointIsNotSuppressed(self,aidvs):
        return self.lcfWork(aidvs,self.suppressMin,self.suppressMax)

    def lcfWork(self,aidvs,threshMin,threshMax):
        if len(aidvs) > threshMax:
            return True
        if len(aidvs) < threshMin:
            return False
        # Following is a poor man's hash of AIDVs
        seed = 0
        mult = 11311
        for aidv in aidvs:
            seed += aidv * mult
            mult += mult
        random.seed(seed)
        thresh = random.randint(threshMin,threshMax)
        #print(f"threshold = {thresh}")
        if len(aidvs) >= thresh:
            return True
        return False

class getHiddenAndVisible():
    def __init__(self,bx,points):
        self.numHidden = 0
        self.numVisible = 0
        self.hidVis = {}
        self.hiddenVals = []
        self.visibleVals = []
        self.aidvs = {}
        self.makeHidVis(bx,points)

    def valsLoop(self):
        for val in self.hidVis.keys():
            yield val

    def getAidvs(self,val):
        if val in self.aidvs:
            return self.aidvs[val]
        return []

    def pointExists(self,val):
        if val in self.hidVis:
            return True
        return False

    def pointIsVisible(self,val):
        if not self.pointExists(val):
            return False
        if self.hidVis[val] == 'visible':
            return True
        return False

    def pointIsHidden(self,val):
        if not self.pointExists(val):
            return False
        if self.hidVis[val] == 'hidden':
            return True
        return False

    def makeHidVis(self,bx,points):
        self.aidvs = {}
        # First get the AIDVs per point
        for point in points:
            if point[V] in self.aidvs:
                self.aidvs[point[V]].append(point[I])
            else:
                self.aidvs[point[V]] = [point[I]]
        self.hidVis = {}
        # Then for each one, decide if hidden or visable
        for val,aidvs in self.aidvs.items():
            if bx.pointIsNotSuppressed(aidvs):
                self.numVisible += 1
                self.visibleVals.append(val)
                state = 'visible'
            else:
                self.numHidden += 1
                self.hiddenVals.append(val)
                state = 'hidden'
            self.hidVis[val] = state
        self.hiddenVals.sort()
        self.visibleVals.sort()

class multiInequalities():
    def __init__(self,mPointsCols,mEdges,bx):
        ''' mPointsCol is a list of points constructs, where a points construct is a list
            of [[id],[val]] tuples, ordered by [val]. Each mPointsCol entry represents a
            different column. The points entries may have a different set of IDs.
            mEdges is a list of per-column edges, indexed by column. 
            groupMax is the number of AIDVs beyond the edge that we want to include.
            mpointsAidv is indexed by the row AIDV. It keeps track of which points are
            included or excluded.
            mPoints is the resulting list of points construts, containing only those points
            that are included by all other lists (plus the additional groupMax of course)
        '''
        self.bx = bx
        self.groupMax = bx.groupMax
        self.mEdges = mEdges
        self.mPointsCols = mPointsCols
        self.hvs = self.makeHiddenAndVisible()
        self.startIndices = [-1 for _ in range(len(mEdges))]
        self.ordermPoints()
        self.mPointsAidv = self.initmPointsAidv()
        # number of columns
        self.mPoints = [[] for _ in range(len(mEdges))]
        self.buildmPointsAidv()
        pass

    def makeHiddenAndVisible(self):
        hvs = []
        for points in self.mPointsCols:
            hvs.append(getHiddenAndVisible(self.bx,points))
        return hvs

    def initmPointsAidv(self):
        mPointsAidv = {}
        # This loop initializes mPointsCols
        for col in range(len(self.mPointsCols)):
            for aidv,_ in self.mPointsCols[col]:
                if aidv not in mPointsAidv:
                    mPointsAidv[aidv] = {'in':[False for _ in range(len(self.mPointsCols))],
                                         'val':[0 for _ in range(len(self.mPointsCols))], }
        # This loop sets the 'val' values in mPointsCols
        for col in range(len(self.mPointsCols)):
            for aidv,val in self.mPointsCols[col]:
                mPointsAidv[aidv]['val'][col] = val
        for col in range(len(self.mPointsCols)):
            # This loop establishes the start index for the column.
            # Note that if edge op is > or >=, these are in reverse order by val (big to small)
            # The start index is set to the first value that is not inside the edge
            edge = self.mEdges[col]
            for i in range(len(self.mPointsCols[col])):
                aidv = self.mPointsCols[col][i][I]
                val = self.mPointsCols[col][i][V]
                if edge.inside(val):
                    mPointsAidv[aidv]['in'][col] = True
                else:
                    self.startIndices[col] = i
                    break
            ''' In this loop, we want to assign groupMax AIDVs worth of points to be included.
                However, we don't want to include visible points, because in any event those
                will be excluded.
            '''
            '''
                Ok, will come back to this later. Whole thing is tricky, and needs to be worked
                out with respect to other forms of flipping (i.e. LED). But some basic thoughts
                here.
                In one round, we can tag rows as 'in' if they are inside the edge. Other rows
                are a kind of "maybe" (or could be given an index number indicating distance
                from edge)
                In another round, we find additional 'in' rows working from the edge outwards,
                where a row is made in if it is 'maybe' for the column, and 'in' for all other
                columns.
                This establishes groupMax additional 'in' rows per column, and also establishes
                a 'max index' (the 'in' row with the highest index) per column.
                In another round, we can find rows that are 'maybe' for one or more columns, but
                the index is below the max index for all columns. These can be made 'in'. (Leads
                to more than groupMax 'in' rows, but that's ok.)
                Then we can do the actual boxing, which we only need to do among the 'in' rows.
                This boxing determines what is included or excluded, but we need to take care
                about cases where one inequality excludes a row, where another includes it...

            '''
            numAidvs = 0
            for i in range(self.startIndices[col],len(self.mPointsCols[col])):
                if numAidvs >= self.groupMax:
                    break
                val = self.mPointsCols[col][i][V]
                if self.hvs[col].pointIsVisible(val):
                    continue
                for aidv in self.hvs[col].getAidvs(val):
                    numAidvs += 1
                    mPointsAidv[aidv]['in'][col] = True
        # At this point, if mPointsAidv is False for the given column, then it is
        # definately excluded. It might be that we included some points that are definitely
        # excluded, so now we loop through and re-assign the extra points among only those
        # that might be included
        self.aidvIsExcluded = {}
        for aidv,thing in mPointsAidv.items():
            if False in thing['in']:
                self.aidvIsExcluded[aidv] = True
        return mPointsAidv

    def ordermPoints(self):
        ''' Just reorder the points where edge is > or >= so that we can always pretend
            that the operation is <=.
        '''
        for points,edge in zip(self.mPointsCols,self.mEdges):
            if edge.op in ['>','>=']:
                points.reverse()

    def buildmPointsAidv(self):
        for aidv,thing in self.mPointsAidv.items():
            print(aidv,thing)
            if aidv in self.aidvIsExcluded:
                continue
            for col in range(len(self.mPointsCols)):
                if thing['in'][col] == True:
                    val = thing['val'][col]
                    self.mPoints[col].append([aidv,val])
        for points in self.mPoints:
            points.sort(key=lambda tup: tup[V])