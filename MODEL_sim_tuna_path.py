#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 26 09:50:25 2018

@author: geraldine

Modified on Feb 05 2021, by adupaix
"""

###############################################################################
#~~~~ Start the simulation ~~~~

for replica in range(Nreplica):
    if verbose==True:
        print("\nTuna n"+str(replica))
    begin_r = time.time()
    begin.append(time.time())
    
    tuna = Tuna(Npas, verbose = verbose, CRW = crw)

    ## First position -> fad in the middle of the array
    if environment == "square":
        diag_fad = FADs.id[FADs.x == FADs.y]
        fad_start = diag_fad[int(len(diag_fad)/2)]
    # Or FAD chosen randomly among FADs used for actual experimental release
    elif choose_fad_start == False:
        fad_start = rd.choice(FADs.id[FADs.of_release != 0])
    
    tuna.x[0] = FADs.x[FADs.id == fad_start]
    tuna.y[0] = FADs.y[FADs.id == fad_start]
    tuna.checkEnv(FADs)
    
    ##Start the tuna path (first step, from p=0 to p=1)
    tuna.alpha[0] = tuna.theta[0] = rd.uniform(0, 2*math.pi)
    
    tuna.x[1] = tuna.x[0] + math.cos(tuna.theta[0])*Tuna.l
    tuna.y[1] = tuna.y[0] + math.sin(tuna.theta[0])*Tuna.l
    tuna.p += 1
    tuna.p_since_asso += 1
    
    
    cpb_array = np.array([0]) #-> Check if replica go out of the L limit
    
    ## While p has not reached the lifetime, simulate tuna movement
    # tuna.p is incremented inside the OMove and CRWMove methods
    while tuna.p < tuna.lifetime-1 and tuna.nb_visit < nb_max_CAT+1:
        
        # check if the tuna is at more than R0 from a FAD, or at less than R0, or at less than the FAD detection radius
        ## the time machine in now called inside checkEnv
        tuna.checkEnv(FADs)
                
        ## Periodic condition on board + Add the last fad when tuna go out of its zo
        if tuna.x[tuna.p]>lims[1] or tuna.y[tuna.p]>lims[1] or tuna.x[tuna.p]<lims[0] or tuna.y[tuna.p]<lims[0]:
            cpb_array = np.hstack((cpb_array, 1))
            break
        
        ## For define the day/night behaviour change  
        if tuna.p%H24<H12: 
            DAY = 0
        else: 
            DAY = 1
        
        #~~~~
        ## BCRW -> All the cases when a tuna orients itself towards a FAD (only during daytime)
        # p_since_asso : number of steps since the last association, check if superior to one day
        if DAY==1 and tuna.in_R0_FAD!=0 and tuna.in_R0_FAD!=tuna.last_FAD_reinit_R0:
            
            # if the CAT is superior to one day or if it is a CAT diff
            # if tuna.p_since_asso > H24 or (tuna.p_since_asso <= H24 and tuna.in_R0_FAD!=tuna.last_FAD_no_reinit):
            tuna.OMove(FADs, CRTs)
            
            # if it's a CAT return of less than 24h, we go back in time !
            # elif tuna.p_since_asso <= H24 and tuna.in_R0_FAD==tuna.last_FAD_no_reinit:
                
                # tuna.in_the_time_machine()
                
        #~~~~
        ## CRW -> All the case where the tuna have a random search behaviour (research behaviour at night and away from FADs)
        else:
            
            if environment != "square" and environment !="maldives":
                tuna.checkLand(Island)
            elif environment == "maldives":
                for i in range(len(Island)):
                    tuna.checkLand(Island[i])
            
            # si repart d'un DCP, Random Walk simple
            if tuna.p_since_asso == 0:
                tuna.RWMove(FADs)
            # sinon, Correlated Random Walk
            else:
                tuna.CRWMove()
        
        
 
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## Save the array containing the tuna trajectory
    tuna.save(path_output = path_output, file_format = output_format, tuna_number = replica+1)
        
    
    end_r = time.time()
    if verbose == True:
        print("- t="+str(round(end_r-begin_r,2)))
    end.append(time.time())

