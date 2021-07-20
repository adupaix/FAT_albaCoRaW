#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 26 09:50:25 2018

@author: geraldine

Modified on Apr 15 2021, by adupaix
"""

###############################################################################
#~~~~ Start the simulation ~~~~

for replica in range(NREPLICA):
    if VERBOSE==True:
        print("\nTuna n"+str(replica))
    begin_r = time.time()
    begin.append(time.time())
    
    tuna = TUNA(Npas, verbose = VERBOSE, time_machine = TIME_MACHINE, CRW = crw)

    ## First position
    # If real array and choose_fad_start is False, FAD chosen randomly among FADs used for actual experimental release
    if CHOOSE_FAD_START == False and environment not in ["square", "random", "square_rd"]:
        fad_start = rd.choice(FADs.id[FADs.of_release != 0])
    # If random array, choose a FAD randomly in the array
    elif environment in ["random","square_rd"]:
        fad_start = rd.choice(FADs.id)
    
    tuna.x[0] = FADs.x[FADs.id == fad_start]
    tuna.y[0] = FADs.y[FADs.id == fad_start]
    tuna.checkEnv(FADs)
    
    ##Start the tuna path (first step, from p=0 to p=1)
    tuna.alpha[0] = tuna.theta[0] = rd.uniform(0, 2*math.pi)
    
    tuna.x[1] = tuna.x[0] + math.cos(tuna.theta[0])*TUNA.l
    tuna.y[1] = tuna.y[0] + math.sin(tuna.theta[0])*TUNA.l
    tuna.p += 1
    tuna.p_since_asso += 1
    
    
    ## While p has not reached the lifetime, simulate tuna movement
    # and while it has not reached the maximum number of associations wanted
    # tuna.p is incremented inside the OMove and CRWMove methods
    while tuna.p < tuna.lifetime-1 and tuna.nb_visit < NB_MAX_CAT+1:
        
        # check if the tuna is at more than R0 from a FAD, or at less than R0, or at less than the FAD detection radius
        # also check if it is not doing a CATreturn of less than 24h (time machine)
        tuna.checkEnv(FADs)
                
        ## Periodic condition on board
        if environment in ["square","random","square_rd"]:
            if tuna.x[tuna.p]>lims[1]:
                tuna.x[tuna.p] = tuna.x[tuna.p] - L
                tuna.edge[tuna.p] = 3
            elif tuna.y[tuna.p]>lims[1]:
                tuna.y[tuna.p] = tuna.y[tuna.p] - L
                tuna.edge[tuna.p] = 2
            elif tuna.x[tuna.p]<lims[0]:
                tuna.x[tuna.p] = tuna.x[tuna.p] + L
                tuna.edge[tuna.p] = 1
            elif tuna.y[tuna.p]<lims[0]:
                tuna.y[tuna.p] = tuna.y[tuna.p] + L
                tuna.edge[tuna.p] = 4
                
        ## For define the day/night behaviour change
        if tuna.p%H24<H12: 
            DAY = 0
        else: 
            DAY = 1
        
        #~~~~
        ## BCRW -> All the cases when a tuna orients itself towards a FAD (only during daytime)
        if DAY==1 and tuna.in_R0_FAD!=0 and tuna.in_R0_FAD!=tuna.last_FAD_reinit_24h:
            
            tuna.OMove(FADs, CRTs)
            
                
        #~~~~
        ## CRW -> All the cases where the tuna have a random search behaviour (research behaviour at night and away from FADs)
        else:
            
            # if it's a simulation in a real environment, check if there is land around
            if environment != "square" and environment !="maldives" and environment != "random" and len(land_files) > 0:
                tuna.checkLand(Island)
            elif environment == "maldives":
                for i in range(len(Island)):
                    tuna.checkLand(Island[i])
            
            # if leaves a FAD, simple Random Walk
            if tuna.p_since_asso==0 and tuna.x[tuna.p] == FADs.x[FADs.id == tuna.in_R0_FAD] and tuna.y[tuna.p] == FADs.y[FADs.id == tuna.in_R0_FAD] and SRW_WHEN_DEPART == True:
                tuna.RWMove(FADs)
            # else, Correlated Random Walk
            else:
                tuna.CRWMove()
        
        
 
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## Save the array containing the tuna trajectory
    tuna.save(path_output = path_output, file_format = output_format, tuna_number = replica+1)
        
    
    end_r = time.time()
    if VERBOSE == True:
        print("- t="+str(round(end_r-begin_r,2)))
    end.append(time.time())

