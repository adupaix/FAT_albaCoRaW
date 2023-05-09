#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  6 13:08:06 2022

Several tests on argument values and types before launching the model

@author: adupaix
"""

#%%####################################
#~~~ Check types ~~
arg_list = ['PATH','CHECK_MAP',"RESET","REPRODUCTIBLE","SEED","OUTPUT_FORMAT","ADD_CRTS",
            "LEAVE_AT_DR","LIMIT_CAT_NB","NB_MAX_CAT","VERBOSE","TIME_MACHINE","SRW_WHEN_DEPART",
            "STUDY", "DIST_FAD", "L", "DR","NREPLICA","PATH_DURATION","STEP_TIME",
            "CHOOSE_FAD_START", "F_TO_PICK_FAD_START","R0","V","C","M"]

expected_type = [str, bool, bool, bool, int, list, bool,
                 bool, bool, int, bool, bool, bool,
                 int, int, int, float, int, int, int,
                 bool, str, int, float, float, int]

for i in range(len(arg_list)):
    if type(eval(arg_list[i])) != expected_type[i]:
        raise Exception("Wrong argument type: "+arg_list[i])

#%%####################################
#~~~ General Parameters ~~

#~ Specified output format
if OUTPUT_FORMAT[0] not in ['npy', 'csv', None] or OUTPUT_FORMAT[1] not in ['npy', 'csv']:
    raise Exception("Specified output formats (OUTPUT_FORMAT) are not compatible. Please see comments in ex_cfg.py")

#~ Consider the whole simulation time (LIMIT_CAT_NB = False) or only until a certain number of CATs (True)
# if True choose the number of CATs (NB_MAX_CAT)
# !! If LIMIT_CAT_NB is True, even if the NB_MAX_CAT is not reached, the simulation will not be longer than the PATH_DURATION
if NB_MAX_CAT < 1:
    raise Exception("Maximum number of CATs (NB_MAX_CAT) specified is too low")


#%%####################################
#~~~ Environement parameters ~~

"""
Environments:
    
    - square array = 1
    - Hawaii 2005 =  2
    - Hawaii 2005 without land = 3
    - Mauritius 2017 = 4
    - Maldives 2017 = 5
    - Maldives 2018 = 6
    - Maldives 2018 without Huvadhoo atoll = 7
    - Maldives 2009 = 8
    - random array = 9
    - randomized square array = 10
"""
#~ Study number
if STUDY not in range(11):
    raise Exception("Specified study number (STUDY) is not compatible. Please see comments in ex_cfg.py")

#~ Characteristics of the FAD array - Apply to square and randomized square arrays
if DIST_FAD <= 0 or L <= 0 or DR <= 0:
    raise Exception("Please check one of the following arguments: DIST_FAD, L, DR. Only positive values are accepted")
if L <= DIST_FAD:
    raise Exception("L must be larger than the mean interFAD distance (DIST_FAD)")


#%%####################################
#~~~ Simulation parameters ~~

#~ Number of tunas to simulate
if NREPLICA  <= 0 or PATH_DURATION <= 0 or STEP_TIME <= 0:
    raise Exception("Please check one of the following arguments: NREPLICA, PATH_DURATION, STEP_TIME. Only positive values are accepted")


#~ If the FAD of release if picked randomly (CHOOSE_FAD_START = False), choose the function used among:
#  "uniform": the probability to pick a FAD is uniformly distributed among the FADs where release occured in the experiment
#  "asData": the probability to pick a FAD is proportional with the number of tuna released at that FAD in the experiment
# Apply to real arrays
if F_TO_PICK_FAD_START not in ['uniforme', 'asData']:
    raise Exception("Specified functions to pick departue FAD (F_TO_PICK_FAD_START) are not compatible. Please see comments in ex_cfg.py")

#%%####################################
#~~~ Individual tuna characteristics ~~

#~ Orientation radius
if R0 < 0:
    raise Exception("Orientation radius (R0) must positive or null.")

#~ Speed
if V <= 0:
    raise Exception("Speed (V) must positive.")

#~ Sinuosity
if C < 0 or C > 1:
    raise Exception("Sinuosity coefficient (C) must be between 0 and 1.")

#~ Mortality
if M < 0 or M > 100:
    raise Exception("Mortality (M) must be expressed in percentage.")
