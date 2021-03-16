#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 12:53:13 2021

@author: adupaix

Dictionnary which contains a list of, for each study:
        the name of the environment
        the year of the study
        a list with the coordinates, in degree, of the "center" of the study
"""

study_dict = {10 : ["square","","",[0,0],[0,L]],
              11 : ["hawaii",2005,"hawaii_coor",[-157.9696437226543,21.4646535007218], [-L/2,L/2]],
              12 : ["mauritius",2017, "mauritius_coor", [57.57120757514343,-20.27771560002525], [-L/2,L/2]],
              13 : ["maldives","",["atoll1","atoll2","atoll3","atoll4"], [73.15555555555555, 3.1993055555555543], [-L/2,L/2]],
              15 : ["maldives",2018,["atoll1","atoll2","atoll3", "atoll4"], [73.25238, 0.3766667], [-L/2,L/2]]}

environment = study_dict[study][0]
studyYear = study_dict[study][1]
land_files = study_dict[study][2]
study_center = study_dict[study][3]
lims = study_dict[study][4]
