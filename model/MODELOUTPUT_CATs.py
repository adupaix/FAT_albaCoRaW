#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 09:21:51 2020

@author: geraldine

Modified on Apr 15 2021, by adupaix
"""


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ 1. DISTANCE BETWEEN FADs

# Calcul les distances entre FAD
#-----
# Methode de la class FAD array qui retourne une matrice de distances entre FADs
# Dans le cas d'un environnement reel, la matrice de distance est calculee une fois entre tous les DCP
# Dans le cas d'un environnement simule, la matrice de distance est calculee pour chaque replicat, uniquement
#   entre les DCP rencontres par le replicat. C'est un peu plus long, mais dans l'environnement theorique on
#   peut se retrouver avec 250 000 DCP, ce qui fait 62*10**9 elements dans la matrice. Donc ca serait
#   plus rapide avec quelques Tb de RAM, mais je ne les ai malheureusement pas...
if environment not in ["square", "random", "square_rd"]:
    distFAD_mat = FADs.distance_matrix()
    FADs_ids = FADs.id


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ 2. CALCULATE CAT AND CRT
cart_array = np.zeros([NREPLICA*10000, 9]) # array a remplir
nCAT = 0
for r in range(NREPLICA):
    
    tuna.load(path_output, r) 
        
    asso = np.where(tuna.num_asso_FAD!=0)[0]
    lead_asso = np.where(tuna.num_asso_FAD!=0)[0]+1
    lag_asso = np.where(tuna.num_asso_FAD!=0)[0]-1
    
    # tous les temps ou le thon commence une association avec un DCP
    start_asso = np.setdiff1d(asso, lead_asso)
    start_asso = start_asso[start_asso != 0]
    
    # tous les temps ou le thon termine une association avec un DCP
    end_asso = np.setdiff1d(asso, lag_asso)
    end_asso = end_asso[end_asso != np.max(tuna.num_steps)]
    
    if environment in ["square","random","square_rd"]:
        # get the list of the encountered FADs from the tuna object
        # and calculate the distances and the nearest neighbor (nn) number
        # distFAD_list contains 2 columns
        distFAD_list = FADs.distance_list(tuna, edge_dict)
    
    ## si le thon n'est pas associe au dernier pas de temps
    # c'est que le dernier temps complet dans la trajectoire est un CRT
    # donc on a autant de CAT que de CRT, donc supprime le dernier temps de fin d'association
    if tuna.num_asso_FAD[-1] == 0:
        rg = range(len(end_asso)-1)
    else: # sinon c'est un CAT, et on garde tous les temps
    # on a alors un CAT de plus que de CRT dans la traj
        rg = range(len(end_asso))
        
    for i in rg:
        # temps de debut du CAT i
        t1 = end_asso[i]
        # temps de fin du CAT i et de debut du CRT i
        t2 = start_asso[i]
        
        cat = ((t2-t1)*STEP_TIME)/(24*3600) #calcul le CAT (en jour)
        
        # DCP de depart
        fad1 = tuna.num_asso_FAD[t1]
        # DCP d'arrivee
        fad2 = tuna.num_asso_FAD[t2]        
        
        if environment in ["square","random","square_rd"]:
            dist = distFAD_list[i,0]
            nn_nb = distFAD_list[i,1]
        else:
            dist = distFAD_mat[np.where(FADs_ids == fad1), np.where(FADs_ids == fad2)] #recupere la distance entre les deux DCP
            nn_nb = np.where(np.sort(distFAD_mat[np.where(FADs_ids == fad1)]) == dist)[1]
            
        # save: id thon, tps depart, tps arrivee, dcp depart, dcp arrivee, cat, dist entre dcp, nn number, bollen "is a CAT" (1)
        cart_array[nCAT,:] = np.array([r+1, t1, t2, fad1, fad2, cat, float(dist), int(nn_nb),1])
        nCAT += 1
        if i != len(end_asso)-1:
            # temps de fin du CRT i
            t3 = end_asso[i+1]
            crt = ((t3-t2)*STEP_TIME)/(24*3600) # recalcul le CRT (en jour)
            cart_array[nCAT,:] = np.array([r+1, t2, t3, fad2, fad2, crt, 0,0,0]) # stock: id thon, tps depart, tps arrivee, dcp, dcp, crt, dist (0 c'est un CRT), nn number (0, did not move) bolleen "is a CAT" (0)
            nCAT += 1
        
        #### rajouter un tuna.save pour mettre a jour
        
delete_row = np.where(cart_array[:,0]==0)[0]
cart_array = np.delete(cart_array, delete_row, 0)

## Save the array containing CATs and CRTs

np.save(str(path_output)+"/CATs/CARTs_array.npy", cart_array)
if output_format[1]=="csv":
    np.savetxt(str(path_output)+"/CATs/CARTs_array."+output_format[1], cart_array)
    
## Save the array containing only the CATs
cat_array = cart_array[cart_array[:,8]!=0]
np.save(str(path_output)+"/CATs/CATs_array.npy", cat_array)
if output_format[1]=="csv":
    np.savetxt(str(path_output)+"/CATs/CATs_array."+output_format[1], cat_array)
    

