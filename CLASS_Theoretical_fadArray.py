#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 15 15:39:26 2021
Adapted from CLASS_Square_fadArray.py

Definition of the class used to create theoretical arrays of FADs
Either square, random or randomized square array

@author: adupaix
"""

class FAD_Array:
    """
    Class which contains an array of FADs, each FAD characterized by :
        - an id (1D array, with numbers from 1 to Nfad)
        - coordinates (two 1D arrays, one with x one with y)
        - presence of not of an acoustic receiver
    """
 
    
    def __init__(self, environment, L, distFAD, R0, frac_with_buoy = 1, detection_radius = 0.5):
        """
        Takes as inputs:
            - the environment name (one of ["random","square","square_rd"])
            - the size of the array to generate (L, in km)
            - the mean distance between FADs (distFAD, in km), used to determine the FAD density
            - the fraction of equipped FADs, default = 1
            - the attraction radius of FADs (R0), used only if environment == "square_rd"
                
            And generates a FAD array containing:
                - two 1D arrays with FAD coordinates (x et y)
                - one 1D array with FAD identification numbers (id)
                - one 1D array with boleens, to know if the FAD is equipped with a receiver (has_buoy)
                    if frac_with_buoy!=1, FADs are randomly equipped (to respect the given fraction)
                - dr: 1D array containing the detection radius for each FAD (0 if no receiver, radius in km if the FAD is equipped)
                - nFAD: number of FADs in the array
                - frac: fraction of equipped FADs
                
            Also stores the inputs given to create the array
                - distFAD: mean inter-FAD distance
                - L: size of the array
                - frac: fraction of equipped FADs
                
        """
        
        self.environment = environment
        
        fadRow  = round(L/distFAD)
        self.nFAD = fadRow**2 # number of FADs in the array
        
        self.id = np.arange(1,self.nFAD+1) #id number
            
        self.has_buoy = np.r_[np.repeat(True, round((fadRow**2)*frac_with_buoy)),
                              np.repeat(False, round((fadRow**2)*(1-frac_with_buoy)))] #wether FADs are equipped or not
            
        rd.shuffle(self.has_buoy)
        
        self.dr = self.has_buoy * detection_radius # detection radius in km
        
        
        self.distFAD = distFAD # distance between FADs
        self.L = L # width of the array
        self.frac = frac_with_buoy # fraction of FADs that are equipped with a buoy
        
        if environment == "random":
            self.x = np.random.rand(self.nFAD)*L #longitude
            self.y = np.random.rand(self.nFAD)*L #latitude
        elif environment in ["square","square_rd"]:
            self.x = np.repeat(np.arange(distFAD/2, (fadRow)*distFAD, distFAD), fadRow) #longitude
            self.y = np.tile(np.arange(distFAD/2, (fadRow)*distFAD, distFAD), fadRow) #latitude
            
            if environment == "square_rd":        
                #move the FADs on x and y axis but with condition (not fully randomized):
                    ## R0 of FADs cannot overlap
                self.x = self.x + np.random.uniform(low = R0 - distFAD/2, high = distFAD/2 - R0, size = fadRow**2)
                self.y = self.y + np.random.uniform(low = R0 - distFAD/2, high = distFAD/2 - R0, size = fadRow**2)
        
                # FADs that went above the edge are moved to the other side of the study area
                self.x[self.x < 0] = self.x[self.x < 0] + L
                self.x[self.x > L] = self.x[self.x > L] - L
                self.y[self.y < 0] = self.y[self.y < 0] + L
                self.y[self.y > L] = self.y[self.y > L] - L
            
                #save the R0 for the display of the array
                self.R0 = R0 
        
    
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
        nns = list()
        for i in rg:
            x1 = FADs.x[np.where(FADs.id == int(FADs_end_list[i][0]))]
            x2 = FADs.x[np.where(FADs.id == int(FADs_start_list[i][0]))]
            y1 = FADs.y[np.where(FADs.id == int(FADs_end_list[i][0]))]
            y2 = FADs.y[np.where(FADs.id == int(FADs_start_list[i][0]))]
            
            # get the positions of the FADs
            # x1 = self.x[np.where(self.id == int(FADs_end_list[i][0]))]
            # x2 = self.x[np.where(self.id == int(FADs_start_list[i][0]))]
            # y1 = self.y[np.where(self.id == int(FADs_end_list[i][0]))]
            # y2 = self.y[np.where(self.id == int(FADs_start_list[i][0]))]
            
            # Then, to get the nearest neighbor number
            # we consider the "arena" of LxL where the tuna was launched from and the 8 squares around
            # FADs_x_for_nn = np.array(list(np.concatenate((self.x + edge_dict[1][0], self.x, self.x + edge_dict[3][0]))) * 3)
            # FADs_y_for_nn = np.concatenate((np.array(list(self.y + edge_dict[2][1]) * 3),
            #                                 np.array(list(self.y) * 3),
            #                                 np.array(list(self.y + edge_dict[4][1]) * 3)))
            
            FADs_x_for_nn = np.array(list(np.concatenate((FADs.x + edge_dict[1][0], FADs.x, FADs.x + edge_dict[3][0]))) * 3)
            FADs_y_for_nn = np.concatenate((np.array(list(FADs.y + edge_dict[2][1]) * 3),
                                            np.array(list(FADs.y) * 3),
                                            np.array(list(FADs.y + edge_dict[4][1]) * 3)))
            
            # Correct the positions in case the tuna crossed by one side of the study area
            if len(FADs_end_list[i]) > 1:
                for j in FADs_end_list[i][1]:
                    x1 += edge_dict[j][0]
                    y1 += edge_dict[j][1]
                    FADs_x_for_nn += edge_dict[j][0]
                    FADs_y_for_nn += edge_dict[j][1]
            if len(FADs_start_list[i]) > 1:
                for j in FADs_start_list[i][1]:
                    x2 += edge_dict[j][0]
                    y2 += edge_dict[j][1]
            
            # get the distance between the two FADs
            d = math.sqrt((x1-x2)**2 + (y1-y2)**2)
            dist.append(d)
            
            # if the tuna traveled more than the length of the arena along one axis (x or y)
            # we add other arenas to the FADs_*_for_nn vectors
            if np.round(abs(x2-x1) / FADs.L)[0] > 0 or np.round(abs(y2-y1) / FADs.L)[0] > 0:
                nb_of_arena_layers = int(max(np.round(abs(x2-x1) / FADs.L), np.round(abs(y2-y1) / FADs.L)))
                if nb_of_arena_layers > 4:
                    raise ValueError('Tuna moved too far from the initial FAD to properly estimate the nearest neighbor number. Please contact us at amael.dupaix@ird.fr so the script can be adapted',
                                     'nb_of_arena_layers: '+str(nb_of_arena_layers),
                                     'FADs_end_list: '+str(FADs_end_list),
                                     'FADs_start_list: '+str(FADs_start_list))
                FADs_x_for_nn = np.repeat(np.concatenate((FADs_x_for_nn + 3*edge_dict[1][0], FADs_x_for_nn, FADs_x_for_nn + 3*edge_dict[3][0])), repeats = 3)
                FADs_y_for_nn = np.concatenate((np.repeat(FADs_y_for_nn + 3*edge_dict[2][1], repeats = 3),
                                                np.repeat(FADs_y_for_nn, repeats = 3),
                                                np.repeat(FADs_y_for_nn + 3*edge_dict[4][1], repeats = 3)))
                    
            # we compute the vector of distance from the starting FAD
            distance_vect = np.sqrt((FADs_y_for_nn - y1)**2 + (FADs_x_for_nn - x1)**2)
            # and get the position corresponding the nn number
            nn = np.min(np.where(np.round(np.sort(distance_vect), decimals = 6) == round(d, ndigits = 6)))
            
            nns.append(nn)
                    
        return np.c_[np.array(dist), np.array(nns)]
    
        
    def __repr__(self):
        """
        Method to represent the object
        """
        if self.environment == "random":
            return "Random FAD Array\n\n Array width: {} km\n Number of FADs: {}\n Mean distance between FADs: {} km\n Fraction of equipped FADs: {}".format(self.L,
                                   self.nFAD,
                                   self.distFAD,
                                   self.frac)
        elif self.environment == "square":
            return "Square FAD Array\n\n Array width: {} km\n Number of FADs: {}\n Distance between FADs: {} km\n Fraction of equipped FADs: {}".format(self.L,
                                   self.nFAD,
                                   self.distFAD,
                                   self.frac)
        elif self.environment == "square_rd":
            return "Randomized square FAD Array\n\n Array width: {} km\n Number of FADs: {}\n Distance between FADs: {} km\n Fraction of equipped FADs: {}\n R0 associated to FADs: {} km".format(self.L,
                                   self.nFAD,
                                   self.distFAD,
                                   self.frac,
                                   self.R0)
            
    
    def save(self):
        """
        Method to save the FAD array coordinates
        """
        FADs_coords = np.c_[self.id, self.x, self.y, self.dr]
        
        np.save(str(path_output)+"/FAD_array/FADs_coords.npy", FADs_coords)
        np.savetxt(str(path_output)+"/FAD_array/FADs_coords.csv", FADs_coords)
        
        
    def load(self, path_output):
        """
        Read an array containing the FADs positions
        and fill the FAD_Array data with it
        """
        FADs_coords = np.load(str(path_output)+"/FAD_array/FADs_coords.npy")
        
        self.id = FADs_coords[:,0]
        self.x = FADs_coords[:,1]
        self.y = FADs_coords[:,2]
        self.dr = FADs_coords[:,3]
        
        self.nFAD = len(self.id)
        self.has_buoy = self.dr != 0
        
        
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
                
                
