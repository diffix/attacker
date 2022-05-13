import math
import pprint
pp = pprint.PrettyPrinter(indent=4)

class snappedBox():
    ''' This class manipulates a given snapped box (shifts left, right, etc.) '''
    def __init__(self,snappingObject,snappedWidthObject,left,right):
        self.sn = snappingObject
        self.sw = snappedWidthObject
        self.left = left
        self.right = right
        self.width = self.right - self.left
        self.shift = None
        self.numShifts = None
        self.setShift()
        pass

    def print(self):
        self.sw.print()
        print(f"box left {round(self.left,4)}, right {round(self.right,4)}, width {round(self.width,4)}, shift {self.shift}, numShifts {self.numShifts}")

    def shiftRight(self):
        self.left += self.shift
        self.right += self.shift

    def setShift(self):
        ''' This sets self.shift, which is the amount that this box is shifted
            It is set so that an integer number of shifts matches a decade perfectly
        '''
        # boxWidShift is what the shifting would be if we didn't need to slot
        # perfectly into the decade
        boxWidShift = self.width / self.sn.params['shifts']
        # nonIntDecadeShifts is the fractional number of shifts that would be needed
        # that would be needed to make a shift that slots into the decade
        nonIntDecadeShifts = self.sw.decadeWid / boxWidShift
        # self.numShifts is the integral number of shifts
        self.numShifts = int(round(nonIntDecadeShifts))
        # self.shift is the shift size
        self.shift = self.sw.decadeWid / 13

class snappedWidth():
    ''' This class manipulates a given snapped width (finds edges, etc.) '''
    def __init__(self,snappingObject,wid):
        self.sn = snappingObject
        self.width = wid
        self.decadeWid = None
        self.roundPrecision = None
        self.setLargerDecade()
        pass

    def print(self):
        self.sn.print()
        print(f"Width: {round(self.width,4)}, decade {self.decadeWid}")

    def setLargerDecade(self):
        ''' Sets self.decadeWid to power of 10 width greater than self.wid, unless
            self.wid is a power of 10 (in which case self.decadeWid == self.wid).
            Also sets self.roundPrecision, which is the constant that can be used in
            the round() function to return the nearest decade.
        '''
        logged = math.log10(self.width)
        if logged >= 0:
            if math.isclose(logged,int(logged)):
                # case when width is a decade
                flooredLog = int(logged)
            else:
                flooredLog = int(logged+1)
            self.decadeWid = 10**flooredLog
            self.roundPrecision = -flooredLog
        else:
            flooredLog = int(abs(logged))
            self.decadeWid = 10**(-flooredLog)
            self.roundPrecision = flooredLog

    def getDecadeFloor(self,left):
        ''' Returns snapped box of width self.wid, aligned to the decade
            to the left of the left edge.
            (I would think there is some kind of python function that does this,
             but don't find it off hand...)
        '''
        remain = left % self.decadeWid
        return left - remain

    def getLeftmostBox(self,left):
        ''' Gets the snapped box to the right of the left edge, but as close as possible
        '''
        decadeFloor = self.getDecadeFloor(left)
        sb = snappedBox(self.sn,self,decadeFloor,decadeFloor+self.width)
        # Start walking right until we are past the left point
        while True:
            print(f"----- left {left}, sb.left {sb.left}")
            if sb.left < left:
                sb.shiftRight()
                continue
            return sb

class snapping():
    def __init__(self,params):
        self.params = params
        self.lowerEqual = 0.9999
        self.upperEqual = 1.0001
        self.shifts = params['shifts']
        # Following set by computeBase
        self.mult = None
        self.steps = None
        self.computeBase()

    def print(self):
        print(f"Snapping: {self.params}, mult {round(self.mult,4)}")
        ps = [round(v,4) for v in self.steps]
        print(f"    steps {ps}")

    def getEnclosedSnappedBox(self,left,right):
        ''' Finds the largest snapped box within the box defined by left,right
        '''
        sw,alreadySnapped = self.getSmallerSnappedWidth(right-left)
        while True:
            sb = sw.getLeftmostBox(left)
            if sb.left >= left and sb.right <= right:
                return sb
            # zzzz get next smaller snapped width...
        pass

    def widthIsSnapped(self,width):
        _, wasAlreadySnapped = self.getSmallerSnappedWidth(width)
        return wasAlreadySnapped

    def getLowerDecade(self,val):
        logged = math.log10(val)
        if logged >= 0:
            flooredLog = int(logged)
            base = 10**flooredLog
        else:
            flooredLog = int(abs(logged)+1)
            if math.isclose(abs(logged)+1,int(abs(logged)+1)):
                # captures corner case where val is already at decade
                flooredLog -= 1
            base = 10**(-flooredLog)
            #print(f"logged: {logged}, floor: {flooredLog}, base: {base}")
        return base

    def getSmallerSnappedWidth(self,width):
        ''' If width is already snapped, then returns same value
            Also returns an indication as to whether width was snapped or not
        '''
        if width <= 0:
            return None
        base = self.getLowerDecade(width)
        # base is the "decade" below the given width
        # base for 123 = 100, base for 0.0123 = 0.01
        # Now we just walk through the step multipliers to find the snapped
        # width just lower than the given width
        for i in range(len(self.steps)-1):
            #print(f"{i}, {self.steps[i]}, {base*self.steps[i]} ({width})")
            if (self.steps[i] * base) <= width and (self.steps[i+1] * base) > width:
                sw = snappedWidth(self, self.steps[i] * base)
                lower = sw.width * self.lowerEqual
                upper = sw.width * self.upperEqual
                wasAlreadySnapped = False
                if width >= lower and width <= upper:
                    wasAlreadySnapped = True
                return sw, wasAlreadySnapped
        # Should never reach this line of code
        return None

    def computeBase(self):
        ''' This makes self.steps, which is a list of multiplier values to
            produce the snapped widths for a given decade (1-10, 10-100, etc.)
            It also computes self.mult, the multiplication factor for each step.
        '''
        steps = self.params['steps']
        start = 10
        finish = 100
        left = 0
        right = 10
        mult = 5
        while True:
            result = self.doTest(mult,steps,start,finish)
            if result == 'good':
                break
            if result == 'low':
                # Need to increase multiplier
                left = mult
                mult = mult + ((right - mult) / 2)
            else:
                # Need to shrink multipler
                right = mult
                mult = mult - ((mult-left)/2)
        self.mult = mult
        self.steps = [1.0]
        next = 1.0
        for _ in range(steps-1):
            next *= mult
            self.steps.append(next)
        # This to simplify some loops later on
        self.steps.append(10.0)

    def doTest(self,mult,steps,start,finish):
        for _ in range(steps):
            start *= mult
        if abs(start - finish) < 0.001:
            return 'good'
        elif start < finish:
            return 'low'
        return 'high'

def testGetSmaller(sn,widths):
    for width in widths:
        print(f"Try width {width[0]}")
        sw, wasAlreadySnapped = sn.getSmallerSnappedWidth(width[0])
        if round(sw.width,4) != width[1]:
            print(f"Bad snapped width {round(sw.width,4)} for width {width[0]}.")
            print(f"    Should be {width[1]}")
            quit()
        if width[0] == width[1] and not wasAlreadySnapped:
            print(f"Width should be snapped {width[0]} and {width[1]}.")
            quit()
        if width[0] != width[1] and wasAlreadySnapped:
            print(f"Width should not be snapped {width[0]} and {width[1]}.")
            quit()
        print("    passed")

def testLargerDecade(test):
    sw, wasAlreadySnapped = sn.getSmallerSnappedWidth(test[0])
    print(f"snapped width for {test[0]} is {sw.width}")
    print(f"    larger decade is {sw.decadeWid}")
    if test[1] != sw.decadeWid:
        print(f"FAIL testLargerDecade: {test}, {sw.decadeWid}")
        quit()

def testDecadeFloor(sw,test):
    decFloor = sw.getDecadeFloor(test[0])
    print(f"Decade floor for {test[0]} with decade {sw.decadeWid} is {decFloor}")
    if decFloor != test[1]:
        print(f"    FAIL, should have gotten {test[1]}")
        quit()

if __name__ == "__main__":
    params = {'steps':3,'shifts':4}
    sn = snapping(params)
    widths = [ [1,1.0],[1.0,1.0],[1.1,1.0],[2.3,2.1544],
               [0.123,0.1],[0.713,0.4642],[0.1,0.1],
             ]
    testGetSmaller(sn,widths)
    print(sn.steps)
    params = {'steps':6,'shifts':4}
    sn = snapping(params)
    print(sn.steps)
    widths = [ [1,1.0],[1.0,1.0],[1.1,1.0],[2.3,2.1544],
               [0.123,0.1],[0.713,0.6813],[0.1,0.1],
             ]
    testGetSmaller(sn,widths)

    for wid in [[21,100],[923,1000],[100,100],[1,1],[1.1,1], [2.1,10],
                [0.21,1],[0.923,1],[0.1,0.1],[0.01,0.01],[0.011,0.01]
               ]:
        testLargerDecade(wid)

    sw, wasAlreadySnapped = sn.getSmallerSnappedWidth(21)
    print(f"snapped width for 21 is {sw.width}")
    print(f"    larger decade is {sw.decadeWid}")
    for test in [ [142,100],[821.535,800],[1.1,0],
                  [0,0],[100,100],[100.0,100],
                  [-5,-100],[-153.22,-200]
                ]:
        testDecadeFloor(sw, test)

    print('-----')
    sb = sn.getEnclosedSnappedBox(24,61)
    print(f"Range: 24,61")
    sb.print()

    print('-----')
    sb = sn.getEnclosedSnappedBox(0.5882,0.71)
    print(f"Range: 0.5882,0.71 ({0.71-0.5882})")
    sb.print()