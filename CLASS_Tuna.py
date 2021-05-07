# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 15:39:26 2021

Definition de la classe TUNA

@author: adupaix
"""


class TUNA:
    """ Classe definissant un thon par :
        - son numero d'id (id)
        - sa duree de vie (lifetime)
        - sa position geographique (x et y)
        - ses angles alpha et theta
        - son pas de temps actuel (p)
        - in_R0_FAD: boleen pour savoir si le thon est a moins de R0 d'un DCP
        - num_asso_FAD: suivi des associations (pour chaque pas de temps, 0 si pas detecte par un DCP, num du DCP sinon)
        - last_FAD_*:   numero du DCP qui vient d'etre visite, pour ne pas revenir en arriere et pour detecter les CATret<24h
                        3 paramètres réinitialisés à différents moments
        - p_since_asso: nombre de pas de temps depuis la dernière association à un DCP, permet de revenir en arrière dans le temps
        - nb_visit: nombre de DCP visités. Permet d'arreter la simulation si on ne veut qu'un seul CAT par exemple
        - verbose: paramètre pour savoir si on affiche les messages
        - crw: determine si le thon se déplace en CRW ou en ligne droite (quand c = 1)
        
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
    step_m = ((m / 100 ) * STEP_TIME)/(24*3600) #mortality rate per time step
    
    
    ### ~~~ INITIALISATION D'UN THON
    ##------------------------------
    
    def __init__(self, Npas, verbose, time_machine, CRW = True):
        """ On definit tous les attributs
        
        Besoin de specifier Npas, pour limiter la duree de vie
        
        """
        
        TUNA.nb_tunas += 1
        
        self.id = TUNA.nb_tunas
        
        ## Parametres d'etat
        self.lifetime = TUNA.lifetime(Npas)
        self.x = np.zeros(self.lifetime)
        self.y = np.zeros(self.lifetime)
        
        ## genere tous les alpha des l'initialisation du thon, a partir d'une loi normale tronquee
        # moyenne: 0, sd: sigma, tronquee a -pi et pi
        # cf. https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.truncnorm.html
        if CRW == True:
            self.alpha = truncnorm.rvs((-math.pi) / TUNA.sigma, (math.pi) / TUNA.sigma, loc=0, scale=TUNA.sigma, size = self.lifetime)
        else:
            self.alpha = np.zeros(self.lifetime)
            TUNA.c = 1
            TUNA.sigma = 0
            
        self.theta = np.zeros(self.lifetime)
        # self.t = 0 #timestamp in s (initial time = 0)
        
        self.in_R0_FAD = 0 # tuna is at a distance < R0 from a FAD or not (0: no FAD, other: number of the FAD)
        
        self.num_asso_FAD = np.zeros(self.lifetime) # a chaque tour, stock 0 (pas d'association) ou x = identifiant du DCP auquel le thon est associe
        self.last_FAD_reinit_R0 = 0 #numero du dernier DCP auquel le thon s'est associe, se remet a 0 quand on sort du R0
        self.last_FAD_reinit_dr = 0 #numero du dernier DCP auquel le thon s'est associe, se remet a 0 quand on sort du rayon de detection
        self.last_FAD_no_reinit = 0 #numero du dernier DCP auquel le thon s'est associe, mais qui ne se remet pas a 0 pas quand on sort du R0 du DCP
        
        self.p = 0 # numero du pas de temps où en est le thon
        self.num_steps = np.array(range(self.lifetime)) # numero des pas de temps stockes (parallele aux autres donnees) Sert pour le plot
        
        self.crw = crw #si le thon (hors association) se déplace en marche aléatoire correlée. False quand on veut explorer la condition
        # extreme c = 1 (le thon se déplace en ligne droite)
        
        self.p_since_asso = 0 #compteur pour connaitre le nombre de pas depuis la derniere association.
        # permet de revenir en arriere en cas de CAT de moins de 24h
        
        self.nb_visit = 0 #compteur du nombre de DCP visites par le thon. Permet d'arreter la trajectoire plus tot si on ne veut considérer
        # que le premier CAT par exemple
        
        self.verbose = verbose #determine si on affiche des elements pendant la simulation
        
        self.time_machine = time_machine #determine si le thon revient en arriere dans le temps quand il fait un CATret<24h

    
    def lifetime(Npas):
        """A l'initialisation du thon
        on calcul sa duree de vie"""
        
        if TUNA.m == 0:
            return Npas-1
        else:
            k=1
            r_mortality = rd.random()
            while r_mortality > TUNA.step_m and k<=Npas-1:
                k += 1
                r_mortality = rd.random()
            
            return(k)
    
    
    
    ### ~~~ METHODES SUR LES PARAMETRES DE CLASSE
    ##-------------------------------------------
    
    def change_c(new_c):
        """Fonction pour modifier le coeff
        de sinuosite c. Change en meme temps
        le sigma
        """
        TUNA.c = new_c
        if new_c != 1:
            TUNA.sigma = math.sqrt(-2*math.log(new_c))
        else:
            TUNA.sigma = 0
                
    def change_m(new_m):
        """Methode pour modifier le taux
        de mortalite m. Change en meme temps
        le step_m
        """
        TUNA.m = new_m
        TUNA.step_m = ((new_m / 100 ) * STEP_TIME)/(24*3600)
    
    
    ### ~~~ METHODES DE MOUVEMENT DES THONS
    ##-------------------------------------
    
    def CRWMove(self):
        """
        On change la position du thon dans le cas
        d'un Correlated Random Walk
        i.e. si le thon ne va pas vers un DCP
        """
        
        p = self.p
        
       
        ## CRW -> random search behaviour: Determine the next position
        # Rappel: alpha est initialise des le debut, on va juste chercher la valeur contenue dans l'array
        self.theta[p] = self.alpha[p] + self.theta[p-1]
        
        
        if self.theta[p] > math.pi:
            self.theta[p] = self.theta[p] - (2*math.pi)
        elif self.theta[p] < (-math.pi):
            self.theta[p] = self.theta[p] + (2*math.pi)
                
        
        self.x[p+1] = self.x[p] + math.cos(self.theta[p])*TUNA.l
        self.y[p+1] = self.y[p] + math.sin(self.theta[p])*TUNA.l
        
        self.p += 1
        self.p_since_asso += 1
        
        
    def RWMove(self, FADs):
        """
        On change la position du thon dans le cas
        d'un Random Walk simple
        i.e. si le thon REPART d'un DCP
        on choisi un angle aleatoire,
        et soit :
            - on replace le thon sur le cercle de rayon dr 
                (dans le cas où on ajoute des CRTs et que le DCP est équipé)
            - le thon se déplace de TUNA.l (quand on n'ajoute pas de CRT)
        """
        
        p = self.p
        
        self.theta[p] = rd.uniform(-math.pi, math.pi)
        
        if ADD_CRTS == True and LEAVE_AT_DR == True:
            self.x[p+1] = self.x[p] + math.cos(self.theta[p]) * max(FADs.dr[np.where(FADs.id == self.num_asso_FAD[p])] , TUNA.l)
            self.y[p+1] = self.y[p] + math.sin(self.theta[p]) * max(FADs.dr[np.where(FADs.id == self.num_asso_FAD[p])] , TUNA.l)
        else:
            self.x[p+1] = self.x[p] + math.cos(self.theta[p]) * TUNA.l
            self.y[p+1] = self.y[p] + math.sin(self.theta[p]) * TUNA.l
            
        self.p += 1
        self.p_since_asso += 1
    
        
    def add_res_time(self, CRTs, x_fadReached, y_fadReached):
        """
        Dans le cas ou add_CRTs est vrai
        on prend un CRT au hasard dans la liste fournie
        et le thon attend ce temps sous le DCP
        
        Les CRT fournis doivent être en jour
        """
        crt_day = rd.choice(CRTs)
        
        crt_steps = int(crt_day * 24 * 3600 / STEP_TIME)
        
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
            if self.verbose == True:
                print("  Warning: Not enough steps to add CRT")
            
        self.p += crt_steps
        self.p_since_asso += crt_steps
        
        
        
    def OMove(self, FADs, CRTs):
        """
        On change la position du thon dans le cas
        d'un Oriented Movment
        i.e. si le thon est a moins de R0 d'un DCP + c'est le jour
        """
        
        p = self.p
        
        x_fadReached = FADs.x[FADs.id == self.in_R0_FAD]
        y_fadReached = FADs.y[FADs.id == self.in_R0_FAD]
        
        dist_tunaFAD = math.sqrt((y_fadReached-self.y[p])**2
                                 +(x_fadReached-self.x[p])**2)
        
            ## Go in straigth line towards the next position
        nstep_jump = round(dist_tunaFAD/TUNA.l)
                
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
            self.x[p + steps_left] = self.x[p] + math.cos(self.theta[p])*TUNA.l*(steps_left)
            self.y[p + steps_left] = self.y[p] + math.sin(self.theta[p])*TUNA.l*(steps_left)
            if self.verbose == True:
                print("  Warning: Not enough steps to reach last FAD")
     
        self.p += nstep_jump
        
        self.p_since_asso += nstep_jump
        
        if ADD_CRTS == True and p+nstep_jump < self.lifetime:
            if self.in_R0_FAD == self.last_FAD_no_reinit and self.p_since_asso < H24 and self.last_FAD_reinit_dr == 0 and self.time_machine == True:
                TUNA.in_the_time_machine(self)
            # print("  adding CRT")
            else:
                TUNA.add_res_time(self, CRTs, x_fadReached, y_fadReached)
            
    
    ### ~~~ METHODES DE VERIFICATION DE L'ENVIRONNEMENT DU THON
    ##---------------------------------------------------------
    
    def in_the_time_machine(self):
        '''
        Revient en arriere dans le temps, dans le cas
        d'un  CAT return < 24h
        
        Tire aleatoirement un nouveau set d'alpha (entre l'association et le debut du retour)
        car ils sont tous determines a l'initialisation du thon
        '''
        if self.verbose == True:
            print("  Time machine: p: "+str(self.p)+" ; back "+str(self.p_since_asso)+" steps")
            print("    Last FAD: "+str(self.num_asso_FAD[self.p-self.p_since_asso])+" ; present FAD "+str(self.last_FAD_no_reinit))
        
        self.p -= self.p_since_asso
        
        self.last_FAD_reinit_R0 = self.last_FAD_no_reinit
        self.last_FAD_reinit_dr = self.last_FAD_no_reinit
        
        self.alpha[self.p:(self.p+self.p_since_asso+1)] = truncnorm.rvs((-math.pi) / TUNA.sigma, (math.pi) / TUNA.sigma, loc=0, scale=TUNA.sigma, size = self.p_since_asso+1)
        
        self.p_since_asso = 0
        
        
        
    def checkEnv(self, FADs):
        '''
        FADs: environnement en objet flottant de classe FAD_Array
        
        Utilise la position du thon pour déterminer si:
            - le thon est associe a un DCP
            - le thon est dans le R0 d'un DCP
            - le thon revient à un DCP visité il y a moins de 24h (CATret<24h)
                dans ce cas là, revient en arriere dans le temps
        
        Les indices renseignes sont utilises comme suit:
            - in_R0_FAD: permet de savoir si le thon detecte un DCP (distance < R0)
            
            - num_asso_FAD: array avec a chaque pas de temps le numero du DCP
                auquel le thon est associe (ou 0 si pas d'association)
                il change quand le thon entre et sort du detection_radius du DCP
                Permet ensuite de calculer les CAT
            
            - last_FAD_reinit_R0: numero du dernier DCP rencontre. Permet que le thon ne revienne
                pas en arriere systematiquement quand il vient de s'associer avec un DCP
                prend le numero du DCP quand rentre dans son detection_radius, reprend la 
                valeur 0 quand il ressort du R0
            -last_FAD_reinit_dr: comme last_FAD_reinit_R0, mais reinitialisé si le thon est hors
                du dr
            -last_FAD_no_reinit: idem ci-dessus, mais jamais reinitialisé
                
                ATTENTION NE FONCTIONNE QUE SI distance entre DCP > R0
        '''
        p = self.p
        
        #calcul la distance entre le thon et les DCP (test en delimitant un carre autour du thon: plus long)
        dist_ft = np.sqrt((FADs.x[:]-self.x[p])**2 + (FADs.y[:]-self.y[p])**2)
        # enregistre l'identifiant du DCP detecte. Si pas de DCP dans un rayon de moins de R0, detected_Fad est vide
        detected_FAD = FADs.id[dist_ft <= TUNA.R0]
        # idem qu'au dessus, mais avec le rayon detection_radius, du DCP
        associated_FAD = FADs.id[dist_ft <= FADs.dr]
        
        if len(detected_FAD) == 0: #s'il n y a pas de DCP detecte par le thon, on met 0 dans in_R0_FAD et on reinitialise last_FAD_reinit_R0
            self.in_R0_FAD = 0
            self.last_FAD_reinit_R0 = 0
        elif len(detected_FAD) == 1: #s'il y a un seul DCP detecte, on met son numero dans in_R0_FAD
            self.in_R0_FAD = detected_FAD
        else: #s'il y a plusieurs DCP detectes, on en choisi un au hasard
            self.in_R0_FAD = np.random.choice(detected_FAD[detected_FAD != self.last_FAD_reinit_R0])
            
            
        if len(associated_FAD) != 0: # si on est dans le rayon de detection (dr)
            if associated_FAD == self.last_FAD_no_reinit and self.p_since_asso < H24 and self.last_FAD_reinit_dr == 0 and self.time_machine == True:
                #on verifie si c'est le meme DCP que la fois d'avant et qu'on l'a visite il y a moins de 24h
                #si c'est le cas, on revient en arriere
                TUNA.in_the_time_machine(self)
            else: #sinon:
                if FADs.dr[dist_ft <= FADs.dr]!=0: # on verifie que le dr du DCP n'est pas nul (S'il est nul, c'est que le DCP n'est pas equipe)
                    self.num_asso_FAD[p] = associated_FAD #et on enregistre la detection du thon
                    if not self.num_asso_FAD[p-1] == associated_FAD:
                        self.nb_visit +=1
            # dans tous les cas, que le DCP soit equipe ou non, on veut le meme comportement du thon, donc on enregistre le numero dans les last_FAD
            # et il est associe au DCP, donc on remet p_since_asso a 0
                self.last_FAD_reinit_R0 = associated_FAD
                self.last_FAD_reinit_dr = associated_FAD
                self.last_FAD_no_reinit = associated_FAD
                self.p_since_asso = 0
        else: # si on n'est pas dans le rayon de detection d'un DCP
            # on reinitialise 
            self.last_FAD_reinit_dr = 0
            self.num_asso_FAD[p] = 0
        
        
    def checkLand(self, Island):
        """
        Methode utilisee dans les simulations dans les
        environnement reels, pour recalculer alpha de maniere a
        ce que le thon n'aille pas sur terre
        """
        
        p = self.p
        
        can_reach_land = Point(np.r_[self.x[p],self.y[p]]).buffer(TUNA.l).intersects(Island.line)
        
        if can_reach_land:
            
            # build the circle around the tuna position
            start_angle, end_angle = 0, 360 # In degrees -> to have a complete ring
            numsegments = 1000
            ## The coordinates of the arc
            theta = np.radians(np.linspace(start_angle, end_angle, numsegments))
            x = self.x[p] + TUNA.l * np.cos(theta)
            y = self.y[p] + TUNA.l * np.sin(theta)
            arc = geom.LineString(np.c_[x, y])
            
            # get the two intersects with the land
            pos1 = list(arc.intersection(Island.line)[0].coords)[0]
            pos2 = list(arc.intersection(Island.line)[1].coords)[0]
            
            # get the alpha angles corresponding to these 2 intersects
            theta2_pos1 = math.asin((pos1[1]-self.y[p])/TUNA.l)  
                    ##If go back to the principale coordinate of the plan
            if pos1[0]<self.x[p]: theta2_pos1 = -math.pi - math.asin((pos1[1]-self.y[p])/TUNA.l)
            alpha_pos1 = theta2_pos1 - self.theta[p-1]
                    #If over trigonometric circle
            if alpha_pos1>math.pi: alpha_pos1 = alpha_pos1 - (2*math.pi)
            if alpha_pos1<-math.pi: alpha_pos1 = alpha_pos1 + (2*math.pi)
                        #-> POSITION 2                        
            theta2_pos2 = math.asin((pos2[1]-self.y[p])/TUNA.l) 
                    ##If go back to the principal coordinate of the plan
            if pos2[0]<self.x[p]: theta2_pos1 = -math.pi - math.asin((pos1[1]-self.y[p])/TUNA.l)
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
            
            
    ### ~~~ METHODES POUR REPRESENTER ET SAUVEGARDER LE THON
    ##------------------------------------------------------
      
    def __repr__(self):
        """Methode pour afficher l objet
        """
        return "Individual of TUNA class\n\n Correlated Random Walk: {}\n v: {} m/s\n m: {} %/day\n R0: {} km\n c: {}\n\n id:{}\n Lifetime: {} days\n Step: {}\n Position: [{},{}]\n\n Talkative: {}\n Time traveler: {}".format(self.crw,
                                   TUNA.v,
                                   TUNA.m,
                                   TUNA.R0,
                                   TUNA.c,
                                   self.id,
                                   (self.lifetime*STEP_TIME)/(24*3600),
                                   self.p,
                                   self.x[self.p],
                                   self.y[self.p],
                                   self.verbose,
                                   self.time_machine)   
    
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
            
        if self.verbose == True:   
            print("- Tuna trajectory saved")
      
        
    
    