#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 11:20:40 2021

Definition of the class used to create real arrays of FADs

@author: adupaix
"""

class FAD_Array:
    """
    Class with contains an array of FADs, each FAD characterized by :
        - an id (1D array, with numbers from 1 to Nfad)
        - coordinates (two 1D arrays, one with x one with y)
        - presence of not of an acoustic receiver
        """
 
    
    def __init__(self, path, environment, studyYear, study_center, detection_radius = 0.5):
        """
        Takes as inputs:
            - the environment name (hawaii, maldive or maurice)
            - the year of the study
            - the detection radius
                
            And generates a FAD array containing:
                - two 1D arrays with FAD coordinates (x et y, in a reference frame in km, centered on the center of gravity of the array)
                - two 1D arrays with FAD coordinates in degrees (x_deg, y_deg)
                - one 1D array with FAD identification numbers (id)
                - one 1D array with boleens, to know if the FAD is equipped with a receiver (has_buoy)
                - dr: 1D array containing the detection radius for each FAD (0 if no receiver, radius in km if the FAD is equipped)
                - nFAD: number of FADs in the array
                - frac: fraction of equipped FADs
                
        """
        
        convKmDeg = 111 #1° = 111 km
        
        fr = open(str(path)+"/FAD_coor_"+str(environment)+str(studyYear)+".csv")
        
        self.env = environment
        self.year = studyYear
        
        #create empty lists
        self.x_deg = []
        self.y_deg = []
        self.has_buoy = []
        self.of_release = []
        self.id = []
        if environment == "maldives":
            self.lost = []
            self.deployed = []
        
        for d in csv.DictReader(fr):
            #print(i)
            self.x_deg.append(float(d['lon']))
            self.y_deg.append(float(d['lat']))
            self.has_buoy.append(float(d['buoy']))
            self.of_release.append(float(d['released']))
            self.id.append(float(d['NumFAD']))
            if environment == "maldives" and studyYear == "":
                self.lost.append(float(d['lost']))
                self.deployed.append(d['Deployed'])
        
        ## change to arrays
        self.x_deg = np.array(self.x_deg)
        self.y_deg = np.array(self.y_deg)
        self.has_buoy = np.array(self.has_buoy)
        self.of_release = np.array(self.of_release)
        self.id = np.array(self.id)
        if environment == "maldives":
            self.lost = np.array(self.lost)

        self.x = (self.x_deg - np.repeat(study_center[0], len(self.x_deg))) * convKmDeg
        self.y = (self.y_deg - np.repeat(study_center[1], len(self.y_deg))) * convKmDeg
        
        self.has_buoy = self.has_buoy > 0
        self.dr = self.has_buoy * detection_radius # detection radius in km
        
        self.nFAD = len(self.x) # number of FADs in the array
        self.frac = sum(self.has_buoy)/len(self.has_buoy) # fraction of FADs that are equipped with a buoy
        
        fr.close()
        
    
    def change_dr(self, new_dr):
        """
        Method to change the detection radius (dr)
        Takes as input either a unique float (a), either a 1D array of length nFAD (b)
        (a): all the equipped receivers' dr take the given value
        (b): FAD i takes the value i of the given array
        """
        if type(new_dr) is float:
            self.dr = self.has_buoy * new_dr
        elif (type(new_dr) is np.ndarray) and len(new_dr)==len(self.dr):
            self.dr = new_dr
        else:
            print("Warning: Wrong type or length of the given new_dr. Detection radius was not changed !")
    
    def distance_matrix(self):
        """
        Calculate the distance matrix between
        all the FADs in the array
        """
        x_line = np.repeat(self.x, self.nFAD).reshape(self.nFAD,self.nFAD)
        x_col = x_line.transpose()

        y_line = np.repeat(self.y, self.nFAD).reshape(self.nFAD,self.nFAD)
        y_col = y_line.transpose()

        return np.sqrt((y_line - y_col)**2 + (x_line - x_col)**2)
        

        
    def __repr__(self):
        """
        Method to represent the object
        """
        return "Real FAD Array\n\n Environment: {} \n Number of FADs: {}\n Fraction of equipped FADs: {}".format(self.env,
                                   self.nFAD,
                                   self.frac)
        
