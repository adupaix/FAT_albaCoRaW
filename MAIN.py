#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 11:36:40 2018
@author: geraldine

Modified on Fri Feb 05 2021, by adupaix
"""


#%%#########################################
#~~~ OPEN PACKAGEs & FUNCTIONs & PATH ~~~

#~ To run the model
import numpy as np
import pylab as plt #~ Allow to easily use python package matplotlib and numpy // Directely access the matplotlib and numpy package
import scipy.stats as stats
from scipy.stats import truncnorm
# from scipy.stats import norm
import random as rd
import math
import os as os
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import shapely.geometry as geom
from shapely.geometry.polygon import LinearRing
from descartes import PolygonPatch
import time
import csv as csv
import re

#~ Path
path_files = PATH+'/files' #where the data files are saved
path_class = PATH+'/classes' # where the classes are saved
path_model = PATH+'/model' # where the two routines (run model & calculate CATs) are saved
path_plot = PATH+'/plot' # where the scripts for plots are saved
path_cfg = PATH+'/cfg' # where the cfg files are saved

#~ Change working directory
os.chdir(PATH)
# os.getcwd()

#~ Set seed
if REPRODUCTIBLE == False:
    while SEED == 10:
        SEED = rd.randint(1, 10**8)
rd.seed(SEED)
np.random.seed(SEED)

#~ Tests
if OUTPUT_FORMAT[0] not in ['npy', 'csv', None] or OUTPUT_FORMAT[1] not in ['npy', 'csv']:
    raise Exception("Specified output formats are not compatible. Please see comments in ex_cfg.py")


#%%####################################
#~~~~ CHARGE CLASSES ~~~~
"""
Environments:
    
    - square array = 1
    - Hawaii 2005 = 2
    - Hawaii 2005 without land = 3
    - Mauritius 2017 = 4
    - Maldives 2017 = 5
    - Maldives 2018 = 6
    - Maldives 2018 without Huvadhoo atoll = 7
    - Maldives 2009 = 8
    - random array = 9
    - randomized square array = 10
"""

#~~~ ENVIRONMENT
#----------------

# get the following variables:
    # environment
    # studyYear
    # land_files (names of the files containing the coordinates of the island(s))
    # study_center (doesn't apply for square, coordinates of the centroid of the island for real envs)
    # lims (limites of the environment: 0;L if square, -L/2;L/2 if real envs)
# WARNING: L is needed to charge the study dictionnary
exec(open(str(path_files)+"/study_dict.py").read())

#~ Check the grid size
if environment in ["random", "square", "square_rd"]:
    if L % DIST_FAD != 0:
        L = round(L/DIST_FAD)*DIST_FAD

## Charge the environment class
if environment in ["random", "square", "square_rd"]:
    exec(open(str(path_class)+"/CLASS_Theoretical_fadArray.py").read())
else:
    exec(open(str(path_class)+"/CLASS_Real_fadArray.py").read())
    exec(open(str(path_class)+"/CLASS_Land.py").read())

#~~~ TUNA
#---------
## Simulation duration in timesteps
Npas = int(abs((PATH_DURATION*24*3600)/STEP_TIME)) # total number of timesteps

## charge the tuna class
# WARNING: STEP_TIME is needed to initialize the TUNA class
exec(open(str(path_class)+"/CLASS_Tuna.py").read())

#~~~ LOG
#---------
exec(open(str(path_class)+"/CLASS_Log.py").read())
# initialize the log
log = Log(path = path_cfg,
          fname = os.path.basename(__file__),
          seed = SEED,
          nreplica = NREPLICA,
          environment = STUDY)
# fill-in the log
log.fill()



#%%####################################
#~~~~~ MODEL PARAMETERS ~~~~

#~~~ ENVIRONMENT
#----------------

## Create the environement
if environment in ["random", "square", "square_rd"]:
    FADs = FAD_Array(environment = environment, L = L, distFAD = DIST_FAD, R0 = R0, detection_radius = DR)
elif environment == "maldives":
    FADs = FAD_Array(path = path_files, environment = environment, studyYear = studyYear, study_center = study_center, detection_radius = DR)
    Island = list()
    for i in range(len(land_files)):
        Island.append( Land(path = path_files, environment = environment, study_center = study_center, land_file = land_files[i]) )
    sigma_island = 2 # sigma used to get the alpha when go close to land
elif len(land_files) > 0:
    FADs = FAD_Array(path = path_files, environment = environment, studyYear = studyYear, study_center = study_center, detection_radius = DR)
    Island = Land(path = path_files, environment = environment, study_center = study_center, land_file = land_files)
    sigma_island = 2 # sigma used to get the alpha when go close to land
else:
    FADs = FAD_Array(path = path_files, environment = environment, studyYear = studyYear, study_center = study_center, detection_radius = DR)
    
    
#~~~ TUNA
#---------
## Choose FAD of release
## First position -> fad in the middle of the array in case of square array
if environment == "square":
    diag_fad = FADs.id[FADs.x == FADs.y]
    fad_start = diag_fad[int(len(diag_fad)/2)]
    fad_start = np.repeat(fad_start, repeats=NREPLICA)
# If random array, choose a FAD randomly in the array
elif environment in ["random","square_rd"]:
    fad_start = np.random.choice(FADs.id, size=NREPLICA)
# If we ask for the fad start
elif CHOOSE_FAD_START == True:
    fad_start = None # get the FAD number here so it can be saved in the output folder name
    while fad_start not in FADs.id[FADs.of_release != 0]:
        fad_start = int(input("Choose the FAD of release in one of the following FADs: "+str(FADs.id[FADs.of_release != 0])))
    fad_start = np.repeat(fad_start, repeats=NREPLICA)
# If real array and choose_fad_start is False, FAD chosen randomly among FADs used for actual experimental release
else:
    # chosen with uniform distribution among the FADs where release occured
    if F_TO_PICK_FAD_START == "uniform":
        fad_start = np.random.choice(FADs.id[FADs.of_release != 0], size=NREPLICA)
    # or respect the actual proportions in the experiment
    elif F_TO_PICK_FAD_START == "asData":
        fad_start = np.random.choice(FADs.id, NREPLICA, p=[i/sum(FADs.of_release) for i in FADs.of_release])


## Orientation radius
TUNA.R0 = R0

## Speed
TUNA.v = V
#~~ Distance covered by a tuna at each time step
TUNA.l = (TUNA.v*STEP_TIME)/1000

## Modulo for change of behavior each 12 hours
H12 = round((0.5*24*3600)/STEP_TIME)
H24 = round((1*24*3600)/STEP_TIME)

### Rmq: methods are used to change c and m, to change sigma and the mortality rate per time step at the same time
## Sinuosity
TUNA.change_c(C)

crw = True
if C == 1:
    crw = False

## Mortality rate in %/day
TUNA.change_m(M)

#~~~ SIMULATION
#---------
## Add CRT when tuna associates with a FAD
CRTs = [0]
if ADD_CRTS == True and environment not in ["square","maldives","random","square_rd"]:
    crt_file = path_files+"/CRTnext_YFT0.7_"+environment+str(studyYear)+".txt"
    with open(crt_file) as f:
        lines = f.readlines()
    # enleve (dr/TUNA.l)*STEP_TIME/(3600*24)) aux valeurs de CRT car c'est environ le temps que les thons vont mettre a ressortir du detection radius
    CRTs = [(float(line.split()[0])) for line in lines]
else:
    ADD_CRTS = False
    
## Limit the simulation to a certain number of CATs
# if does not limit, limit to infinity
# else, does not change NB_MAX_CAT
if LIMIT_CAT_NB == False:
    NB_MAX_CAT = math.inf

#~~~ OUTPUTS
# ----------

# Generate output folders
if environment in ["square", "random", "square_rd"]:
    sim_name = environment+"_v"+str(TUNA.v)+"_m"+str(TUNA.m)+"_distFAD"+str(FADs.distFAD)+"_Ro"+str(TUNA.R0)+"_c"+str(TUNA.c)+"_seed"+str(SEED)
elif CHOOSE_FAD_START == False:
    sim_name = environment+str(studyYear)+"_v"+str(TUNA.v)+"_m"+str(TUNA.m)+"_Ro"+str(TUNA.R0)+"_c"+str(TUNA.c)
elif CHOOSE_FAD_START == True:
    sim_name = environment+str(studyYear)+"_v"+str(TUNA.v)+"_m"+str(TUNA.m)+"_Ro"+str(TUNA.R0)+"_c"+str(TUNA.c)+"_FAD"+str(fad_start)

sim_name = sim_name+add_to_name

if ADD_CRTS == True:
    sim_name = sim_name+"_withCRT"
if LIMIT_CAT_NB == True:
    sim_name = sim_name+"_"+str(NB_MAX_CAT)+"CATonly"

path_output = str(PATH)+"/modelOutput/"+sim_name
output_folders = ['Path_tuna','CATs']
if environment in ["random","square","square_rd"]:
    output_folders.append('FAD_array')
for folder in output_folders:
    os.makedirs(os.path.join(path_output,folder), exist_ok=True)
    
## Choose output format
# the first element is the output format of the tuna trajectories
# the second is the format of the array containing CATs
### For both, output is ALWAYS saved in npy, and will ALSO be saved in csv if ouput_format == "csv"
output_format = OUTPUT_FORMAT


#%%####################################
#~~~~~ SIMULATION ~~~~

#~~ RUN THE ENVIRONMENT ~~
# Plot the environment (and save an image if environment is random)
if CHECK_MAP == True or environment in ["square","random","square_rd"]:
    exec(open(path_plot+"/PLOT_checkenv.py").read())

# If the environment is square or random, save the FADs coordinates
if environment in ["random","square","square_rd"]:
    FADs.save()


#~~ RUN THE SIMULATION ~~
# Print information
if environment in ["square","random","square_rd"]:
    print(environment+' | n tunas='+str(NREPLICA)+' | v='+str(TUNA.v)+' m/s | dist='+str(FADs.distFAD)+' km | Ro='+str(TUNA.R0)+' km | sigma='+str(round(TUNA.sigma,3))+' -> c='+str(TUNA.c)+' | Add CRTs = '+str(ADD_CRTS))
else:
    print(environment+' '+str(studyYear)+' | n tunas='+str(NREPLICA)+' | v='+str(TUNA.v)+' m/s | Ro='+str(TUNA.R0)+' km | sigma='+str(round(TUNA.sigma,3))+' -> c='+str(TUNA.c)+' | Add CRTs = '+str(ADD_CRTS))
    

#> Tuna movement
# a. check if the trajectories were already simulated
files_exist = list()
for i in range(NREPLICA):
    if output_format[0] is None:
        extention = "npy"
    else:
        extention = output_format[0]
    files_exist.append(os.path.isfile(str(path_output)+"/Path_tuna/tuna_n"+str(i+1)+"."+extention))

# b. simulate new trajectories if there are less trajectories saved than NREPLICA
#    or if RESET has been set to True
if sum(files_exist)<NREPLICA or RESET == True:
    begin=list()
    end = list()

    exec(open(str(path_model)+"/MODEL_sim_tuna_path.py").read())

    times = [end[i] - begin[i] for i in range(len(end))]
    time_tot = sum(times)
    
    if VERBOSE == True:
        print("Time for simulating tuna trajectories: "+str(round(time_tot))+"s")

elif VERBOSE == True:
    print("\nUsing existing tuna trajectories")

if VERBOSE == True:
    print("\nTuna trajectories saved in:\n    "+str(path_output)+"/Path_tuna/")


#~~ CALCULATE CAT ~~
exec(open(str(path_model)+"/MODELOUTPUT_CATs.py").read())

if VERBOSE == True:
    print("\nCATs saved in:\n    "+str(path_output)+"/CATs/CATs_array."+output_format[1])


#~~ SAVE SUMMARY ~~
log.save(path_output)



