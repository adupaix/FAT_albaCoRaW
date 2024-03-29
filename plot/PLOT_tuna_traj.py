#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 15:46:03 2021

@author: adupaix

Allows to plot tuna trajectories
Does NOT work on its own
Works after running the simulation, with the parameters of interest
"""

r=0

plot_zoom = False

tuna.load(path_output, r)
tuna.correct_edge(edge_dict)

if environment == "random" or environment == "square":
    FADs.load(path_output)
    FADs.correct_edge(tuna)

fig=plt.figure(1) 
fig, ax = plt.subplots(figsize=(10, 10)) #figsize=(longueur, hauteur)
        #> Plot axis
plt.ylabel('y (km)')
plt.xlabel('x (km)')
plt.title(str(environment)+' '+str(studyYear)+' | $N_{FAD}$='+str(FADs.nFAD))
plt.axis('equal')
for i in range(0, int(FADs.nFAD)):
    fad_circle_oz=plt.Circle((FADs.x[i], FADs.y[i]), TUNA.R0, color='green', fill=False)
    ax.add_patch(fad_circle_oz)
for i in range(0, int(FADs.nFAD)):
    fad_circle_oz=plt.Circle((FADs.x[i], FADs.y[i]), FADs.dr[i], color='red', fill=False)
    ax.add_patch(fad_circle_oz)
        #> Plot FAD
plt.plot(FADs.x[FADs.has_buoy], FADs.y[FADs.has_buoy], 'k+', label='Equiped FAD')
        #> Plot tuna path
for step in np.arange(0, max(tuna.num_steps), H12):
    if step%H24<H12: col="blue"
    else: col = 'red'
    if step==0: step=1
    plt.plot(tuna.x[(tuna.num_steps>=step)&(tuna.num_steps<=(step+H12))&((tuna.x!=0) * (tuna.y!=0))], 
             tuna.y[(tuna.num_steps>=step)&(tuna.num_steps<=(step+H12))&((tuna.x!=0) * (tuna.y!=0))], 
             "-", color=col, alpha=0.6)
            #plt.plot(tunaPath_r[0:(p-1), 0], tunaPath_r[0:(p-1), 1], 'k--', alpha=0.4, label='tuna path')
        #> Plot limit of the env
        # plt.plot(np.array([0,0,L,L,0]), np.array([0,L,L,0,0]), 'k-')
        #> Zoom
if environment!="square" and environment != "maldives" and environment != "random" and len(land_files) > 0:
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
            
if plot_zoom==True and (environment=="square" or environment=="random"):
    dist_one_day = (TUNA.v*3600*24)/1000 #distance parcourue en 1 jour
    interval = dist_one_day*PATH_DURATION/15 #distance parcourue sur l'ensemble du trajet / 15
    # plt.xlim(-10, 20)
    # plt.ylim(20, 50)
    plt.xlim(tuna.x[0]-interval, tuna.x[0]+interval)
    plt.ylim(tuna.y[0]-interval, tuna.y[0]+interval)
elif plot_zoom==True:
    plt.xlim(-10, 20)
    plt.ylim(20, 50)
