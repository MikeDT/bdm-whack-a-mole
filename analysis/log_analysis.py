# -*- coding: utf-8 -*-
"""
Created on Sat May 15 17:08:29 2021

@author: Mike
"""
import pandas as pd
import matplotlib.pyplot as plt

import os
from os import listdir
from os.path import isfile, join

mypath = os.getcwd()
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

files = [i for i in onlyfiles if '.log' in i]


skill_luck_rat = 'demo'
skill_luck_rat, score, skill_luck_rating, mole_x, mole_y, rel_x,rel_y = None, None,None,None,None,None,None

columns = ['file', 'time', 'mole_up_time', 'time_step', 'step','luck_skill', 'score', 'skill_luck_rating', 'molexy',
                             'mole_x', 'mole_y', 'rel_x', 'rel_y', 'hit/miss']


results = []

for file in files:
    f = open(file)
    line = f.readline()
    print(file)
    i=0
    j=0
    while line:
        time = line[11:23]
        i+=1
        if 'Event(11-Score' in line:
             tmp_line = line.split("score_inc': ")
             score = tmp_line[1][0]
             tmp_line = line.split("skill/luck':")
             true_score = tmp_line[1][0]
        elif "Event(10-MoleUp)" in line:
             mole_up_time = line[11:23]
        elif "_vs_luck_rating': " in line:
             tmp_line = line.split("_vs_luck_rating': ")
             skill_luck_rating = tmp_line[1][0:6]
             try:
                 skill_luck_rating = skill_luck_rating.split(',')[0]
             except:
                 pass
        elif "9-Hit Attempt {'result': [False," in line:
             j +=1
             tmp_line = line.split("'pos': (")
             mole_x = tmp_line[1].split(", ")[0]
             mole_y = tmp_line[1].split(", ")[1].split(')')[0]
             tmp_line = line.split("'relative_loc': (")
             rel_x = tmp_line[1].split(", ")[0]
             rel_y = tmp_line[1].split(", ")[1].split(')')[0]        
             results += [[file, time, mole_up_time, i,j, skill_luck_rat, 0, skill_luck_rating, 
                          str(mole_x) + '_' + str(mole_y), mole_x, mole_y, rel_x,rel_y, 'miss']]
        elif "9-Hit Attempt {'result': [True," in line:
             j +=1
             tmp_line = line.split("'pos': (")
             mole_x = tmp_line[1].split(", ")[0]
             mole_y = tmp_line[1].split(", ")[1].split(')')[0]
             tmp_line = line.split("'relative_loc': (")
             rel_x = tmp_line[1].split(", ")[0]
             rel_y = tmp_line[1].split(", ")[1].split(')')[0]        
             results += [[file, time, mole_up_time, i,j, skill_luck_rat, score, skill_luck_rating, 
                          str(mole_x) + '_' + str(mole_y), mole_x, mole_y, rel_x,rel_y, 'hit']]
        elif "12-Skill_Luck_Ratio" in line:
             tmp_line = line.split("12-Skill_Luck_Ratio {'New': ")
             skill_luck_rat = tmp_line[1][0:4]
        line = f.readline()
    f.close()   

df = pd.DataFrame(results, columns = columns)


for col in columns[1:]:
    try:
        df[col] = df[col].astype(float)
    except:
        None

df['distance'] = df['rel_x']**2 + df['rel_y']**2
df['distance'] = df['distance']**0.5


df = df[df['step'] >30]

# calculate the mean rating, score, z score etc.

from scipy.stats import zscore

df['skill_luck_rating_Zscore'] = df['skill_luck_rating'] 
df['skill_luck_rating_Zscore_hitmiss'] = df['skill_luck_rating'] 
df['skill_luck_rating_minmax'] = df['skill_luck_rating'] 
df['skill_luck_rating_minmax_hitmiss'] = df['skill_luck_rating'] 

df['skill_luck_rating_Zscore'] = df.groupby(['file']).skill_luck_rating_Zscore.transform(lambda x : zscore(x,ddof=1))    
df['skill_luck_rating_Zscore_hitmiss'] = df.groupby(['file', 'hit/miss']).skill_luck_rating_Zscore_hitmiss.transform(lambda x : zscore(x,ddof=1))    
df['skill_luck_rating_minmax'] = df.groupby(['file']).skill_luck_rating_minmax.transform(lambda x: (x-min(x))/(max(x)-min(x)))   
df['skill_luck_rating_minmax_hitmiss'] = df.groupby(['file', 'hit/miss']).skill_luck_rating_minmax_hitmiss.transform(lambda x: (x-min(x))/(max(x)-min(x)))   

df['distance_Zscore'] = df['distance'] 
df['distance_Zscore_hitmiss'] = df['distance']
df['distance_minmax'] = df['distance'] 
df['distance_minmax_hitmiss'] = df['distance'] 

df['distance_Zscore'] = df.groupby(['file']).distance_Zscore.transform(lambda x : zscore(x,ddof=1))    
df['distance_Zscore_hitmiss'] = df.groupby(['file', 'hit/miss']).distance_Zscore_hitmiss.transform(lambda x : zscore(x,ddof=1))
df['distance_minmax'] = df.groupby(['file']).distance_minmax.transform(lambda x: (x-min(x))/(max(x)-min(x)))   
df['distance_minmax_hitmiss'] = df.groupby(['file', 'hit/miss']).distance_minmax_hitmiss.transform(lambda x: (x-min(x))/(max(x)-min(x)))   

df.to_csv('results_v3.csv')


# plt.title('Relative Hit Locations')
# plt.scatter(df['rel_x'], df['rel_y'], alpha=0.2)
# plt.xlabel('rel_x')
# plt.ylabel('rel_y')
# plt.xlim(-30,30)
# plt.ylim(-30,30)
# plt.show()

# plt.title('Distance vs Skill Luck Rating')
# plt.scatter(df['distance'], df['skill_luck_rating'], alpha=0.2)
# plt.xlabel('distance')
# plt.ylabel('skill_luck_rating')
# plt.xlim(0,30)
# plt.ylim(0.1,0.5)
# plt.show()

# plt.title('Environment Skill vs Skill Luck Rating')
# plt.scatter(df['luck_skill'], df['skill_luck_rating'], alpha=0.2)
# plt.xlabel('luck_skill actual')
# plt.ylabel('skill_luck_rating')
# plt.xlim(0,1)
# plt.ylim(0.1,0.5)
# plt.show()

# plt.title('Environment Skill vs Skill Luck Rating OVer time')
# #plt.plot(df['score'], alpha=0.2, c='g')
# plt.plot(df['skill_luck_rating'], alpha=0.2, c = 'b')
# plt.plot(df['luck_skill'], alpha=0.2, c='r')
# plt.show()

