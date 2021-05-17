# -*- coding: utf-8 -*-
"""
Created on Sat May 15 17:08:29 2021

@author: Mike
"""
import pandas as pd
import matplotlib.pyplot as plt

f = open("Laky.log")
f = open("harada.log")
f = open("Nizar.log")
skill_luck_rat = 'demo'
line = f.readline()
skill_luck_rat, score, skill_luck_rating, mole_x, mole_y, rel_x,rel_y = None, None,None,None,None,None,None

results = []
while line:
    if 'Event(11-Score' in line:
         tmp_line = line.split("score_inc': ")
         score = tmp_line[1][0]
    elif "_vs_luck_rating': " in line:
         tmp_line = line.split("_vs_luck_rating': ")
         skill_luck_rating = tmp_line[1][0:6]
         try:
             skill_luck_rating = skill_luck_rating.split(',')[0]
         except:
             pass
    elif "9-Hit Attempt {'result':" in line:
         tmp_line = line.split("'pos': (")
         mole_x = tmp_line[1].split(", ")[0]
         mole_y = tmp_line[1].split(", ")[1].split(')')[0]
         tmp_line = line.split("'relative_loc': (")
         rel_x = tmp_line[1].split(", ")[0]
         rel_y = tmp_line[1].split(", ")[1].split(')')[0]        
         results += [[skill_luck_rat, score, skill_luck_rating, mole_x, mole_y, rel_x,rel_y]]
    elif "12-Skill_Luck_Ratio" in line:
         tmp_line = line.split("12-Skill_Luck_Ratio {'New': ")
         skill_luck_rat = tmp_line[1][0:4]
    line = f.readline()
f.close()   

columns = ['luck_skill', 'score', 'skill_luck_rating',
                             'mole_x', 'mole_y', 'rel_x', 'rel_y']
df = pd.DataFrame(results, columns = columns)
for col in columns[1:]:
    df[col] = df[col].astype(float)

df['distance'] = df['rel_x']**2 + df['rel_y']**2
df['distance'] = df['distance']**0.5
print(df)


plt.title('Relative Hit Locations')
plt.scatter(df['rel_x'], df['rel_y'], alpha=0.2)
plt.xlabel('rel_x')
plt.ylabel('rel_y')
plt.xlim(-30,30)
plt.ylim(-30,30)
plt.show()

plt.title('Distance vs Skill Luck Rating')
plt.scatter(df['distance'], df['skill_luck_rating'], alpha=0.2)
plt.xlabel('distance')
plt.ylabel('skill_luck_rating')
plt.xlim(0,30)
plt.ylim(0.1,0.5)
plt.show()

plt.title('Environment Skill vs Skill Luck Rating')
plt.scatter(df['luck_skill'], df['skill_luck_rating'], alpha=0.2)
plt.xlabel('luck_skill actual')
plt.ylabel('skill_luck_rating')
plt.xlim(0,1)
plt.ylim(0.1,0.5)
plt.show()

plt.title('Environment Skill vs Skill Luck Rating OVer time')
#plt.plot(df['score'], alpha=0.2, c='g')
plt.plot(df['skill_luck_rating'], alpha=0.2, c = 'b')
plt.plot(df['luck_skill'], alpha=0.2, c='r')
plt.show()

