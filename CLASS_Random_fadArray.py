#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 15:39:26 2021

Definition de la classe utilisee pour creer l'environnement de DCP theorique

@author: adupaix
"""

class FAD_Array:
    """Classe qui contient un ensemble
    de DCP, tous caractérisés par :
        - un identifiant (un array, avec des numeros de 1 a Nfad)
        - des coordonnées (deux array, un avec x l'autre avec y')
        - la presence ou non d'une bouee
        """
 
    
    def __init__(self, L, distFAD, frac_with_buoy = 1, detection_radius = 0.5):
        """
        Prend comme input:
            - la largeur du carre a generer (L, en km)
            - la distance moyenne entre DCP (distFAD, en km), utilisee pour determiner la densite
            - la fraction de DCP equipes, par defaut = 1
                
            Et genere un ensemble de DCP contenant:
                - 2 array avec 1 colonne contenant les coordonnes de tous les DCP (x et y)
                - un array avec 1 colonne contenant l'identifiant des DCP (id)
                - un array contenant un boleen par DCP, disant s'il a une bouee qui lui est associee (has_buoy)
                    si frac_with_buoy != 1, les DCP sont aleatoirement equipes (de maniere a respecter la fraction)
                - dr: un array contenant le rayon de detection par DCP (0 si pas de bouee, un nombre en km si le DCP est equipe)
                - nFAD: le nombre de DCP dans l'environnement
                
                Stock aussi les arguments fournis pour creer l'environnement
                - distFAD: la distance entre DCP
                - L: la largeur du carre
                - frac: la fraction de DCP equipes
                
        """
        
        fadRow  = round(L/distFAD)+1
        self.nFAD = fadRow**2 # number of FADs in the array
        
        self.x = np.random.rand(self.nFAD)*L #longitude
        self.y = np.random.rand(self.nFAD)*L #latitude
            
        self.id = np.arange(1,fadRow**2+1) #id number
            
        self.has_buoy = np.r_[np.repeat(True, round((fadRow**2)*frac_with_buoy)),
                              np.repeat(False, round((fadRow**2)*(1-frac_with_buoy)))] #wether FADs are equipped or not
            
        rd.shuffle(self.has_buoy)
        
        self.dr = self.has_buoy * detection_radius # detection radius in km
        
        
        self.distFAD = distFAD # distance between FADs
        self.L = L # width of the array
        self.frac = frac_with_buoy # fraction of FADs that are equipped with a buoy
        
    
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
    
        
    def distance_matrix(self, array_FADs):
        """
        Calcule la matrice de distance entre un set
        de DCP, fournis dans array_FADs (contient l'identifiant des DCP)
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
        """Methode pour afficher l objet
        """
        return "Random FAD Array\n\n Array width: {} km\n Number of FADs: {}\n Mean distance between FADs: {} km\n Fraction of equipped FADs: {}".format(self.L,
                                   self.nFAD,
                                   self.distFAD,
                                   self.frac)
        
