#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 14:48:02 2021

Definition de la classe Land

@author: adupaix
"""

class Land:
    """
    Class qui contient un polygone construit a partir des
    coordonnees des terres dans la zone d'etude
    """
    
    def __init__(self, path, environment, study_center, land_file):
        """
        Initialise un objet de la classe Land
        
        arguments:
            - path: (str) chemin vers les fichiers csv avec les coordonnees de la terre
            - environment: (str) soit hawaii, maldives ou mauritius
            
        contient:
            - poly : polygon of the land
            - line: lines of the coasts
            - x and y: coordinates of the points used to build the polygon and line
            Each of these 4 variables are stored in km from the "study_center" and in degree of long,lat
            (add "_deg" to the name of the variable)
            
            - env: name of the environment
        """
        convKmDeg = 111
        
        self.env = environment
        self.island = land_file
        
        self.x_deg = []
        self.y_deg = []
        
        fr = open(str(path)+"/"+land_file+".csv")
              
        for d in csv.DictReader(fr):
            self.x_deg.append(float(d['x']))
            self.y_deg.append(float(d['y']))
            
        fr.close()
        
                    
        self.x_deg = np.array(self.x_deg)
        self.y_deg = np.array(self.y_deg)
        
        coords_deg = np.c_[self.x_deg, self.y_deg]
                
        self.poly_deg = Polygon(coords_deg)
        self.line_deg = LinearRing(coords_deg)
        
        self.x = (self.x_deg - np.repeat(study_center[0], len(self.x_deg))) * convKmDeg
        self.y = (self.y_deg - np.repeat(study_center[1], len(self.y_deg))) * convKmDeg
        
        coords = np.c_[self.x, self.y]
                
        self.poly = Polygon(coords)
        self.line = LinearRing(coords)
        
        
    def __repr__(self):
        """Methode pour afficher l objet
        """
        return "Land object\n\n Environment: {}\n Island: {}".format(self.env, self.island)
        
        