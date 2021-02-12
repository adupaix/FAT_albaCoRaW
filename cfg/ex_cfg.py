#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 10:44:32 2021

Config file to launch the model

@author: adupaix
"""

#%%####################################
#~~~ General Parameters ~~

#~ Path were the scripts are
PATH = '/home/adupaix/Documents/CRW/CRW_model_modif' # where the script are saved

#~ Plots
CHECK_MAP = False
PLOT_TUNAPATH = False
PLOT_ZOOM = False

#~ Wether to recalculate existing tuna trajectories
RESET = True
# If RESET == True, calculate tuna trajectories in any case.
# if RESET == False, calculate new tuna trajectories only if less replica are saved (in "path_output/Path_tuna") than asked (in Nreplica)

#~ Not used yet
ADD_CRTS = False

#%%####################################
#~~~ Environement parameters ~~

"""
Environments:
    
    - square array = 10
    - hawaii 2005 = 11 
    - Mauritius 2017 = 12 
    - Maldives = 13
"""
#~ Study number
STUDY = 10

#~ Characteristics of the FAD array
DIST_FAD = 100 #Distance between FADs, in km
L = 5000 #Width of the environment, in km
DR = 0.5 #Detection radius of FADs, in km


#%%####################################
#~~~ Simulation parameters ~~

#~ Number of tunas to simulate
NREPLICA = 300

#~ Maximum duration of a tuna path
PATH_DURATION = 120 # in days

#~ Time step
STEP_TIME = 100 # in seconds

#%%####################################
#~~~ Individual tuna characteristics ~~

#~ Orientation radius
R0 = 5 #in km

#~ Speed
V = 0.7 #in m/s

#~ Sinuosity
C = 0.99

#~ Mortality
M = 0 #in %/day


#%%####################################
#~~~ Launch the study ~~

exec(open(PATH+"/MAIN.py").read())
 
 
#%%####################################