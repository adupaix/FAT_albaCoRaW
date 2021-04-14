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
PATH = '/home/adupaix/Documents/CRW/CRW_model' # enter the path of the directory where the script are saved

#~ Plots
CHECK_MAP = False
PLOT_TUNAPATH = False # deprecated, better to leave False. Instead, use PLOT_tuna_traj.py after the simulation has run
PLOT_ZOOM = False

#~ Wether to recalculate existing tuna trajectories
RESET = True
# If RESET == True, calculate tuna trajectories in any case.
# if RESET == False, calculate new tuna trajectories only if less replica are saved (in "path_output/Path_tuna") than asked (in Nreplica)

#~ Choose a random seed (False) or set the seed to that the simulation is reproductible
REPRODUCTIBLE = True

## Choose output format
# the first element is the output format of the tuna trajectories
# the second is the format of the array containing CATs
### For both, output is ALWAYS saved in npy, and will ALSO be saved in csv if ouput_format == "csv"
OUTPUT_FORMAT = ["npy","csv"]

#~ Add CRTs when reach a FAD
ADD_CRTS = False

#~ Consider the whole simulation time (LIMIT_CAT_NB = False) or only until a certain number of CATs (True)
# if True choose the number of CATs (NB_MAX_CAT)
# !! If LIMIT_CAT_NB is True, even if the NB_MAX_CAT is not reached, the simulation will not be longer than the PATH_DURATION
LIMIT_CAT_NB = True
NB_MAX_CAT = 1

#%%####################################
#~~~ Environement parameters ~~

"""
Environments:
    
    - square array = 10
    - hawaii 2005 = 11 
    - Mauritius 2017 = 12 
    - Maldives = 13
    - Maldives 2018 = 15
    - Maldives 2018 without Huvadhoo atoll = 16
    - Maldives 2009 = 17
"""
#~ Study number
STUDY = 10

#~ Characteristics of the FAD array
DIST_FAD = 20 #Distance between FADs, in km
L = 5000 #Width of the environment, in km
DR = 0.5 #Detection radius of FADs, in km


#%%####################################
#~~~ Simulation parameters ~~

#~ Number of tunas to simulate
NREPLICA = 1000

#~ Maximum duration of a tuna path
PATH_DURATION = 120 # in days

#~ Time step
STEP_TIME = 100 # in seconds

#~ Wether to choose the FAD of release or not
CHOOSE_RELEASE_FAD = True

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
