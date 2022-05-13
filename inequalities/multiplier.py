import pprint
pp = pprint.PrettyPrinter(indent=4)

'''
We want to find a multiplier that fits perfectly in powers of 10...
'''

def doTest(mult,steps,start,finish):
    for _ in range(steps):
        start *= mult
    if abs(start - finish) < 0.001:
        return 'good'
    elif start < finish:
        return 'low'
    return 'high'


start = 10
finish = 100
for steps in range(1,10):
    left = 0
    right = 10
    mult = 5
    tries = 0
    while True:
        tries += 1
        result = doTest(mult,steps,start,finish)
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
    print(f"Multiplier for {steps} steps is {mult} (found in {tries} tries")
    begin = 0.1
    for _ in range((steps * 3)+1):
        print(f"{round(begin,2)}, ",end='')
        begin *= mult
    print('')

