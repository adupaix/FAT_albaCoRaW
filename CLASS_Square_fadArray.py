#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 15:39:26 2021

Definition of the class used to create square arrays of FADs

@author: adupaix
"""

class FAD_Array:
    """
    Class with contains an array of FADs, each FAD characterized by :
        - an id (1D array, with numbers from 1 to Nfad)
        - coordinates (two 1D arrays, one with x one with y)
        - presence of not of an acoustic receiver
        """
 
    
    def __init__(self, L, distFAD, frac_with_buoy = 1, detection_radius = 0.5):
        """
        Takes as inputs:
            - the size of the array to generate (L, in km)
            - the distance between FADs (distFAD, in km)
            - the fraction of equipped FADs, default = 1
                
            And generates a FAD array containing:
                - two 1D arrays with FAD coordinates (x et y)
                - one 1D array with FAD identification numbers (id)
                - one 1D array with boleens, to know if the FAD is equipped with a receiver (has_buoy)
                    if frac_with_buoy!=1, FADs are randomly equipped (to respect the given fraction)
                - dr: 1D array containing the detection radius for each FAD (0 if no receiver, radius in km if the FAD is equipped)
                - nFAD: number of FADs in the array
                - frac: fraction of equipped FADs
                
        """
            
        fadRow  = round(L/distFAD)+1
        self.x = np.repeat(np.arange(0, fadRow*distFAD, distFAD), fadRow) #longitude
        self.y = np.tile(np.arange(0, fadRow*distFAD, distFAD), fadRow) #latitude
            
        self.id = np.arange(1,fadRow**2+1) #id number
            
        self.has_buoy = np.r_[np.repeat(True, round((fadRow**2)*frac_with_buoy)),
                              np.repeat(False, round((fadRow**2)*(1-frac_with_buoy)))] #wether FADs are equipped or not
            
        rd.shuffle(self.has_buoy)
        
        self.dr = self.has_buoy * detection_radius # detection radius in km
        
        self.nFAD = fadRow**2 # number of FADs in the array
        self.distFAD = distFAD # distance between FADs
        self.L = L # width of the array
        self.frac = frac_with_buoy # fraction of FADs that are equipped with a buoy
        
    
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
    
        
    def distance_matrix(self, array_FADs):
        """
        Calculate the distance matrix between
        a set of FADs in the array
        given in array_FADs (containing the FADs id)
        """
        # get the positions of the FADs which are in array_FADs
        x = self.x[np.where([fad in array_FADs for fad in self.id])[0]]
        y = self.y[np.where([fad in array_FADs for fad in self.id])[0]]
        
        x_line = np.repeat(x, len(x)).reshape(len(x),len(x))
        x_col = x_line.transpose()
        
        y_line = np.repeat(y, len(y)).reshape(len(y),len(y))
        y_col = y_line.transpose()
        
        return np.sqrt((y_line - y_col)**2 + (x_line - x_col)**2)

        
    def __repr__(self):
        """
        Method to represent the object
        """
        return "Square FAD Array\n\n Array width: {} km\n Number of FADs: {}\n Distance between FADs: {} km\n Fraction of equipped FADs: {}".format(self.L,
                                   self.nFAD,
                                   self.distFAD,
                                   self.frac)
    
    def save(self):
        """
        Method to save the FAD array coordinates
        """
        FADs_coords = np.c_[self.id, self.x, self.y, self.dr]
        
        np.save(str(path_output)+"/FAD_array/FADs_coords.npy", FADs_coords)
        np.savetxt(str(path_output)+"/FAD_array/FADs_coords.csv", FADs_coords)
        
