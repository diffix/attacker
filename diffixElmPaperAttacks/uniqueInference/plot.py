import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pprint
pp = pprint.PrettyPrinter(indent=4)

with open('results.json', 'r') as f:
    results = json.load(f)

for dataset in results.keys():
    for resName in results[dataset].keys():
        if resName == 'original':
            continue
        data = {'Precision':[],'Total Rows':[],'NULL':[]}
        for k,v in results[dataset][resName]['compare'].items():
            total = v['numMatch'] + v['numMiss']
            if total == 0:
                print(k)
                pp.pprint(v)
                continue
            precision = v['numMatch'] / total
            data['Precision'].append(precision)
            data['Total Rows'].append(total)
            data['NULL'].append(v['NULL'])

        df = pd.DataFrame.from_dict(data)
        plt.figure(figsize=(6, 3))
        ax = sns.scatterplot(data=df, x="Precision", y="Total Rows",hue='NULL',s=80)
        ax.set(yscale='log')
        plt.xlabel('Precision',fontsize=12)
        plt.ylabel('Total Rows',fontsize=12)
        ax.legend(loc='lower center', bbox_to_anchor=(0.5, 1.0), ncol=1)
        plt.grid()
        figName = resName + '.png'
        plt.savefig(figName,bbox_inches='tight')