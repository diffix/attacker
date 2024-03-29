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

with open('data.json', 'r') as f:
    data = json.load(f)
dfInit = pd.DataFrame.from_dict(data)
#df = dfInit.query('SD > 0.5 and `Stat Guess` < 0.9')
df = dfInit.query('SD > 0.5 and `Stat Guess` < 1.0')
df = df.rename(columns={'Stat Guess':'Value Freq.'})
df['SD'] = df['SD'].replace([1.5,2.25,3.0],['1.5 (P)','2.25 (XP)','3.0 (XXP)'])
#df['SD'] = df['SD'].astype(str)
plt.figure(figsize=(6, 3))
colors = {1.0:"purple",'1.5 (P)': "red", '2.25 (XP)': "orange", '3.0 (XXP)': "blue"}
ax = sns.scatterplot(data=df, x="CR", y="CI",style='Value Freq.',hue='SD',
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
    'risk_level':'low',
    #'alpha':0.5,
}
rp = tools.risk.riskPatches()
shapes = rp.getShapes(params)
plt.xlabel('Prediction Rate (PR)',fontsize=12)
plt.ylabel('Precision Improvement (PI)',fontsize=12)
ax.legend(loc='lower center', bbox_to_anchor=(0.6, 0.1), ncol=2)
plt.grid()
for shape in shapes:
    plt.gca().add_patch(shape)
plt.savefig('sim-know-noise.png',bbox_inches='tight')
