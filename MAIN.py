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
rd.seed(10)


#%%####################################
#~~~~ CHARGE CLASSES ~~~~
"""
Environments:
    
    - square array = 10
    - hawaii 2005 = 11 
    - Mauritius 2017 = 12 
    - Maldives = 13
"""

#~~~ ENVIRONMENT
#----------------
## Choose environment characteristics
study = STUDY


distFAD = DIST_FAD #Distance between FADs, in km
L = L #Width of the environment, in km
dr = DR #Detection radius of FADs, in km

first_FAD_only = FIRST_FAD_ONLY # wether to stop the simulation avec the first encountered FAD or not

# get the following variables:
    # environment
    # studyYear
    # land_files (names of the files containing the coordinates of the island(s))
    # study_center (doesn't apply for square, coordinates of the centroid of the island for real envs)
    # lims (limites of the environment: 0;L if square, -L/2;L/2 if real envs)
# WARNING: L is needed to charge the study dictionnary
exec(open(str(path_machine)+"/study_dict.py").read())



## Charge the environment class
if environment == "square":
    exec(open(str(path_script)+"/CLASS_Square_fadArray.py").read())
else:
    exec(open(str(path_script)+"/CLASS_Real_fadArray.py").read())
    exec(open(str(path_script)+"/CLASS_Land.py").read())

## Wether to check environment with plot
checkMap = CHECK_MAP


#~~~ TUNA
#---------
## Simulation duration
path_duration = PATH_DURATION # in days
step_time= STEP_TIME # second ~ 1.66 min

Npas = int(abs((path_duration*24*3600)/step_time)) # total number of timesteps

## charge the tuna class
# WARNING: step_time is needed to initialize the Tuna class
exec(open(str(path_script)+"/CLASS_Tuna.py").read())



#%%####################################
#~~~~~ MODEL PARAMETERS ~~~~

# model = 22 #day/night model (DN) NE SERT PLUS, A REMETTRE

#~~~ ENVIRONMENT
#----------------

## Create the environement
if environment == "square":
    FADs = FAD_Array(L = L, distFAD = distFAD, detection_radius = dr)
elif environment == "maldives":
    FADs = FAD_Array(path = path_machine, environment = environment, studyYear = studyYear, study_center = study_center)
    Island = list()
    for i in range(len(land_files)):
        Island.append( Land(path = path_machine, environment = environment, study_center = study_center, land_file = land_files[i]) )
    sigma_island = 2 # sigma used to get the alpha when go close to land
else:
    FADs = FAD_Array(path = path_machine, environment = environment, studyYear = studyYear, study_center = study_center)
    Island = Land(path = path_machine, environment = environment, study_center = study_center, land_file = land_files)
    sigma_island = 2 # sigma used to get the alpha when go close to land
    
    
#~~~ TUNA
#---------
## Number of tunas to be simulated
Nreplica=NREPLICA

## Orientation radius
Tuna.R0 = R0

## Speed
Tuna.v = V
#~~ Distance covered by a tuna at each time step
Tuna.l = (Tuna.v*step_time)/1000

## Modulo for change of behavior each 12 hours
H12 = round((0.5*24*3600)/step_time)
H24 = round((1*24*3600)/step_time)

### Rmq: methods are used to change c and m, to change sigma and the mortality rate per time step at the same time
## Sinuosity
c = C # sinuosity coefficient
Tuna.change_c(c)

crw = True
if C == 1:
    crw = False

## Mortality rate
m = M  # mortality in %/day
Tuna.change_m(m)

##Plot
plot_tunaPath = PLOT_TUNAPATH
plot_zoom = PLOT_ZOOM

# If RESET == True, calculate tuna trajectories in any case.
# if RESET == False, calculate new tuna trajectories only if less replica are saved (in "path_output/Path_tuna") than asked (in Nreplica)
RESET = RESET

## Add CRT when tuna associates with a FAD
addCRTs = ADD_CRTS ## POUR LE MOMENT PAS MIS EN PLACE 

#~~~ OUTPUTS
# ----------

# Generate output folders
if environment == "square":
    sim_name = environment+"_v"+str(Tuna.v)+"_m"+str(Tuna.m)+"_distFAD"+str(FADs.distFAD)+"_Ro"+str(Tuna.R0)+"_c"+str(Tuna.c)
else:
    sim_name = environment+str(studyYear)+"_v"+str(Tuna.v)+"_m"+str(Tuna.m)+"_Ro"+str(Tuna.R0)+"_c"+str(Tuna.c)

path_output = str(path_script)+"/modelOutput/"+sim_name
output_folders = ['Path_tuna','CATs']
for folder in output_folders:
    os.makedirs(os.path.join(path_output,folder), exist_ok=True)
    
## Choose output format
# the first element is the output format of the tuna trajectories
# the second is the format of the array containing CATs
### For both, output is ALWAYS saved in npy, and will ALSO be saved in csv if ouput_format == "csv"
output_format = ["npy","csv"]


#%%####################################
#~~~~~ SIMULATION ~~~~

#~~ RUN THE ENVIRONMENT ~~
if checkMap == True:
    exec(open(path_script+"/PLOT_checkenv.py").read())  


#~~ RUN THE SIMULATION ~~
# Print information
if environment == "square":
    print(environment+' | n tunas='+str(Nreplica)+' | v='+str(Tuna.v)+' m/s | dist='+str(FADs.distFAD)+' km | Ro='+str(Tuna.R0)+' km | sigma='+str(round(Tuna.sigma,3))+' -> c='+str(Tuna.c))
else:
    print(environment+' '+str(studyYear)+' | n tunas='+str(Nreplica)+' | v='+str(Tuna.v)+' m/s | Ro='+str(Tuna.R0)+' km | sigma='+str(round(Tuna.sigma,3))+' -> c='+str(Tuna.c))
    

#> Tuna movement
# a. check if the trajectories were already simulated
files_exist = list()
for i in range(Nreplica):
    files_exist.append(os.path.isfile(str(path_output)+"/Path_tuna/tuna_n"+str(i+1)+"."+output_format[0]))

# b. simulate new trajectories if there are less trajectories saved than Nreplica
#    or if RESET has been set to True
if sum(files_exist)<Nreplica or RESET == True:
    begin=list()
    end = list()

    exec(open(str(path_script)+"/MODEL_sim_tuna_path.py").read())

    times = [end[i] - begin[i] for i in range(len(end))]
    time_tot = sum(times)

    print("Time for simulating tuna trajectories: "+str(round(time_tot))+"s")

else:
    print("\nUsing existing tuna trajectories")

print("\nTuna trajectories saved in:\n    "+str(path_output)+"/Path_tuna/")
#> Loss simulation
# m = m_array[0]
# exec(open(str(path_script)+"/MODEL_mortalityRateSimulation.py").read())

#~~ CALCULATE CAT ~~
exec(open(str(path_script)+"/MODELOUTPUT_CATs.py").read())

print("\nCATs saved in:\n    "+str(path_output)+"/CATs/CATs_array."+output_format[1])


