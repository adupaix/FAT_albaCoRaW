#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 15:46:03 2021

@author: adupaix

Permet de tracer les trajectoires des thons.
Ne fonctionne pas seul
Fonctionne après avoir fait tourné le MAIN, avec les parametres d'interet
"""

r=8

tunaPath_array = np.load(os.path.join(path_output,"Path_tuna","tuna_n"+str(r+1)+".npy"))

fig=plt.figure(1) 
fig, ax = plt.subplots(figsize=(10, 10)) #figsize=(longueur, hauteur)
        #> Plot axis
plt.ylabel('y (km)')
plt.xlabel('x (km)')
plt.title(str(environment)+' '+str(studyYear)+' | $N_{FAD}$='+str(FADs.nFAD))
plt.axis('equal')
for i in range(0, int(FADs.nFAD)):
    fad_circle_oz=plt.Circle((FADs.x[i], FADs.y[i]), Tuna.R0, color='green', fill=False)
    ax.add_patch(fad_circle_oz)
        #> Plot FAD
plt.plot(FADs.x[FADs.has_buoy], FADs.y[FADs.has_buoy], 'k+', label='Equiped FAD')
        #> Plot tuna path
for step in np.arange(0, max(tunaPath_array[:,4]), H12):
    if step%H24<H12: col="blue"
    else: col = 'red'
    if step==0: step=1
    plt.plot(tunaPath_array[(tunaPath_array[:,4]>=step)&(tunaPath_array[:,4]<=(step+H12))&(tunaPath_array[:,0]!=0),0], 
             tunaPath_array[(tunaPath_array[:,4]>=step)&(tunaPath_array[:,4]<=(step+H12))&(tunaPath_array[:,0]!=0),1], 
             "-", color=col, alpha=0.6)
            #plt.plot(tunaPath_r[0:(p-1), 0], tunaPath_r[0:(p-1), 1], 'k--', alpha=0.4, label='tuna path')
        #> Plot limit of the env
        # plt.plot(np.array([0,0,L,L,0]), np.array([0,L,L,0,0]), 'k-')
        #> Zoom
if environment!="square" and environment != "maldives":
    for i in range(len(Island.x)):
        plt.plot(Island.x[i:i+2],
                 Island.y[i:i+2],
                 "-", color = "black")
if plot_zoom==True and environment=="square":
    dist_one_day = (tuna.v*3600*24)/1000 #distance parcourue en 1 jour
    interval = dist_one_day*path_duration/15 #distance parcourue sur l'ensemble du trajet / 15
    plt.xlim(1580, 1600)
    plt.ylim(2780, 2820)
    # plt.xlim(tuna.x[0]-interval, tuna.x[0]+interval)
    # plt.ylim(tuna.y[0]-interval, tuna.y[0]+interval)