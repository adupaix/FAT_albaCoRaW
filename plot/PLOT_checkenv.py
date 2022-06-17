#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 26 09:50:25 2018
@author: geraldine

Modified on Fri Feb 05 2021, by adupaix
"""


# #%%############################################################################
# #~ 1. TEST IN PLOTING

if environment == "square":
    plot_title = str(environment)+' '+str(studyYear)+' | inter-FAD distances= '+str(FADs.distFAD)+' km | $N_{FAD}$='+str(FADs.nFAD)
elif environment in ["random","square_rd"]:
    plot_title = str(environment)+' '+str(studyYear)+' | mean inter-FAD distances= '+str(FADs.distFAD)+' km | $N_{FAD}$='+str(FADs.nFAD)
    if environment == "square_rd":
        plot_title = plot_title+' | R0= '+str(FADs.R0)+' km'
else:
    plot_title = str(environment)+' '+str(studyYear)+' | $N_{FAD}$='+str(FADs.nFAD)
    
    
fig=plt.figure(1) 
fig, ax = plt.subplots(figsize=(10, 10)) #figsize=(longueur, hauteur)
    #~ Plot axis
plt.ylabel('y')
plt.xlabel('x')
plt.title(plot_title)
plt.axis('equal')
for i in range(0, int(FADs.nFAD)):
    fad_circle_oz=plt.Circle((FADs.x[i], FADs.y[i]), TUNA.R0, color='green', fill=False)
    ax.add_patch(fad_circle_oz)
for i in range(0, int(FADs.nFAD)):
    fad_circle_oz=plt.Circle((FADs.x[i], FADs.y[i]), FADs.dr[i], color='red', fill=False)
    ax.add_patch(fad_circle_oz)
#~ Plot FAD
plt.plot(FADs.x[FADs.has_buoy], FADs.y[FADs.has_buoy], 'k+', label='Equiped FAD')

if environment not in ["square","random","square_rd","maldives"] and len(land_files) > 0:
    for i in range(len(Island.x)):
        plt.plot(Island.x[i:i+2],
                 Island.y[i:i+2],
                 "-", color = "black")
elif environment == "maldives":
    for j in range(len(Island)):
        for i in range(len(Island[j].x)):
            plt.plot(Island[j].x[i:i+2],
                 Island[j].y[i:i+2],
                 "-", color = "black")

if environment in ["square","random","square_rd"]:
    plt.savefig(path_output+"/FAD_array/env_plot.png")
    
#%%############################################################################

    
