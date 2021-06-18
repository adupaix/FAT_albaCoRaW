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
            - la distance entre DCP (distFAD, en km)
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
    
        
    def distance_list(self, tuna, edge_dict):
        """
        Returns an array of distances for each CAT performed by the tuna
        taking into account the edge crosses
        """
        # get the positions and the side where the tuna crossed at the edge
        edge_p = np.where(tuna.edge != 0)
        edge_side = tuna.edge[edge_p]
        
        # create a list with the id of FADs to which the tuna associated
        # each element of the list contains [FAD id, array with the side crossing done before this association]
        FADs_start_asso = tuna.num_asso_FAD[start_asso]
        FADs_start_list = [[i] for i in FADs_start_asso]
        for i in range(start_asso.shape[0]):
            if (start_asso[i] >= edge_p).any():
                FADs_start_list[i].append(edge_side[np.where(start_asso[i] >= edge_p)[1]])
        
        # identical as above, but for the ends of associations
        FADs_end_asso = tuna.num_asso_FAD[end_asso]
        FADs_end_list = [[i] for i in FADs_end_asso]
        for i in range(end_asso.shape[0]):
            if (end_asso[i] >= edge_p).any():
                FADs_end_list[i].append(edge_side[np.where(end_asso[i] >= edge_p)[1]])
        
        # get the number of distances to calculate
        # if the tuna is not associated at the end of its path
        # the last complete time is a CRT. So we have the same number of
        # CATs and CRTs, hence we delete the last time of end of association
        if tuna.num_asso_FAD[-1] == 0:
            rg = range(len(end_asso)-1)
        else: # else, tha last complete time is a CAT, so we keep all the times
        # and we have n+1 CATs and n CRTs in the tuna trajectory
            rg = range(len(end_asso))
        
        dist = list()
        for i in rg:
            # get the positions of the FADs
            x1 = self.x[np.where(self.id == int(FADs_end_list[i][0]))]
            x2 = self.x[np.where(self.id == int(FADs_start_list[i][0]))]
            y1 = self.y[np.where(self.id == int(FADs_end_list[i][0]))]
            y2 = self.y[np.where(self.id == int(FADs_start_list[i][0]))]
            # Correct them in case the tuna crossed by one side of the study area
            if len(FADs_end_list[i]) > 1:
                for j in FADs_end_list[i][1]:
                    x1 += edge_dict[j][0]
                    y1 += edge_dict[j][1]
            if len(FADs_start_list[i]) > 1:
                for j in FADs_start_list[i][1]:
                    x2 += edge_dict[j][0]
                    y2 += edge_dict[j][1]
            
            d = math.sqrt((x1-x2)**2 + (y1-y2)**2)
            dist.append(d)
        
        return np.array(dist)

        
    def __repr__(self):
        """Methode pour afficher l objet
        """
        return "Square FAD Array\n\n Array width: {} km\n Number of FADs: {}\n Distance between FADs: {} km\n Fraction of equipped FADs: {}".format(self.L,
                                   self.nFAD,
                                   self.distFAD,
                                   self.frac)
        


    def correct_edge(self, tuna):
        """
        Add other FADs, to have an array covering the whole
        tuna path
        """
        
        x_rg = range(math.floor(min(tuna.x) / L), math.ceil(max(tuna.x) / L))
        y_rg = range(math.floor(min(tuna.y) / L), math.ceil(max(tuna.y) / L))
        
        for i in x_rg:
            if i != 0:
                self.x = np.r_[self.x, self.x + i*L]
                self.y = np.r_[self.y, self.y]
                
        for i in y_rg:
            if i != 0:
                self.x = np.r_[self.x, self.x]
                self.y = np.r_[self.y, self.y + i*L]
                
        self.nFAD = len(self.x)
        self.dr = np.repeat(self.dr, len(self.x)/len(self.dr))
        self.has_buoy = np.repeat(self.has_buoy, len(self.x)/len(self.has_buoy))
                
                
        