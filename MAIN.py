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


#~ Path
path_machine = PATH+'/files' #where the data files are saved
path_script = PATH #where the script are save
#Tu peux aussi creer un fichier .py avec ces deux precedentes lignes de code qui varient
#en fonction de la machine que tu utilises pour ne pas avoir de probleme de chemin
#> exec(open("path.py").read()) #pour executer le code

#~ Change working directory
os.chdir(path_script)
# os.getcwd()

#~ Set seed
if REPRODUCTIBLE == False:
    while SEED == 10:
        SEED = rd.randint(1, 1000)
rd.seed(SEED)
np.random.seed(SEED)


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
exec(open(str(path_machine)+"/study_dict.py").read())

#~ Check the grid size
if environment == "random" or environment == "square":
    if L % DIST_FAD != 0:
        L = round(L/DIST_FAD)*DIST_FAD

## Charge the environment class
if environment == "square":
    exec(open(str(path_script)+"/CLASS_Square_fadArray.py").read())
elif environment == "random":
    exec(open(str(path_script)+"/CLASS_Random_fadArray.py").read())
else:
    exec(open(str(path_script)+"/CLASS_Real_fadArray.py").read())
    exec(open(str(path_script)+"/CLASS_Land.py").read())

#~~~ TUNA
#---------
## Simulation duration in timesteps
Npas = int(abs((PATH_DURATION*24*3600)/STEP_TIME)) # total number of timesteps

## charge the tuna class
# WARNING: STEP_TIME is needed to initialize the TUNA class
exec(open(str(path_script)+"/CLASS_Tuna.py").read())



#%%####################################
#~~~~~ MODEL PARAMETERS ~~~~

#~~~ ENVIRONMENT
#----------------

## Create the environement
if environment == "square" or environment == "random":
    FADs = FAD_Array(L = L, distFAD = DIST_FAD, detection_radius = DR)
elif environment == "maldives":
    FADs = FAD_Array(path = path_machine, environment = environment, studyYear = studyYear, study_center = study_center, detection_radius = DR)
    Island = list()
    for i in range(len(land_files)):
        Island.append( Land(path = path_machine, environment = environment, study_center = study_center, land_file = land_files[i]) )
    sigma_island = 2 # sigma used to get the alpha when go close to land
elif len(land_files) > 0:
    FADs = FAD_Array(path = path_machine, environment = environment, studyYear = studyYear, study_center = study_center, detection_radius = DR)
    Island = Land(path = path_machine, environment = environment, study_center = study_center, land_file = land_files)
    sigma_island = 2 # sigma used to get the alpha when go close to land
else:
    FADs = FAD_Array(path = path_machine, environment = environment, studyYear = studyYear, study_center = study_center, detection_radius = DR)
    
    
#~~~ TUNA
#---------
## Choose FAD of release
## First position -> fad in the middle of the array in case of square array
if environment == "square":
    diag_fad = FADs.id[FADs.x == FADs.y]
    fad_start = diag_fad[int(len(diag_fad)/2)]
# if random array, choose the closest FAD to the center of the study area
elif environment == "random":
    fad_start = FADs.id[np.sqrt((FADs.x - L/2)**2 + (FADs.y - L/2)**2) == min(np.sqrt((FADs.x - L/2)**2 + (FADs.y - L/2)**2))]
elif CHOOSE_FAD_START == True:
    fad_start = None # get the FAD number here so it can be saved in the output folder name
    while fad_start not in FADs.id[FADs.of_release != 0]:
        fad_start = int(input("Choose the FAD of release in one of the following FADs: "+str(FADs.id[FADs.of_release != 0])))


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
if ADD_CRTS == True and environment != "square" and environment != "maldives" and environment != "random":
    crt_file = path_machine+"/CRTnext_YFT0.7_"+environment+str(studyYear)+".txt"
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
if environment == "square" or environment == "random":
    sim_name = environment+"_v"+str(TUNA.v)+"_m"+str(TUNA.m)+"_distFAD"+str(FADs.distFAD)+"_Ro"+str(TUNA.R0)+"_c"+str(TUNA.c)
    if environment == "random":
        sim_name = sim_name+"_seed"+str(SEED)
elif CHOOSE_FAD_START == False:
    sim_name = environment+str(studyYear)+"_v"+str(TUNA.v)+"_m"+str(TUNA.m)+"_Ro"+str(TUNA.R0)+"_c"+str(TUNA.c)
elif CHOOSE_FAD_START == True:
    sim_name = environment+str(studyYear)+"_v"+str(TUNA.v)+"_m"+str(TUNA.m)+"_Ro"+str(TUNA.R0)+"_c"+str(TUNA.c)+"_FAD"+str(fad_start)

sim_name = sim_name+add_to_name

if ADD_CRTS == True:
    sim_name = sim_name+"_withCRT"
if LIMIT_CAT_NB == True:
    sim_name = sim_name+"_"+str(NB_MAX_CAT)+"CATonly"

path_output = str(path_script)+"/modelOutput/"+sim_name
output_folders = ['Path_tuna','CATs']
if environment == "random":
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
if CHECK_MAP == True or environment == "random":
    exec(open(path_script+"/PLOT_checkenv.py").read())

# If the environment is random, save the FADs coordinates
if environment == "random":
    FADs.save()


#~~ RUN THE SIMULATION ~~
# Print information
if environment == "square" or environment == "random":
    print(environment+' | n tunas='+str(NREPLICA)+' | v='+str(TUNA.v)+' m/s | dist='+str(FADs.distFAD)+' km | Ro='+str(TUNA.R0)+' km | sigma='+str(round(TUNA.sigma,3))+' -> c='+str(TUNA.c)+' | Add CRTs = '+str(ADD_CRTS))
else:
    print(environment+' '+str(studyYear)+' | n tunas='+str(NREPLICA)+' | v='+str(TUNA.v)+' m/s | Ro='+str(TUNA.R0)+' km | sigma='+str(round(TUNA.sigma,3))+' -> c='+str(TUNA.c)+' | Add CRTs = '+str(ADD_CRTS))
    

#> Tuna movement
# a. check if the trajectories were already simulated
files_exist = list()
for i in range(NREPLICA):
    files_exist.append(os.path.isfile(str(path_output)+"/Path_tuna/tuna_n"+str(i+1)+"."+output_format[0]))

# b. simulate new trajectories if there are less trajectories saved than NREPLICA
#    or if RESET has been set to True
if sum(files_exist)<NREPLICA or RESET == True:
    begin=list()
    end = list()

    exec(open(str(path_script)+"/MODEL_sim_tuna_path.py").read())

    times = [end[i] - begin[i] for i in range(len(end))]
    time_tot = sum(times)
    
    if VERBOSE == True:
        print("Time for simulating tuna trajectories: "+str(round(time_tot))+"s")

elif VERBOSE == True:
    print("\nUsing existing tuna trajectories")

if VERBOSE == True:
    print("\nTuna trajectories saved in:\n    "+str(path_output)+"/Path_tuna/")


#~~ CALCULATE CAT ~~
exec(open(str(path_script)+"/MODELOUTPUT_CATs.py").read())

if VERBOSE == True:
    print("\nCATs saved in:\n    "+str(path_output)+"/CATs/CATs_array."+output_format[1])

#~~ SAVE SUMMARY ~~

lines = ["Execution time : "+str(time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.localtime())),
     "\n--------------",
     "\n",
     "\nNumber of simulated tunas : "+str(NREPLICA),
     "\nEnvironment type : "+str(environment),
     "\nSeed :"+str(SEED)
     ]
summary = open(str(path_output)+"/Summary.txt", "w")
summary.writelines(lines)
summary.close()



