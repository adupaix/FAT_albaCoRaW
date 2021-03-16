#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 11:20:40 2021

Definition de la classe utilisee pour creer les environnements de DCP reels

@author: adupaix
"""

class FAD_Array:
    """Classe qui contient un ensemble
    de DCP, tous caractérisés par :
        - un identifiant (un array, avec des numeros de 1 a Nfad)
        - des coordonnées (deux array, un avec x l'autre avec y')
        - la presence ou non d'une bouee
        """
 
    
    def __init__(self, path, environment, studyYear, study_center, detection_radius = 0.5):
        """
        Prend comme input:
            - l'environnement d'interet (hawaii, maldive ou maurice)
            - l'annee de l'etude
            - le rayon de detection
                
            Et genere un ensemble de DCP contenant:
                - 2 array avec 1 colonne contenant les coordonnes de tous les DCP (x et y, dans un repere en km, centre sur le 1e DCP)
                - 2 array avec une colonne contenant les coordonnes en degres (x_deg, y_deg)
                - un array avec 1 colonne contenant l'identifiant des DCP (id)
                - un array contenant un boleen par DCP, disant s'il a une bouee qui lui est associee (has_buoy)
                    si frac_with_buoy != 1, les DCP sont aleatoirement equipes (de maniere a respecter la fraction)
                - dr: un array contenant le rayon de detection par DCP (0 si pas de bouee, un nombre en km si le DCP est equipe)
                - nFAD: le nombre de DCP dans l'environnement
                - frac: la fraction de DCP equipes
                
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
        Methode pour changer le rayon de detection (dr) des DCPs
        Prend comme argument soit un float unique (a), soit un array de dimension (1,nFAD) (b)
        (a): toutes les bouees equipees prennent comme valeur de dr la valeur fournie
        (b): le DCP i prend la valeur i du vecteur fourni
        """
        if type(new_dr) is float:
            self.dr = self.has_buoy * new_dr
        elif (type(new_dr) is np.ndarray) and len(new_dr)==len(self.dr):
            self.dr = new_dr
        else:
            print("Warning: Wrong type or length of the given new_dr. Detection radius was not changed !")
    
    def distance_matrix(self):
        """
        Calcule la matrice de distance entre
        tous les DCP de l'array
        """
        x_line = np.repeat(self.x, self.nFAD).reshape(self.nFAD,self.nFAD)
        x_col = x_line.transpose()

        y_line = np.repeat(self.y, self.nFAD).reshape(self.nFAD,self.nFAD)
        y_col = y_line.transpose()

        return np.sqrt((y_line - y_col)**2 + (x_line - x_col)**2)
        

        
    def __repr__(self):
        """Methode pour afficher l objet
        """
        return "Real FAD Array\n\n Environment: {} \n Number of FADs: {}\n Fraction of equipped FADs: {}".format(self.env,
                                   self.nFAD,
                                   self.frac)
        
