import ineqTestsLib
import inequalities
import random
import pprint

''' Runs basic correctness checks. Will halt with error message if anything
    is wrong.
'''

def test_getBox(bx,test,vals,points):
    print("--------")
    print(f"test_getBox {test}")
    random.seed(1)
    sb = bx.getBox(inequalities.edgeCompare(test[1],test[0]),points)
    print("Use this box:")
    sb.print()
    if sb.left != test[2] or sb.width != test[3]:
        print(f"FAIL: {test}")
        print(vals)
        quit()

def test_getMatchingValues(bx,test,vals,points):
    print("--------")
    print(f"test_getMatchingValues {test}")
    I = 0
    random.seed(1)
    edge = inequalities.edgeCompare(test[1],test[0])
    sb = bx.getBox(edge,points)
    boxed,true,_ = bx.getMatchingValues(edge,sb,points)
    boxmm = [None,None]
    trmm = [None,None]
    if len(boxed) > 0: boxmm[0] = boxed[0][I]
    if len(boxed) > 1: boxmm[1] = boxed[-1][I]
    if len(true) > 0: trmm[0] = true[0][I]
    if len(true) > 1: trmm[1] = true[-1][I]
    print("Use this box:")
    sb.print()
    print(f"boxed {boxmm}, {boxed}")
    print(f"true {trmm}, {true}")
    if boxmm != test[2] or trmm != test[3]:
        print(f"FAIL: {test}")
        print(vals)
        print(points)
        quit()

def test_findAdjacentPoints(bx,points,test):
    edge = inequalities.edgeCompare(test[1],test[0])
    print('-----------------------------')
    print(f"Try test = {test}")
    outer = bx.findAdjacentPoints(edge,points)
    if (   (test[2] is None and len(outer['left']) > 0) or
           (test[3] is None and len(outer['right']) > 0) or
           (test[2] is not None and len(outer['left']) == 0) or
           (test[3] is not None and len(outer['right']) == 0) or
           (len(outer['left']) and test[2] != outer['left'][-1]) or
           (len(outer['right']) and test[3] != outer['right'][0])   ):
        print("FAIL")
        pp.pprint(outer)
        quit()

def test_getEncompassingBox(bx,test):
    print('--------------------')
    print(f"test_getEncompassingBox (base {bx.base}) {test}")
    sb = inequalities.snappedBox(test[0][0],None,base=bx.base,right=test[0][1])
    sb.print()
    if sb.left != test[1][0] or sb.width != test[1][1]:
        print(f"FAIL: ")
        quit()

def runChecks():
    bx = inequalities.boxes()
    vals = [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
              3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,
              30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,
    ]
    points = ineqTestsLib.makePointsFromVals(vals)
    # [operation, edgeVal, rightmost left side, leftmost right side]
    tests = [
        ['<=',0,None,(0,2)], ['<',0,None,(0,2)], ['>',0,None,(0,2)], ['>=',0,None,(0,2)],
        ['<=',100,(58,30),None], ['<',100,(58,30),None], ['>',100,(58,30),None], ['>=',100,(58,30),None],
        ['<=',2,(16,2),(17,3)], ['<',2,None,(0,2)], ['>',2,(16,2),(17,3)], ['>=',2,None,(0,2)],
        ['<=',30,(58,30),None], ['<',30,(39,25),(40,30)], ['>',30,(58,30),None], ['>=',30,(39,25),(40,30)],
        ['<=',14.5,(28,14),(29,15)], ['<',14.5,(28,14),(29,15)], ['>',14.5,(28,14),(29,15)], ['>=',14.5,(28,14),(29,15)],
        ['<=',14,(28,14),(29,15)], ['<',14,(27,13),(28,14)], ['>',14,(28,14),(29,15)], ['>=',14,(27,13),(28,14)],
    ]
    for test in tests:
        test_findAdjacentPoints(bx,points,test)
    vals = [2,2,
              3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,
              30,30,
    ]
    points = ineqTestsLib.makePointsFromVals(vals)
    # [operation, edge, rightmost left side, leftmost right side]
    tests = [
        ['<=',2,(1,2),(2,3)], ['<',2,None,(0,2)], ['>',2,(1,2),(2,3)], ['>=',2,None,(0,2)],
        ['<=',30,(26,30),None], ['<',30,(24,25),(25,30)], ['>',30,(26,30),None], ['>=',30,(24,25),(25,30)],
    ]
    for test in tests:
        test_findAdjacentPoints(bx,points,test)

    bx = inequalities.boxes(base=10)
    # [[leftedge,rightedge],[leftboxedge,rightboxedge]]
    tests = [
        [[28,28],[28,0]],
        [[9.9,10.1],[9.5,1]],
        [[99.9,100.1],[99.5,1]],
        [[28,42],[0,100]],
        [[162.4,221.9],[150,100]],
        [[0.28,0.42],[0,1]],
        [[0.28,1.42],[0,10]],
    ]
    for test in tests:
        test_getEncompassingBox(bx,test)

    bx = inequalities.boxes(base=2)
    tests = [
        [[28,28],[28,0]],
        # Note that the following is not the smallest possible box. (We don't try
        # to find the smallest possible ... shrinking comes later)
        [[28,42],[16,32]],
        [[162.4,221.9],[160,64]],
        [[0.28,0.42],[0.25,0.25]],
        [[0.28,1.42],[0,2]],
        [[1,1],[1,0]],
    ]
    for test in tests:
        test_getEncompassingBox(bx,test)

    print('=======================================================')
    print('=======================================================')
    vals = [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
              3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,
              30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,
    ]
    print(vals)
    points = ineqTestsLib.makePointsFromVals(vals)
    # These tests are all [operation,edge,boxLeft,boxWidth]
    tests = [
        ['<=',14,13,2], ['<=',15.5,14,2], ['<=',12,10,4], ['<=',13.5,13,2],
        ['<=',8,7,2],['<=',8.5,8,2],['<=',7.5,7,2],['<=',3.5,3,1],['<=',3,3,1],
        # The following all have the same box. Could in principle also be ['<=',2,0],
        # But that would not literally include the edge. If we use the box given
        # here, then we get a noise layer change when the edge moves from 3.0 to
        # 2.999999..... But that seems unavoidable.... 
        ['<=',2,2,0],['<=',2.99,2,1],['<=',2.49,2,0.5],['<=',2.00001,2,0.0000152587890625],
        # These have a box that does not include the edge. In any event, these
        # would be suppressed, so we don't care what the box is.
        ['<=',1.8,2,0], ['<=',-100,2,0],
        ['<=',30,30,0],['<=',31,30,0],['<=',1000,30,0],
        # We should always get the same box regardless of operation:
        ['<=',14,13,2], ['<',14,13,2], ['>=',14,13,2], ['>',14,13,2],
        ['<=',2,2,0], ['<',2,2,0], ['>=',2,2,0], ['>',2,2,0], 
        ['<=',30,30,0], ['<',30,30,0], ['>=',30,30,0], ['>',30,30,0], 
        ['<=',15.5,14,2], ['<',15.5,14,2], ['>=',15.5,14,2], ['>',15.5,14,2], 
    ]
    for test in tests:
        test_getBox(bx,test,vals,points)

    vals = [ 3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,
              30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,
              41,42,43,44,45,46,47,48,49,50,51,52,53,
    ]
    print(vals)
    points = ineqTestsLib.makePointsFromVals(vals)
    # These tests are all [edge,boxLeft,boxWidth]
    tests = [
        # Note in the following that we can get a funky thing where moving an edge
        # further left (from 7.5 to 3.5) leads to a larger and more to the right
        # box (at least the right edge). This is because sometimes a larger AIDV
        # set can be suppressed compared to a smaller one. I think this is ok.
        ['<=',14,14,2], ['<=',12,10,4], ['<=',8,6,4],['<=',8.5,6,4],['<=',7.5,6,2],['<=',3.5,0,8],
        # The following will all be suppressed anyway, so box doesn't matter
        ['<=',2,0,8],['<=',2.99,0,8],['<=',2.49,0,8],['<=',2.00001,0,8],
        # These have a box that does not include the edge. In any event, these
        # would be suppressed, so we don't care what the box is.
        ['<=',1.8,0,8], ['<=',-100,0,8],
        ['<=',30,30,0],['<=',31,30,2],['<=',1000,52,2],['<=',500,52,2],
        # Note below that this change in the middle of a gap nevertheless causes
        # a new box. This is due to the left and right shift difference. Not sure
        # this helps or hurts. 
        ['<=',36,28,8],['<=',35,28,8],
    ]
    for test in tests:
        test_getBox(bx,test,vals,points)

    print('=========================================================')
    print('    Test getMatchingValues')
    print('=========================================================')
    vals = [ 3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,
              30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,
              41,42,43,44,45,46,47,48,49,50,51,52,53,
    ]
    print(vals)
    points = ineqTestsLib.makePointsFromVals(vals)
    # [operator,edge, [min,max boxed index],  [min,max true index]]
    tests = [
        # Note in following that the boxed values are the same
        ['<',-100,[0,None],[None,None]], 
        ['<',0,[0,None],[None,None]], 
        ['<',1,[0,None],[None,None]], 
        ['<=',1,[0,None],[None,None]],
        ['<=',2,[0,None],[None,None]],
        ['<=',3,[0,None],[0,None]], 
        # Following tests some suppressed values
        ['<=',14,[0,11],[0,11]], 
        ['<',15,[0,11],[0,11]], 
        ['<=',15,[0,11],[0,12]], 
        ['<=',19,[0,15],[0,16]], 
        # Following ensures that non-suppressed values are included
        ['>=',30,[23,54],[23,54]], 
        ['>',29,[23,54],[23,54]],
        ['>=',31,[42,54],[42,54]], 
        ['>',30,[42,54],[42,54]],
        # Following ensures that high values are dealt with properly
        ['>',100,[54,None],[None,None]],
        ['>',53,[54,None],[None,None]],
        ['>=',53.01,[54,None],[None,None]],
    ]
    for test in tests:
        test_getMatchingValues(bx,test,vals,points)

def runMultiChecks():
    print('=========================================================')
    print('    runMultiChecks')
    print('=========================================================')
    random.seed(1)
    bx = inequalities.boxes(base=2)
    mPointsCols = []
    mEdges = []
    vals = ineqTestsLib.makePointsCluster(50,1)
    points = ineqTestsLib.makePointsFromVals(vals)
    mPointsCols.append(points)
    edge = inequalities.edgeCompare(int(min(vals)+((max(vals)-min(vals))/2)),'>=')
    edge.print()
    mEdges.append(edge)
    vals = ineqTestsLib.makePointsCluster(50,1)
    points = ineqTestsLib.makePointsFromVals(vals)
    points = ineqTestsLib.shuffleAidvs(points)
    mPointsCols.append(points)
    edge = inequalities.edgeCompare(int(min(vals)+((max(vals)-min(vals))/2)),'>=')
    edge.print()
    mEdges.append(edge)
    mi = inequalities.multiInequalities(mPointsCols,mEdges,bx)
    print("mPointsCols:")
    pp.pprint(mi.mPointsCols)
    print("mPointsAidv:")
    pp.pprint(mi.mPointsAidv)
    print(f"start indices: {mi.startIndices}") 
    print("Hidden, Visible:")
    pp.pprint(mi.hvs)
    print("Final points:")
    pp.pprint(mi.mPoints)

pp = pprint.PrettyPrinter(indent=4)
runChecks()
runMultiChecks()
