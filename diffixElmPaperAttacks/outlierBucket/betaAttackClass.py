import sys
import os
import json
import statistics
import random
filePath = __file__
parDir = os.path.abspath(os.path.join(filePath, os.pardir, os.pardir))
sys.path.append(parDir)
import tools.score
import tools.stuff
import anonymize.anonAlgs

'''
This code is for the somewhat more realistic version of the outlier attack.
Here, we have a beta distribution with more or less skew at the top. The
attacker knows the highest contributor.
The attacker simply requests a histogram, and
then determines that the outliers are in buckets that have high counts.
For this to work, there needs to be more outliers than the minimum
out_range. Otherwise, the outliers will all be flattened.
'''

class betaAttack():
    def __init__(self):
        pass

    def selectVictimBucket(self,bktCountsLeft,bktCountsRight):
        maxDiff = -1000
        maxIndex = -1
        for i in range(len(bktCountsLeft)):
            diff = bktCountsRight[i] - bktCountsLeft[i]
            if diff > maxDiff:
                maxDiff = diff
                maxIndex = i
        return maxIndex,maxDiff

    def modifyBktForDistinct(self,oldBkt):
        '''
            Coming in, `oldBkt` has a per-AIDV contribution in terms of rows.
            We want to mimic what would happen if these rows were spread over
            a set of distinct values such that each value has between 2-4
            AIDVs. Then we run the distinct counting algorithm and compute
            a resulting per-AIDV contribution. This is substituted back into
            the bucket and returned.
        '''
        # First, assign distinct values (note these are associated with
        # a single bucket). (Note it doesn't matter if different buckets
        # have the same value.)
        aidvs = {}
        for aidv,cont in zip(oldBkt['aidvSet'], oldBkt['contributions']):
            aidvs[aidv] = cont
        dvals = {}
        val = 1
        while True:
            val += 1
            sampleAidvs = list(aidvs.keys())
            numAidvs = min(random.randint(1,4),len(sampleAidvs))
            dvals[val] = random.sample(sampleAidvs,k=numAidvs)
            for aidv in dvals[val]:
                aidvs[aidv] -= 1
                if aidvs[aidv] == 0:
                    del aidvs[aidv]
            if len(aidvs) == 0:
                break
        return self.computeContributionsFromVals(dvals)

    def computeContributionsFromVals(self,dvals):
        # dvals is a dict of {val,[list of aidvs]}
        ''' DQH step 3.1: For each AIDV, list all of the suppressed
            column values for which the AIDV is a bucket member.  '''
        aidvs = {}
        for val,aidvl in dvals.items():
            for aidv in aidvl:
                if aidv in aidvs:
                    aidvs[aidv].append(val)
                else:
                    aidvs[aidv] = [val]
        ''' DQH step 3.2: Sort the AIDVs according to the number
            of suppressed column values ascending.'''
        sortedAidvVals = []
        for aidv,vals in aidvs.items():
            sortedAidvVals.append([aidv,len(vals)])
        sortedAidvVals.sort(key=lambda tup: tup[1])
        sortedAidvs = []
        for i in range(len(sortedAidvVals)):
            sortedAidvs.append(sortedAidvVals[i][0])
        ''' DQH step 3.3: Repeatedly traverse the sorted list until
            all suppressed column values are assigned to one
            AIDV. For each encountered AIDV X, if there is
            an associated suppressed column value that is not
            assigned to any AIDV, then assign it to AIDV X. (If
            there are no unassigned values, then AIDV X may
            be removed from the sorted list.)'''
        # We'll use sortedAidvs to count the vals assigned to each AIDV
        aidvCont = {}
        for i in range(len(sortedAidvs)):
            aidvCont[sortedAidvs[i]] = 0
        for i in range(10000000000000000):
            index = i%len(sortedAidvs)
            aidv = sortedAidvs[index]
            #print(f"i {i} -> index {index} -> aidv {aidv}")
            #print(sortedAidvs)
            if aidv not in aidvs:
                pp.pprint(sortedAidvs)
                pp.pprint(aidvs)
                pp.pprint(aidvCont)
                print(f"index {index} for aidv {aidv}")
            val = random.choice(aidvs[aidv])
            aidvCont[aidv] += 1
            allDone = self.cleanOutVal(val,sortedAidvs,aidvs)
            if allDone:
                break
        bkt = {'aidvSet':[],'contributions':[]}
        for aidv,cont in aidvCont.items():
            bkt['aidvSet'].append(aidv)
            bkt['contributions'].append(cont)
        return bkt

    def cleanOutVal(self,val,sortedAidvs,aidvs):
        #print("--------------------------")
        aidvList = sortedAidvs.copy()
        for aidv in aidvList:
            if val in aidvs[aidv]:
                aidvs[aidv].remove(val)
                if len(aidvs[aidv]) == 0:
                    #pp.pprint(sortedAidvs)
                    del aidvs[aidv]
                    sortedAidvs.remove(aidv)
                    #pp.pprint(sortedAidvs)
                    if len(sortedAidvs) == 0:
                        return True
        return False
    
    def runOne(self,params,mcv,salt):
        countType = params['countType']
        numUnknownVals = params['numUnknownVals']
        sd = params['SD']
        alphbet = params['alphbet']
        outParams = params['outParams']
        aidvPerBucket = round(1000/numUnknownVals)
        alpha = alphbet[0]
        beta = alphbet[1]
        # The specific column names and values don't matter, so long as they are consistent
        # within the set of buckets
        cols = mcv.getCols(3)
        vals = mcv.getVals(3)
        # for each outlier, select a bucket where the outlier will go
        buckets = []
        maxContribution = 0
        victimBucket = 0
        # Each bucket has a different set of AIDVs. Each AIDV has a different
        # contribution amount. The one with the largest contribution amount
        # is designated as the victim (we are trying to guess the bucket
        # of the largest contributor)
        for bktIndex in range(numUnknownVals):
            mas = tools.stuff.makeAidvSets(baseIndividuals=aidvPerBucket)
            mas.makeBase()
            contributions = []
            for _ in range(aidvPerBucket):
                cont = round(random.betavariate(alpha,beta) * 1000) + 1
                if cont > maxContribution:
                    maxContribution = cont
                    victimBucket = bktIndex
                contributions.append(cont)
            bkt = {
                'aidvSet': mas.aidvSet,
                'contributions': contributions,
            }
            if countType == 'distinct':
                bkt = self.modifyBktForDistinct(bkt)
            buckets.append(bkt)
        # Compute the noisy count for each bucket
        noisyCounts = []
        noises = []
        anon = anonymize.anonAlgs.anon(0,0,0,[sd],salt=salt,
                                    outRange=outParams[0],topRange=outParams[1])
        for bktIndex in range(numUnknownVals):
            bkt = buckets[bktIndex]
            # By convention, assume that last column contains the unknown value
            vals[-1] = bktIndex
            trueCount = sum(bkt['contributions'])
            #print(f'{numTries} {numClaimHas}',flush=True)
            noise,noisyCount = anon.getNoise(trueCount,aidvSet=bkt['aidvSet'],cols=cols,vals=vals,
                                            contributions=bkt['contributions'])
            noisyCounts.append(noisyCount)
            noises.append(noise)
        # The attack is to select the bucket with the highest count as the victim bucket
        maxNoisyCount = max(noisyCounts)
        guessedBkt = noisyCounts.index(maxNoisyCount)
        if guessedBkt == victimBucket:
            claimCorrect = True
        else:
            claimCorrect = False
        meanNoisyCount = statistics.mean(noisyCounts)
        excess = maxNoisyCount/meanNoisyCount
        return claimCorrect,excess

    def basicAttack(self,scoreProb,jparams,claimThresh,tries=10000,atLeast=100):
        params = json.loads(jparams)
        bailOutReason = ''
        random.seed()
        salt = random.randint(1000,100000000)
        score = tools.score.score(scoreProb)
        mcv = tools.stuff.makeColsVals()
        # Nominally we'll make `tries` attempts, but we need to have at
        # least `atLeast` claims that the victim has the attribute
        numTries = 0
        numClaimHas = 0
        numNoClaims = 0
        while True:
            numTries += 1
            claimCorrect,excess = self.runOne(params,mcv,salt)
            # We need to decide if we want to make a claim at all.
            # We define a threshold as how much the max exceeds the average
            if claimThresh and excess < claimThresh:
                #print(f"claimThresh {claimThresh}, excess {excess}, max {maxNoisyCount}, mean {meanNoisyCount}",flush=True)
                # Don't make a claim
                numNoClaims += 1
                makesClaim = False
                dontCare = True
                score.attempt(makesClaim,dontCare,dontCare)
                if numTries > tries * 100:
                    bailOutReason = f"Bail Out: too many tries (> {tries * 100})"
                    break
                continue
            makesClaim = True
            claimHas = True
            numClaimHas += 1
            score.attempt(makesClaim,claimHas,claimCorrect)
            if numTries > tries * 100:
                # If we can't get enough above threshold samples in this many tries,
                # then give up. This prevents us from never terminating because we
                # can't get `atLeast` above threshold samples
                bailOutReason = f"Bail Out: too many tries (> {tries * 100})"
                break
            if numTries >= tries and numClaimHas >= atLeast:
                break
            if claimThresh and numClaimHas > atLeast*2 and numClaimHas % atLeast*2 == 1:
                # We have some reasonable number of claims. If CI is not that high,
                # then we can quit early so the calling code can compute a larger threshold.
                claimRate,confImprove,confidence = score.computeScore()
                if confImprove < 0.9:
                    bailOutReason = f"Bail out: CI too low ({confImprove})"
                    break
        claimRate,confImprove,confidence = score.computeScore()
        cr,ci,c = score.prettyScore()
        if claimRate == 0:
            # We couldn't make even one claim, but don't want 0 rate because
            # that won't plot on a log scale!
            claimRate = 1/(tries*100*10)
            cr = str(claimRate)
        if numClaimHas < 10:
            # There just aren't enough samples to get a meaningful CI
            confImprove = 1.05
            confidence = 1.05
            ci = '1.05'
            c = '1.05'
        print(bailOutReason,flush=True)
        print(f"numNoClaim {numNoClaims}, numClaimHas {numClaimHas}",flush=True)
        result = {'CR':claimRate,'CI':confImprove,'C':confidence,
                   'PCR':cr,'PCI':ci,'PC':c,'claimThresh':claimThresh,'excess':excess,
                   'numClaimHas':numClaimHas}
        return result

if __name__ == "__main__":
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    ba = betaAttack()
    aidvPerBucket = 5
    alpha = 2
    beta = 16
    mas = tools.stuff.makeAidvSets(baseIndividuals=aidvPerBucket)
    mas.makeBase()
    contributions = []
    for _ in range(aidvPerBucket):
        cont = round(random.betavariate(alpha,beta) * 1000) + 1
        contributions.append(cont)
    bkt = {
        'aidvSet': mas.aidvSet,
        'contributions': contributions,
    }
    pp.pprint(bkt)
    newBkt = ba.modifyBktForDistinct(bkt)
    pp.pprint(newBkt)