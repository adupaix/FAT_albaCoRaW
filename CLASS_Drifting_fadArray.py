#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 2 14:27:26 2021

Definition de la classe utilisee pour creer l'environnement de DCP derivants

@author: adupaix
"""

class FAD_Array:
    """Classe qui contient un ensemble
    de DCP, tous caractérisés par :
        - un identifiant (un array, avec des numeros de 1 a Nfad)
        - des coordonnées (deux array, un avec x l'autre avec y')
        - la presence ou non d'une bouee
        
        A CHANGER
        """
 
    
    def __init__(self, path, detection_radius = 0.5):
        """
        Prend comme input:
            - chemin contenant les fichiers (les csv contenant les positions de DCP sont dans un sous-dossier nommé "drifting_FadArray")
            - le rayon de detection d'un DCP
                
            Et genere un ensemble de DCP contenant:
                - 2 array avec 1 colonne contenant les coordonnes de tous les DCP (x et y)
                - un array avec 1 colonne contenant l'identifiant des DCP (id)
                - le pas de temps p, fixé à 0 au départ
                - dr: un array contenant le rayon de detection par DCP (0 si pas de bouee, un nombre en km si le DCP est equipe) OK
                - nFAD: le nombre de DCP dans l'environnement (sera mis a jour a chaque pas de temps)
                - files: list contenant les noms de fichiers csv
                - dict_files: dict qui contient {position du csv dans files : [min step contenu dans le csv, max step contenu dans le csv]}
                
                Stock aussi les arguments fournis pour creer l'environnement
                - L: la largeur du carre (PAS UTILE?)
                - frac: la fraction de DCP equipes OK
                
        """
            
        convKmDeg = 111
        
        # read the first file with FAD positions
        self.files = list()
        for file in os.listdir(str(path)+"/drifting_fadArray"):
            if file.startswith("0to"):
                init_file = file
            if "to" in file:
                self.files.append(file)
                
        # initialize variables
        timesteps = list()
        self.x_deg = list()
        self.y_deg = list()
        self.id = list()
        
        # read csv file
        with open(str(path)+"/drifting_fadArray/"+init_file) as fr:
            for d in csv.DictReader(fr):
                timesteps.append(float(d['timestep']))
                self.x_deg.append(float(d['longitude']))
                self.y_deg.append(float(d['latitude']))
                self.id.append(float(d['FAD_id']))
        
        # change variables to arrays
        timesteps = np.array(timesteps)
        self.x_deg = np.array(self.x_deg)
        self.y_deg = np.array(self.y_deg)
        self.id = np.array(self.id)
        
        # keep only the initial positions
        self.x_deg = self.x_deg[timesteps == 0]
        self.y_deg = self.y_deg[timesteps == 0]
        self.id = self.id[timesteps == 0]
        
               
        # change positions in degree to positions in km from center
        self.x = (self.x_deg - np.repeat(study_center[0], len(self.x_deg))) * convKmDeg
        self.y = (self.y_deg - np.repeat(study_center[1], len(self.y_deg))) * convKmDeg
        
        # step
        self.p = 0
        
        ## Other variables
        self.dr = np.repeat(detection_radius, len(self.id))# detection radius in km
        
        self.nFAD = len(self.id) # number of FADs in the array
        # self.distFAD = distFAD # distance between FADs
        self.L = L # width of the array
        self.frac = 1 # fraction of FADs that are equipped with a buoy
        
        # create a dictionnary to know which steps are in which csv files
        self.dict_files = dict()
        for i in range(len(self.files)):
            self.dict_files[i] = [int( self.files[i][0:(self.files[i].index("to"))] ),
                                  int( self.files[i][(self.files[i].index("to"))+2 : -4])]
        
    
    
    def update_position(self, path, new_p):
        """
        Méthode pour mettre à jour les positions des DCP
        Prend comme argument le chemin vers les fichier,
        et le nouveau step (dans la simulation, contenu dans tuna.p)
        """
        
        convKmDeg = 111
        
        self.p = new_p
        
        # get the name of the file containing the data for the timestep p
        for fnb, rg in self.dict_files.items():
            if self.p >= rg[0] and self.p <= rg[1]:
                int_file = self.files[fnb]
                
        
        # re-initialize variables
        timesteps = list()
        self.x_deg = list()
        self.y_deg = list()
        self.id = list()
        
        # read csv file
        with open(str(path)+"/drifting_fadArray/"+int_file) as fr:
            for d in csv.DictReader(fr):
                timesteps.append(float(d['timestep']))
                self.x_deg.append(float(d['longitude']))
                self.y_deg.append(float(d['latitude']))
                self.id.append(float(d['FAD_id']))
                
        # change variables to arrays
        timesteps = np.array(timesteps)
        self.x_deg = np.array(self.x_deg)
        self.y_deg = np.array(self.y_deg)
        self.id = np.array(self.id)
        
        # keep only the positions of the timestep p
        self.x_deg = self.x_deg[timesteps == self.p]
        self.y_deg = self.y_deg[timesteps == self.p]
        self.id = self.id[timesteps == self.p]
        
        # change positions in degree to positions in km from center
        self.x = (self.x_deg - np.repeat(study_center[0], len(self.x_deg))) * convKmDeg
        self.y = (self.y_deg - np.repeat(study_center[1], len(self.y_deg))) * convKmDeg
        
        ## Update other variables
        self.dr = np.repeat(self.dr[0], len(self.id))# detection radius in km
        
        self.nFAD = len(self.id) # number of FADs in the array
        
    
    
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
    
        
    def distance_matrix(self, array_FADs, timestep_FADs):
        """
        Calcule la matrice de distance entre un set
        de DCP, fournis dans array_FADs (contient l'identifiant des DCP)
                                         
        BESOIN DE FOURNIR AUSSI LES timesteps OU LES DCP ONT ETE VISITES
        """
        
        x = list()
        y = list()
        
        int_file = list()
        
        for i in range(len(timestep_FADs)):
            # get the name of the file containing the data for the timestep p
            for fnb, rg in self.dict_files.items():
                if timestep_FADs[i] >= rg[0] and timestep_FADs[i] <= rg[1]:
                    int_file.append(self.files[fnb])
        
        int_file = np.array(int_file)
        
        array_toread = np.c_[int_file, array_FADs, timestep_FADs]
        
        for int_file_i in np.unique(int_file):
            array_toread_i = array_toread[array_toread[:,0] == int_file_i, :]
                    
            xp = list()
            yp = list()
            idp = list()
            tsp = list()
            # read csv file
            with open(str(path)+"/drifting_fadArray/"+int_file_i) as fr:
                for d in csv.DictReader(fr):
                    tsp.append(float(d['timestep']))
                    xp.append(float(d['longitude']))
                    yp.append(float(d['latitude']))
                    idp.append(float(d['FAD_id']))
                    
            tsp = np.array(tsp)
            xp = np.array(xp)
            yp = np.array(yp)
            idp = np.array(idp)
        
        id_unique_part1 = np.char.add(tsp.astype(np.int).astype(np.str), np.repeat('_', len(tsp)))
        #rajouter idp
        
            xp = xp[np.logical_and(np.in1d(tsp, array_toread_i[:,2].astype(np.float)),
                                   np.in1d(idp, array_toread_i[:,1].astype(np.float)))]
            yp = yp[np.logical_and(tsp == timestep_FADs[i], idp == array_FADs[i])]
            
            x.append(float(xp))
            x.append(float(yp))
                    
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
        return "Drifting FAD Array\n\n Number of FADs: {}\n Simulation step: {} \n Fraction of equipped FADs: {}".format(self.nFAD,
                                   self.p,
                                   self.frac)
        
