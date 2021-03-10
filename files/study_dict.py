#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 12:53:13 2021

@author: adupaix

Dictionnary which contains a list of, for each study:
        the name of the environment
        the year of the study
	the name of the file containing the land coordinates
        a list with the coordinates, in degree, of the "center" of the study
	the limits of the study area (interval around the center), out of which we consider that the tuna got out
"""

study_dict = {10 : ["square","","",[0,0],[0,L]],
              11 : ["hawaii",2005,"hawaii_coor",[-157.9696437226543,21.4646535007218], [-L/2,L/2]],
              12 : ["mauritius",2017, "mauritius_coor", [57.57120757514343,-20.27771560002525], [-L/2,L/2]],
              13 : ["maldives","",["atoll1","atoll2","atoll3","atoll4"], [73.15555555555555, 3.1993055555555543], [-L/2,L/2]],
              14 : ["drifting",2020,"", [55, -2.5], [-10*111,10*111]]}

environment = study_dict[study][0]
studyYear = study_dict[study][1]
land_files = study_dict[study][2]
study_center = study_dict[study][3]
lims = study_dict[study][4]
