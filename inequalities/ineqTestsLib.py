import random
import matplotlib.pyplot as plt
import pprint
pp = pprint.PrettyPrinter(indent=4)

# index and value
I = 0
V = 1

def makePointsCluster(num,cluster):
    vals = []
    prob = 1000/cluster
    val = 0
    for _ in range(num):
        vals.append(val)
        if random.randint(0,1000) < prob:
            val += random.randint(1,20)
    return vals

def shuffleAidvs(points):
    aidvs,vals = zip(*points)
    aidvs = list(aidvs)
    random.shuffle(aidvs)
    return(list(zip(aidvs,vals)))

def reverseAidvs(points):
    aidvs,vals = zip(*points)
    aidvs = list(aidvs)
    aidvs.reverse()
    return(list(zip(aidvs,vals)))

def plotPoints(points,cluster):
    fileName = f"{cluster}.{len(points)}.png"
    plt.figure(figsize=(6, 3))
    plt.plot(points,marker='.')
    plt.savefig(fileName)

def makePointsFromVals(vals):
    points = []
    for point in zip(range(len(vals)), vals):
        points.append(point)
    points.sort(key=lambda tup: tup[V])
    return points

def getNameFromParams(params):
    fileName = ''
    for _,value in params.items():
        fileName += str(value) + '.'
    return fileName

class rememberBoxes():
    def __init__(self):
        self.boxes = {}

    def addBox(self,sb):
        key = f"{round(sb.left,5)}.{round(sb.width,5)}"
        if key not in self.boxes:
            self.boxes[key] = 1

    def numBoxes(self):
        return len(self.boxes)
