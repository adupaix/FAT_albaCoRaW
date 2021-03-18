# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 15:39:26 2021

Definition de la classe Tuna

@author: adupaix
"""


class Tuna:
    """ Classe definissant un thon par :
        - son numero d'id (id)
        - sa duree de vie (lifetime)
        - sa position geographique (x et y)
        - ses angles alpha et theta
        - in_R0_FAD: boleen pour savoir si le thon est a moins de R0 d'un DCP
        - num_asso_FAD: suivi des associations (pour chaque pas de temps, 0 si pas detecte par un DCP, num du DCP sinon)
        - last_FAD: numero du DCP qui vient d'etre visite, pour ne pas revenir en arriere (reinitialise quand sort du rayon R0)
        
        parametres de classe:
        - vitesse (v)
        - taux de mortalite (m)
        - rayon d'orientation (R0)
        - coefficient de sinuosite (c)
        
        + methodes associees
        
        """
    
    nb_tunas = 0
    
    v = 0.7 #speed
    l = 0 # distance covered by a tuna at each time step
    
    R0 = 5 #orientation radius in km
    
    c = 0.999 #coefficient of sinuosity
    sigma = math.sqrt(-2*math.log(c))
    
    m = 1 #mortality rate in %/day
    step_m = ((m / 100 ) * step_time)/(24*3600) #mortality rate per time step
    # q = 0
    
    def __init__(self, Npas, CRW = True):
        """ On definit tous les attributs
        
        Besoin de specifier Npas, pour limiter la duree de vie
        
        """
        
        Tuna.nb_tunas += 1
        
        self.id = Tuna.nb_tunas 
        
        ## Parametres d'etat
        self.lifetime = Tuna.lifetime(Npas)
        self.x = np.zeros(self.lifetime)
        self.y = np.zeros(self.lifetime)
        
        ## genere tous les alpha des l'initialisation du thon, a partir d'une loi normale tronquee
        # moyenne: 0, sd: sigma, tronquee a -pi et pi
        # cf. https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.truncnorm.html
        if CRW == True:
            self.alpha = truncnorm.rvs((-math.pi) / Tuna.sigma, (math.pi) / Tuna.sigma, loc=0, scale=Tuna.sigma, size = self.lifetime)
        else:
            self.alpha = np.zeros(self.lifetime)
            Tuna.c = 1
            Tuna.sigma = 0
            
        self.theta = np.zeros(self.lifetime)
        # self.t = 0 #timestamp in s (initial time = 0)
        
        self.in_R0_FAD = 0 # tuna is at a distance < R0 from a FAD or not (0: no FAD, other: number of the FAD)
        
        self.num_asso_FAD = np.zeros(self.lifetime) # a chaque tour, stock 0 (pas d'association) ou x = identifiant du DCP auquel le thon est associe
        self.last_FAD = 0 #numero du dernier DCP auquel le thon s'est associe
        
        self.p = 0 # numero du pas de temps où en est le thon
        self.num_steps = np.array(range(self.lifetime)) # numero des pas de temps stockes (parallele aux autres donnees) Sert pour le plot
        
        self.crw = crw #si le thon (hors association) se déplace en marche aléatoire correlée. False quand on veut explorer la condition
        # extreme c = 1 (le thon se déplace en ligne droite)
        
    
    def lifetime(Npas):
        """A l'initialisation du thon
        on calcul sa duree de vie"""
        
        if Tuna.m == 0:
            return Npas-1
        else:
            k=1
            r_mortality = rd.random()
            while r_mortality > Tuna.step_m and k<=Npas-1:
                k += 1
                r_mortality = rd.random()
            
            return(k)
    
    
    #### METHODE SUR LES PARAMETRES DE CLASSE
    def change_c(new_c):
        """Fonction pour modifier le coeff
        de sinuosite c. Change en meme temps
        le sigma
        """
        Tuna.c = new_c
        if new_c != 1:
            Tuna.sigma = math.sqrt(-2*math.log(new_c))
        else:
            Tuna.sigma = 0
                
    def change_m(new_m):
        """Methode pour modifier le taux
        de mortalite m. Change en meme temps
        le step_m
        """
        Tuna.m = new_m
        Tuna.step_m = ((new_m / 100 ) * step_time)/(24*3600)
    
    
    ### METHODES DE MOUVEMENT DES THONS
    def CRWMove(self):
        """ On change la position du thon dans le cas
        d'un Correlated Random Walk
        i.e. si le thon ne va pas vers un DCP"""
        
        p = self.p
        
       
        ## CRW -> random search behaviour: Determine the next position
        # Rappel: alpha est initialise des le debut, on va juste chercher la valeur contenue dans l'array
        self.theta[p] = self.alpha[p] + self.theta[p-1]
        
        
        if self.theta[p] > math.pi:
            self.theta[p] = self.theta[p] - (2*math.pi)
        elif self.theta[p] < (-math.pi):
            self.theta[p] = self.theta[p] + (2*math.pi)
        
        
        
        self.x[p+1] = self.x[p] + math.cos(self.theta[p])*Tuna.l
        self.y[p+1] = self.y[p] + math.sin(self.theta[p])*Tuna.l
        
        self.p += 1
    
        
    def add_res_time(self, CRTs):
        """
        Dans le cas ou add_CRTs est vrai
        on prend un CRT au hasard dans la liste fournie
        et le thon attend ce temps sous le DCP
        
        Les CRT fournis doivent être en jour
        """
        crt_day = rd.choice(CRTs)
        
        crt_steps = int(crt_day * 24 * 3600 / step_time)
        
        p = self.p
        
        # If there are enough steps to wait under the FAD
        if p+crt_steps < self.lifetime:
            self.x[p:p+crt_steps+1] = x_fadReached
            self.y[p:p+crt_steps+1] = y_fadReached
            self.num_asso_FAD[p:p+crt_steps+1] = self.in_R0_FAD
            #pour que le thon reparte dans la meme direction que celle d'arrivee:
            self.theta[p-1:p+crt_steps] = self.theta[p-1] 
            
        # If there are not enough steps, stops
        else:
            steps_left = self.lifetime-(p)
            self.x[p:p + steps_left] = x_fadReached
            self.y[p:p + steps_left] = y_fadReached
            self.num_asso_FAD[p:p+steps_left] = self.in_R0_FAD
            print("  Warning: Not enough steps to add CRT")
            
        self.p += crt_steps
        
        
        
    def OMove(self, x_fadReached, y_fadReached, CRTs):
        """ On change la position du thon dans le cas
        d'un Oriented Movment
        i.e. si le thon est a moins de R0 d'un DCP + c'est le jour """
        
        p = self.p
        
        dist_tunaFAD = math.sqrt((y_fadReached-self.y[p])**2
                                 +(x_fadReached-self.x[p])**2)
        
            ## Go in straigth line towards the next position
        nstep_jump = round(dist_tunaFAD/Tuna.l)
                
            ## The new theta angle is directly determined by the positions                  
        self.theta[p] = math.asin((y_fadReached - self.y[p])/dist_tunaFAD)
            #~> If go backward on the x axis (ie if beta in -pi;-pi/2 or in pi/2;pi)
        if x_fadReached < self.x[p]: self.theta[p] = math.pi-math.asin((y_fadReached - self.y[p])/dist_tunaFAD)
            
        if self.theta[p] > math.pi:
            self.theta[p] -= 2*math.pi
        if self.theta[p] < (-math.pi):
            self.theta[p] += 2*math.pi
        
        # calculate alpha after theta, using theta i and theta i-1
        # replace the random alpha in the alpha array
        self.alpha[p] = self.theta[p] - self.theta[p-1]
        
        # If there are enough steps to reach the FAD, the following position is the FAD position
        if p+nstep_jump < self.lifetime:
            self.x[p+nstep_jump] = x_fadReached
            self.y[p+nstep_jump] = y_fadReached
            #pour que le thon reparte dans la meme direction que celle d'arrivee:
            self.theta[p+nstep_jump-1] = self.theta[p] 
            
        # If there are not enough steps, stops before the FAD
        else:
            steps_left = self.lifetime-(p+1)
            self.x[p + steps_left] = self.x[p] + math.cos(self.theta[p])*Tuna.l*(steps_left)
            self.y[p + steps_left] = self.y[p] + math.sin(self.theta[p])*Tuna.l*(steps_left)
            
            print("  Warning: Not enough steps to reach last FAD")
     
        self.p += nstep_jump
        
        if addCRTs == True and p+nstep_jump < self.lifetime:
            # print("  adding CRT")
            Tuna.add_res_time(self, CRTs)
    
        
    def checkEnv(self, FADs):
        '''
        FADs: environnement en objet flottant de classe Square_fadArray
        
        Utilise la position du thon pour déterminer si:
            - le thon est associe a un DCP
            - le thon est dans le R0 d'un DCP
        
        Les trois indices renseignes sont utilises comme suit:
            - in_R0_FAD: permet de savoir si le thon detecte un DCP (distance < R0)
            
            - num_asso_FAD: array avec a chaque pas de temps le numero du DCP
                auquel le thon est associe (ou 0 si pas d'association)
                il change quand le thon entre et sort du detection_radius du DCP
                Permet ensuite de calculer les CAT
            
            - last_FAD: numero du dernier DCP rencontre. Permet que le thon ne revienne
                pas en arriere systematiquement quand il vient de s'associer avec un DCP
                prend le numero du DCP quand rentre dans son detection_radius, reprend la 
                valeur 0 quand il ressort du R0
                
                ATTENTION NE FONCTIONNE QUE SI distance entre DCP > R0
        '''
        p = self.p
        
        #calcul la distance entre le thon et les DCP (test en delimitant un carre autour du thon: plus long)
        dist_ft = np.sqrt((FADs.x[:]-self.x[p])**2 + (FADs.y[:]-self.y[p])**2)
        # enregistre l'identifiant du DCP detecte. Si pas de DCP dans un rayon de moins de R0, detected_Fad est vide
        detected_FAD = FADs.id[dist_ft <= Tuna.R0]
        # idem qu'au dessus, mais avec le rayon detection_radius, du DCP
        associated_FAD = FADs.id[dist_ft <= FADs.dr]
        
        if len(detected_FAD) == 0: #s'il n y a pas de DCP detecte, on met 0 dans in_R0_FAD et on reinitialise last_FAD
            self.in_R0_FAD = 0
            self.last_FAD = 0
        elif len(detected_FAD) == 1: #s'il y a un seul DCP detecte, on met son numero dans in_R0_FAD
            self.in_R0_FAD = detected_FAD
        else: #s'il y a plusieurs DCP detectes, on en choisi un au hasard
            self.in_R0_FAD = np.random.choice(detected_FAD)
            
            
        if len(associated_FAD) != 0: # si on est dans le rayon de detection (dr)
            if FADs.dr[dist_ft <= FADs.dr]!=0: # on verifie que le dr du DCP n'est pas nul. S'il est nul, c'est que le DCP n'est pas equipe
                self.num_asso_FAD[p] = associated_FAD
            # dans tous les cas, que le DCP soit equipe ou non, on ne veut pas que le thon y boucle, donc on enregistre le numero dans last_FAD
            self.last_FAD = associated_FAD
        else: # si on n'est pas dans le rayon de detection
            self.num_asso_FAD[p] = 0
        
        
    def checkLand(self, Island):
        """
        Methode utilisee dans les simulations dans des
        environnement reels, pour recalculer alpha de maniere a
        ce que le thon n'aille pas sur terre
        """
        
        p = self.p
        
        can_reach_land = Point(np.r_[self.x[p],self.y[p]]).buffer(Tuna.l).intersects(Island.line)
        
        if can_reach_land:
            
            # build the circle around the tuna position
            start_angle, end_angle = 0, 360 # In degrees -> to have a complete ring
            numsegments = 1000
            ## The coordinates of the arc
            theta = np.radians(np.linspace(start_angle, end_angle, numsegments))
            x = self.x[p] + Tuna.l * np.cos(theta)
            y = self.y[p] + Tuna.l * np.sin(theta)
            arc = geom.LineString(np.c_[x, y])
            
            # get the two intersects with the land
            pos1 = list(arc.intersection(Island.line)[0].coords)[0]
            pos2 = list(arc.intersection(Island.line)[1].coords)[0]
            
            # get the alpha angles corresponding to these 2 intersects
            theta2_pos1 = math.asin((pos1[1]-self.y[p])/Tuna.l)  
                    ##If go back to the principale coordinate of the plan
            if pos1[0]<self.x[p]: theta2_pos1 = -math.pi - math.asin((pos1[1]-self.y[p])/Tuna.l)
            alpha_pos1 = theta2_pos1 - self.theta[p-1]
                    #If over trigonometric circle
            if alpha_pos1>math.pi: alpha_pos1 = alpha_pos1 - (2*math.pi)
            if alpha_pos1<-math.pi: alpha_pos1 = alpha_pos1 + (2*math.pi)
                        #-> POSITION 2                        
            theta2_pos2 = math.asin((pos2[1]-self.y[p])/Tuna.l) 
                    ##If go back to the principal coordinate of the plan
            if pos2[0]<self.x[p]: theta2_pos1 = -math.pi - math.asin((pos1[1]-self.y[p])/Tuna.l)
            alpha_pos2 = theta2_pos2 - self.theta[p-1]
                    #If over trogonometric circle
            if alpha_pos2>math.pi: alpha_pos2 = alpha_pos2 - (2*math.pi)
            if alpha_pos2<-math.pi: alpha_pos2 = alpha_pos2 + (2*math.pi)
            
            proba_alpha = np.zeros((2, 4))
                   #pos1
            norm1 = truncnorm((-math.pi) / sigma_island, min(alpha_pos1, alpha_pos2) / sigma_island, loc=0, scale=sigma_island)
            proba_alpha[0,0] = alpha1 = norm1.rvs(1)
            proba_alpha[0,1] = P_alpha1 = stats.norm.pdf(alpha1, 0, sigma_island)
                  #pos2
            norm2 = truncnorm((max(alpha_pos1, alpha_pos2)) / sigma_island, math.pi / sigma_island, loc=0, scale=sigma_island)
            proba_alpha[1,0] = alpha2 = norm2.rvs(1)
            proba_alpha[1,1] = P_alpha2 = stats.norm.pdf(alpha2, 0, sigma_island)
                  #Second random draw
            proba_alpha[0,2] = P_alpha1/(P_alpha1+P_alpha2)
            proba_alpha[1,2] = P_alpha2/(P_alpha1+P_alpha2)
            zeta = rd.uniform(0, 1)
            proba_alpha[np.where(proba_alpha[:,2]==max(proba_alpha[:,2])),3] = 1  #->Determined the max and min proba
            
            if zeta<max(proba_alpha[:,2]): self.alpha[p] = proba_alpha[np.where(proba_alpha[:,3]==1),0][0]
            else: self.alpha[p] = proba_alpha[np.where(proba_alpha[:,3]==0),0][0]
            
            
    
    def __del__(self):
        """Methode pour supprimer le thon
        On met a jour le compteur de classe
        Et on sauvegarde dans un fichier toutes
        les informations sur la trajectoire du thon
        """
        Tuna.nb_tunas -= 1
        
      
    def __repr__(self):
        """Methode pour afficher l objet
        """
        return "Individual of Tuna class\n Correlated Random Walk: {}\n v: {} m/s\n m: {} %/day\n R0: {} km\n c: {}\n\n id:{}\n Lifetime: {} days\n Step: {}\n Position: [{},{}]".format(self.crw,
                                   Tuna.v,
                                   Tuna.m,
                                   Tuna.R0,
                                   Tuna.c,
                                   self.id,
                                   (self.lifetime*step_time)/(24*3600),
                                   self.p,
                                   self.x[self.p],
                                   self.y[self.p])
    
    def init_n():
        """ Reinitialise le nombre de thons crees"""
        Tuna.nb_tunas = 0
    
    
    def save(self, path_output, file_format, tuna_number):
        """Fonction sauvegardant la trajectoire du thon
        Arguments:
            - path_output: dossier dans lequel sera enregistre le fichier
            - file_format: format utilise pour enregistrer (soit csv soit npy)
            
        """
        
        tuna_traj = np.c_[self.x, self.y, self.alpha, self.theta, self.num_steps, self.num_asso_FAD]
        
        np.save(str(path_output)+"/Path_tuna/tuna_n"+str(tuna_number)+".npy", tuna_traj)
        if file_format[0]=="csv":
            np.savetxt(str(path_output)+"/Path_tuna/tuna_n"+str(tuna_number)+"."+file_format[0], tuna_traj)
            
            
        return "- Tuna trajectory saved"
      
        
    
    