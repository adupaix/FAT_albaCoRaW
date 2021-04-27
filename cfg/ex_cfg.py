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

#~ Wether to recalculate existing tuna trajectories
RESET = True
# If RESET == True, calculate tuna trajectories in any case.
# if RESET == False, calculate new tuna trajectories only if less replica are saved (in "path_output/Path_tuna") than asked (in Nreplica)

#~ Choose a random seed (False) or set the seed to that the simulation is reproductible
# !! if the SEED is set at another value than 10, the REPRODUCTIBLE argument is overriden and the seed will be set to the given value
REPRODUCTIBLE = True
SEED = 10

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
LIMIT_CAT_NB = False
NB_MAX_CAT = 1

#~ Wether to print verbose when the script is running
VERBOSE = True

#~ Wether to go back in time or not when the tuna does a CATreturn < 24h
TIME_MACHINE = True

#~ When a tuna leaves a FAD, does a simple Random Walk (True) or a Correlated Random Walk (False)
SRW_WHEN_DEPART = False

#%%####################################
#~~~ Environement parameters ~~

"""
Environments:
    
    - square array = 1
    - Hawaii 2005 = 2
    - Mauritius 2017 = 3
    - Maldives 2018 = 4
    - Maldives 2018 without Huvadhoo atoll = 5
    - Maldives 2009 = 6
"""
#~ Study number
STUDY = 2

#~ Characteristics of the FAD array
DIST_FAD = 25 #Distance between FADs, in km
L = 5000 #Width of the environment, in km
DR = 0.5 #Detection radius of FADs, in km


#%%####################################
#~~~ Simulation parameters ~~

#~ Number of tunas to simulate
NREPLICA = 10

#~ Maximum duration of a tuna path
PATH_DURATION = 20 # in days

#~ Time step
STEP_TIME = 100 # in seconds

#~ Wether to choose the FAD of release or not
CHOOSE_FAD_START = False

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
