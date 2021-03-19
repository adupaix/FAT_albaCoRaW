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
    print("\nTuna n"+str(replica))
    begin_r = time.time()
    begin.append(time.time())
    
    tuna = Tuna(Npas, CRW = crw)

    ## First position -> fad in the middle of the array
    if environment == "square":
        diag_fad = FADs.id[FADs.x == FADs.y]
        fad_start = diag_fad[int(len(diag_fad)/2)]
    elif environment == "drifting":
        fad_start = rd.choice(FADs.id)
    # Or FAD chosen randomly among FADs used for actual experimental release
    else:
        fad_start = rd.choice(FADs.id[FADs.of_release != 0])
    
    
    tuna.x[0] = FADs.x[FADs.id == fad_start]
    tuna.y[0] = FADs.y[FADs.id == fad_start]
    tuna.checkEnv(FADs)
    
    ##Start the tuna path (first step, from p=0 to p=1)
    tuna.alpha[0] = tuna.theta[0] = rd.uniform(0, 2*math.pi)
    
    tuna.x[1] = tuna.x[0] + math.cos(tuna.theta[0])*Tuna.l
    tuna.y[1] = tuna.y[0] + math.sin(tuna.theta[0])*Tuna.l
    tuna.p += 1
    
    
    cpb_array = np.array([0]) #-> Check if replica go out of the L limit
    
    ## While p has not reached the lifetime, simulate tuna movement
    # tuna.p is incremented inside the OMove and CRWMove methods
    while tuna.p < tuna.lifetime-1:
        
        # check if the tuna is at more than R0 from a FAD, or at less than R0, or at less than the FAD detection radius
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
        if DAY==1 and tuna.in_R0_FAD!=0 and tuna.in_R0_FAD!=tuna.last_FAD:
            
            x_fadReached = FADs.x[FADs.id == tuna.in_R0_FAD]
            y_fadReached = FADs.y[FADs.id == tuna.in_R0_FAD]
            
            tuna.OMove(x_fadReached, y_fadReached, CRTs)
        #~~~~
        ## CRW -> All the case where the tuna have a random search behaviour (research behaviour at night and away from FADs)
        else:
            
            if environment != "square" and environment !="maldives" and environment !="drifting":
                tuna.checkLand(Island)
            elif environment == "maldives":
                for i in range(len(Island)):
                    tuna.checkLand(Island[i])
            
            tuna.CRWMove()
        
        
 
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## Save the array containing the tuna trajectory
    print(
    tuna.save(path_output = path_output, file_format = output_format, tuna_number = replica+1)
    )
    # nrow_end =  max(np.where(tunaPath_r[:,0]!=0)[0])
    # tunaPath_r = tunaPath_r[0:nrow_end,:]
    
    # nrow_start = max(np.where(tunaPath_array[:,0]!=0)[0])
    # nrow_end = nrow_start + len(tunaPath_r) 
    # tunaPath_array[(nrow_start+1):(nrow_end+1),:] = tunaPath_r 
    
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## PLOT
    if plot_tunaPath==True:
        fig=plt.figure(1) 
        fig, ax = plt.subplots(figsize=(10, 10)) #figsize=(longueur, hauteur)
        #> Plot axis
        plt.ylabel('y')
        plt.xlabel('x')
        plt.title(str(environment)+' '+str(studyYear)+' | $N_{FAD}$='+str(FADs.nFAD))
        plt.axis('equal')
        for i in range(0, int(FADs.nFAD)):
            fad_circle_oz=plt.Circle((FADs.x[i], FADs.y[i]), Tuna.R0, color='green', fill=False)
            ax.add_patch(fad_circle_oz)
        #> Plot FAD
        plt.plot(FADs.x[FADs.has_buoy], FADs.y[FADs.has_buoy], 'k+', label='Equiped FAD')
        #> Plot tuna path
        for step in np.arange(0, tuna.p, H12):
            if step%H24<H12: col="blue"
            else: col = 'red'
            if step==0: step=1
            plt.plot(tuna.x[(tuna.num_steps[:]>=step)&(tuna.num_steps[:]<=(step+H12))&(tuna.x[:]!=0)], 
                     tuna.y[(tuna.num_steps[:]>=step)&(tuna.num_steps[:]<=(step+H12))&(tuna.x[:]!=0)], 
                     "-", color=col, alpha=0.6)
            #plt.plot(tunaPath_r[0:(p-1), 0], tunaPath_r[0:(p-1), 1], 'k--', alpha=0.4, label='tuna path')
        #> Plot limit of the env
        # plt.plot(np.array([0,0,L,L,0]), np.array([0,L,L,0,0]), 'k-')
        #> Zoom
        if plot_zoom==True:
            dist_one_day = (tuna.v*3600*24)/1000 #distance parcourue en 1 jour
            interval = dist_one_day*path_duration/15 #distance parcourue sur l'ensemble du trajet / 15
            plt.xlim(tuna.x[0]-interval, tuna.x[0]+interval)
            plt.ylim(tuna.y[0]-interval, tuna.y[0]+interval)
    
    end_r = time.time()
    print("- t="+str(round(end_r-begin_r,2)))
    end.append(time.time())

