import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import sys
import os
filePath = __file__
parDir = os.path.abspath(os.path.join(filePath, os.pardir, os.pardir))
sys.path.append(parDir)
import tools.risk
import pprint
pp = pprint.PrettyPrinter(indent=4)
colors = {'1.5 (P)': "red", '2.25 (XP)': "orange", '3.0 (XXP)': "blue"}

# -------------------------------------------------------------------------------------
with open('dataDiffLed.json', 'r') as f:
    data = json.load(f)
df = pd.DataFrame.from_dict(data)

plt.figure(figsize=(6, 3))
df['numUnknownVals'] = df['numUnknownVals'].apply(str)
df = df.rename(columns={'numUnknownVals':'Unknown Vals'})
df = df.rename(columns={'numIsolated':'Num Isolated'})
ax = sns.scatterplot(data=df, x="CR", y="CI",hue='Unknown Vals',style='Num Isolated',s=80)
ax.set(xscale='log')
params = {
    'numBoxes':20,
    'fromLeft':0.000008,
    'toLeft':0.00008,
    'fromBottom':0.45,
    'toBottom':0.7,
    'right':2.0,
    'top':1.1,
    'alpha':0.03,
    'risk_level':'low',
    #'alpha':0.5,
}
rp = tools.risk.riskPatches()
shapes = rp.getShapes(params)
plt.xlabel('Prediction Rate (PR)',fontsize=12)
plt.ylabel('Precision Improvement (PI)',fontsize=12)
ax.legend(loc='lower center', bbox_to_anchor=(0.65, 0.7), ncol=2)
plt.grid()
#plt.ylim(0,1.1)
for shape in shapes:
    plt.gca().add_patch(shape)
plt.savefig('diff-attack-led.png',bbox_inches='tight')

plt.figure(figsize=(6, 3))
ax = sns.scatterplot(data=df, x="CR", y="CI",style='Num Isolated',hue='SD',s=80)
ax.set(xscale='log')
params = {
    'numBoxes':20,
    'fromLeft':0.000008,
    'toLeft':0.00008,
    'fromBottom':0.45,
    'toBottom':0.7,
    'right':2.0,
    'top':1.1,
    'alpha':0.03,
    #'alpha':0.5,
}
rp = tools.risk.riskPatches()
shapes = rp.getShapes(params)
plt.xlabel('Prediction Rate (PR)',fontsize=12)
plt.ylabel('Precision Improvement (PI)',fontsize=12)
ax.legend(loc='lower center', bbox_to_anchor=(0.65, 0.7), ncol=2)
plt.grid()
#plt.ylim(0,1.1)
for shape in shapes:
    plt.gca().add_patch(shape)
plt.savefig('diff-attack-led-iso.png',bbox_inches='tight')

plt.figure(figsize=(6, 3))
ax = sns.scatterplot(data=df, x="CR", y="C",hue='Unknown Vals',style='Num Isolated',s=80)
ax.set(xscale='log')
plt.xlabel('Prediction Rate (PR)',fontsize=12)
plt.ylabel('Precision (C)',fontsize=12)
ax.legend(loc='upper center', bbox_to_anchor=(0.4, 1.2), ncol=2)
plt.grid()
#plt.ylim(0,1.0)
plt.savefig('diff-attack-led-conf.png',bbox_inches='tight')

# -------------------------------------------------------------------------------------
with open('dataDiffElm1.json', 'r') as f:
    data = json.load(f)
df = pd.DataFrame.from_dict(data)

plt.figure(figsize=(6, 3))
ax = sns.scatterplot(data=df, x="CR", y="CI",style='Unknown Vals',hue='SD',s=80)
ax.set(xscale='log')
params = {
    'numBoxes':20,
    'fromLeft':0.000008,
    'toLeft':0.00008,
    'fromBottom':0.45,
    'toBottom':0.7,
    'right':2.0,
    'top':1.1,
    'alpha':0.03,
    #'alpha':0.5,
}
rp = tools.risk.riskPatches()
shapes = rp.getShapes(params)
plt.xlabel('Prediction Rate (PR)',fontsize=12)
plt.ylabel('Precision Improvement (PI)',fontsize=12)
ax.legend(loc='lower center', bbox_to_anchor=(0.6, 0.0), ncol=1)
plt.grid()
plt.ylim(0,1.0)
for shape in shapes:
    plt.gca().add_patch(shape)
plt.savefig('diff-elm1-attack.png',bbox_inches='tight')

# -------------------------------------------------------------------------------------
with open('dataChangeAvg.json', 'r') as f:
    data = json.load(f)
df = pd.DataFrame.from_dict(data)
df = df.rename(columns={'numSamples':'Samples'})

plt.figure(figsize=(6, 3))
ax = sns.scatterplot(data=df, x="CR", y="CI",hue='Samples',s=80)
ax.set(xscale='log')
params = {
    'numBoxes':20,
    'fromLeft':0.000008,
    'toLeft':0.00008,
    'fromBottom':0.45,
    'toBottom':0.7,
    'right':2.0,
    'top':1.1,
    'alpha':0.03,
    'risk_level':'high',
    #'alpha':0.5,
}
rp = tools.risk.riskPatches()
shapes = rp.getShapes(params)
plt.xlabel('Prediction Rate (PR)',fontsize=12)
plt.ylabel('Precision Improvement (PI)',fontsize=12)
ax.legend(title='Samples',loc='lower center', bbox_to_anchor=(0.6, 0.6), ncol=2)
plt.grid()
#plt.ylim(0,1.0)
for shape in shapes:
    plt.gca().add_patch(shape)
plt.savefig('change-avg-attack.png',bbox_inches='tight')

# ----------------------------------------------------------------------------------
with open('dataDiff.json', 'r') as f:
    data = json.load(f)
dfInit = pd.DataFrame.from_dict(data)
df = dfInit.query('SD > 0.5')
df['SD'] = df['SD'].replace([1.5,2.25,3.0],['1.5 (P)','2.25 (XP)','3.0 (XXP)'])

plt.figure(figsize=(6, 3))
ax = sns.scatterplot(data=df, x="CR", y="CI",style='Unknown Vals',hue='SD',s=80)
ax.set(xscale='log')
params = {
    'numBoxes':20,
    'fromLeft':0.000008,
    'toLeft':0.00008,
    'fromBottom':0.45,
    'toBottom':0.7,
    'right':2.0,
    'top':1.1,
    'alpha':0.03,
    #'alpha':0.5,
}
rp = tools.risk.riskPatches()
shapes = rp.getShapes(params)
plt.xlabel('Prediction Rate (PR)',fontsize=12)
plt.ylabel('Precision Improvement (PI)',fontsize=12)
ax.legend(loc='lower left', bbox_to_anchor=(0.0, 0.0), ncol=2)
plt.grid()
for shape in shapes:
    plt.gca().add_patch(shape)
plt.savefig('diff-attack.png',bbox_inches='tight')

# The above plot assumes that the attack conditions exist. The
# following plot incorporates the probabilty that the attack
# conditions exist for a given user based on measures of the
# big_census.csv table (1/50000)

df['CR'] = df['CR'].apply(lambda x: x/50000)
plt.figure(figsize=(6, 3))
ax = sns.scatterplot(data=df, x="CR", y="CI",style='Unknown Vals',hue='SD',s=80)
ax.set(xscale='log')
params = {
    'numBoxes':20,
    'fromLeft':0.000008,
    'toLeft':0.00008,
    'fromBottom':0.45,
    'toBottom':0.7,
    'right':2.0,
    'top':1.1,
    'alpha':0.03,
    #'alpha':0.5,
}
rp = tools.risk.riskPatches()
shapes = rp.getShapes(params)
plt.xlabel('Prediction Rate (PR) x Vulnerability Probability',fontsize=12)
plt.ylabel('Precision Improvement (PI)',fontsize=12)
ax.legend(loc='upper right', bbox_to_anchor=(1.0, 1.0), ncol=1)
plt.grid()
plt.xlim(10e-9,1.0)
for shape in shapes:
    plt.gca().add_patch(shape)
plt.savefig('diff-attack-adjusted.png',bbox_inches='tight')

# ---------------------------------------------------------------------------
with open('dataChangeDiff.json', 'r') as f:
    data = json.load(f)

dfInit = pd.DataFrame.from_dict(data)
df = dfInit.query('SD > 0.5')
df['SD'] = df['SD'].replace([1.5,2.25,3.0],['1.5 (P)','2.25 (XP)','3.0 (XXP)'])
df = df.rename(columns={'numUnknownVals':'Unknown Vals'})

plt.figure(figsize=(6, 3))
ax = sns.scatterplot(data=df, x="CR", y="CI",style='Unknown Vals',hue='SD',
                     palette=colors,s=80)
ax.set(xscale='log')
params = {
    'numBoxes':20,
    'fromLeft':0.000008,
    'toLeft':0.00008,
    'fromBottom':0.45,
    'toBottom':0.7,
    'right':2.0,
    'top':1.1,
    'alpha':0.03,
    'risk_level':'high',
    #'alpha':0.5,
}
rp = tools.risk.riskPatches()
shapes = rp.getShapes(params)
plt.xlabel('Prediction Rate (PR)',fontsize=12)
plt.ylabel('Precision Improvement (PI)',fontsize=12)
ax.legend(loc='lower center', bbox_to_anchor=(0.65, 0.7), ncol=2)
plt.grid()
#plt.ylim(0,1.0)
for shape in shapes:
    plt.gca().add_patch(shape)
plt.savefig('change-attack.png',bbox_inches='tight')
