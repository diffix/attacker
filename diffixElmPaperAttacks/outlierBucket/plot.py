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

with open('betaData.json', 'r') as f:
    data = json.load(f)
df = pd.DataFrame.from_dict(data)
df['alphbet'] = df['alphbet'].apply(str)
df['outParams'] = df['outParams'].apply(str)
df = df.rename(columns={'numUnknownVals':'Unknown Vals'})
df = df.rename(columns={'alphbet':'Alpha-Beta'})

plt.figure(figsize=(6, 3))
ax = sns.scatterplot(data=df, x="CR", y="CI",hue='Unknown Vals',style='Alpha-Beta',s=80)
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
ax.legend(loc='lower center', bbox_to_anchor=(0.5, 1.0), ncol=2)
plt.grid()
#plt.ylim(0,1.0)
for shape in shapes:
    plt.gca().add_patch(shape)
plt.savefig('beta-outlier.png',bbox_inches='tight')

with open('data.json', 'r') as f:
    data = json.load(f)
dfOrig = pd.DataFrame.from_dict(data)
dfOrig['CR'] = pd.to_numeric(dfOrig['CR'])
dfOrig['CI'] = pd.to_numeric(dfOrig['CI'])
dfOrig['C'] = pd.to_numeric(dfOrig['C'])
dfOrig['Num Outliers'] = dfOrig['Num Outliers'].apply(str)
dfOrig = dfOrig.rename(columns={'setting':'Setting'})
df = dfOrig.rename(columns={'Out Factor':'of'})
df = df.query("of == 5.0")
df = df.rename(columns={'of':'Out Factor'})

plt.figure(figsize=(6, 3))
ax = sns.scatterplot(data=df, x="CR", y="CI",hue='Setting',style='Unknown Vals',s=80)
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
ax.legend(loc='lower left', bbox_to_anchor=(1.0, 0.0), ncol=1)
plt.grid()
for shape in shapes:
    plt.gca().add_patch(shape)
plt.ylim(0,1.1)
plt.xlim(0.000001,2.0)
plt.savefig('worst-outlier.png',bbox_inches='tight')

plt.figure(figsize=(6, 3))
ax = sns.scatterplot(data=df, x="CR", y="CI",hue='Setting',style='Unknown Vals',s=80)
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
ax.legend(loc='lower left', bbox_to_anchor=(1.0, 0.0), ncol=1)
plt.grid()
for shape in shapes:
    plt.gca().add_patch(shape)
plt.ylim(0.94,1.02)
plt.xlim(0.001,1.0)
plt.savefig('worst-outlier-close.png',bbox_inches='tight')

# ---------------------------------------------------------------
df = dfOrig.query("CI > 0.95")
df = df.rename(columns={'Unknown Vals':'uv'})
df = df.query("uv < 15")
df = df.rename(columns={'uv':'Unknown Vals'})
plt.figure(figsize=(6, 3))
ax2 = sns.boxplot(x='Out Factor',y='CR',data=df,hue='Unknown Vals')
ax2.set(yscale='log')
params = {
    'numBoxes':20,
    'fromLeft':-1,
    'toLeft':-1,
    'fromBottom':0.45,
    'toBottom':0.7,
    'right':5,
    'top':1.1,
    'alpha':0.03,
    'risk_level':'low',
    #'alpha':0.5,
}
rp = tools.risk.riskPatches()
shapes = rp.getShapes(params)
ax2.set(ylabel = 'Prediction Rate (PR)', xlabel='Average Extreme Contribution')
ax2.grid(axis='y')
ax2.set(xticklabels=["16","18","21","37","65"])
for shape in shapes:
    plt.gca().add_patch(shape)
ax2.legend(title='Unknown Vals',loc='lower left', bbox_to_anchor=(0.7, 0.0), ncol=1)
plt.savefig('worst-by-out-factor.png',bbox_inches='tight')

with open('distinctBetaData.json', 'r') as f:
    data = json.load(f)
df = pd.DataFrame.from_dict(data)
df['alphbet'] = df['alphbet'].apply(str)
df['outParams'] = df['outParams'].apply(str)
df = df.rename(columns={'numUnknownVals':'Unknown Vals'})
df = df.rename(columns={'alphbet':'Alpha-Beta'})

plt.figure(figsize=(6, 3))
ax = sns.scatterplot(data=df, x="CR", y="CI",hue='Unknown Vals',style='Alpha-Beta',s=80)
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
ax.legend(loc='lower center', bbox_to_anchor=(0.5, 1.0), ncol=2)
plt.grid()
plt.ylim(0,1.0)
plt.xlim(0.000001,1.2)
for shape in shapes:
    plt.gca().add_patch(shape)
plt.savefig('distinct-beta-outlier.png',bbox_inches='tight')
