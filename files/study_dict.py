#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 12:53:13 2021

@author: adupaix

Dictionnary which contains a list of, for each study:
        the name of the environment
        the year of the study
        the name or the list of the names of the files containing the land data
        a list with the coordinates, in degree, of the "center" of the study
        the interval around the center of the study
        a possible str to add to the name of the simulation
        
Also load a reference dictionnary for the condition at the edge
"""

study_dict = {1 : ["square","","",[0,0],[0,L],""],
              2 : ["hawaii",2005,"hawaii_coor",[-157.9696437226543,21.4646535007218], [-L/2,L/2],""],
              3 : ["hawaii",2005,"",[-157.9696437226543,21.4646535007218], [-L/2,L/2],"_no_land"],
              4 : ["mauritius",2017, "mauritius_coor", [57.57120757514343,-20.27771560002525], [-L/2,L/2],""],
              5 : ["maldives",2017,["atoll1","atoll2","atoll3", "atoll4"], [73.19073, 2.979273], [-L/2,L/2],""],
              6 : ["maldives",2018,["atoll1","atoll2","atoll3", "atoll4"], [73.19073, 2.979273], [-L/2,L/2],""],
              7 : ["maldives",2018,["atoll1","atoll3", "atoll4"], [73.19073, 2.979273], [-L/2,L/2],"_no_huva"],
              8 : ["maldives",2009,["atoll1", "atoll2", "atoll3", "atoll4"], [73.21022, 3.063778], [-L/2,L/2],""],
              9 : ["random","","",[0,0],[0,L],""],
              10: ["square_rd","","",[0,0],[0,L],""]}

environment = study_dict[STUDY][0]
studyYear = study_dict[STUDY][1]
land_files = study_dict[STUDY][2]
study_center = study_dict[STUDY][3]
lims = study_dict[STUDY][4]
add_to_name = study_dict[STUDY][5]

# reference to know which number in edge corresponds to which transformation of the FADs coordinates
edge_dict = {1:[-L,0],2:[0,L],3:[L,0],4:[0,-L]}
