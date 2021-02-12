#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 09:21:51 2020

@author: geraldine
"""


# lossRate_array = np.load(str(path_machine)+"/modelOutput/"+environment+"_DN_cutPath"+str(path_duration)+"_v"+str(v)+"_m"+str(m)+"_Ro"+str(Ro_km)+"_c"+str(c)+".npy")


#> Open environment
# if environment=="square":
#     fadArray = np.load(path_machine+"/FAD_coor_"+environment+"_distFAD"+str(distFAD_km)+".npy")
#     tunaPath_array = np.load(path_machine+"/modelOutput/"+environment+"_tunaPath_v"+str(v)+"_m0.0_distFAD"+str(distFAD_km)+"_Ro"+str(Ro_km)+"_c"+str(c)+".npy")
# else:
#     fadArray = np.load(path_machine+"/FAD_coor_"+environment+".npy") 
#     tunaPath_array = np.load(path_machine+"/modelOutput/"+environment+"_DN_tunaPath_v"+str(v)+"_m0.0_Ro"+str(Ro_km)+"_c"+str(c)+".npy")



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
if environment != "square":
    distFAD_mat = FADs.distance_matrix()
    FADs_ids = FADs.id


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ 3. BUILD CAT    
cat_array = np.zeros([Nreplica*100, 7]) # array a remplir
nCAT = 0
for r in range(Nreplica):
    tunaPath_array = np.load(os.path.join(path_output,"Path_tuna","tuna_n"+str(r+1)+".npy"))
    tunaPath_r_cat = tunaPath_array[tunaPath_array[:,5]!=0,:] # garde uniquement les lignes ou le thon est associe
    
    if environment == "square":
        # get the list of the encountered FADs
        array_FADs = np.unique(tunaPath_array[:,-1])
        array_FADs = array_FADs[array_FADs != 0]
    
        # calculate the distance between these FADs
        distFAD_mat = FADs.distance_matrix(array_FADs)
        
        FADs_ids = array_FADs
    
    for i in range(len(tunaPath_r_cat)-1): #pour chaque pas de temps associe a un DCP, regarde le suivant
        t1 = tunaPath_r_cat[i, 4]
        fad1 = tunaPath_r_cat[i, 5]
        t2 = tunaPath_r_cat[i+1, 4]
        fad2 = tunaPath_r_cat[i+1, 5]

         # si ca change de DCP, ou s'il s'ecoule plus de 24h entre les deux detections, c'est un CAT
        if fad1!=fad2 or (fad1==fad2 and t2-t1>H24):
            nstep = tunaPath_r_cat[i+1, 4] ### ???
            cat = ((t2-t1)*step_time)/(24*3600) #calcul le CAT (en jour)
            dist = distFAD_mat[np.where(FADs_ids == fad1), np.where(FADs_ids == fad2)] #recupere la distance entre les deux DCP
            cat_array[nCAT,:] = np.array([r+1, t1, t2, fad1, fad2, cat, float(dist)]) # stock: id thon, tps depart, tps arrivee, dcp depart, dcp arrivee, cat, dist entre dcp
            nCAT = nCAT+1
        
delete_row = np.where(cat_array[:,0]==0)[0]
cat_array = np.delete(cat_array, delete_row, 0)

## Save the array containing CATs

np.save(str(path_output)+"/CATs/CATs_array.npy", cat_array)
if output_format[1]=="csv":
    np.savetxt(str(path_output)+"/CATs/CATs_array."+output_format[1], cat_array)
    



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ 4. MAKE THE CAT FOR THE COMPARISON WITH ACTUAL DATA
# if addCRTs==True:
#     #~ 4.1. Add the CRT
#     #> Open model output and delete CATreturn<24h
#     model_cat = cat_array
#     # ajout de deux colonnes
#     model_cat = np.append(model_cat, np.zeros([len(model_cat), 1]), axis=1)
#     model_cat = np.append(model_cat, np.zeros([len(model_cat), 1]), axis=1)
    
#     CATCRT_array = np.zeros([1, model_cat.shape[1]])
#     for replica in replica_array: 
#         model_cat_replica = model_cat[model_cat[:,0]==replica,:]
        
#         if len(model_cat_replica)==0:
#             crt_toadd = 0
#             model_cat_replica = np.zeros((1,9))
#             model_cat_replica[0, 0] = replica
#             model_cat_replica[0, 7] = crt_toadd
#             model_cat_replica[0, 8] = crt_toadd
#         else:
#             #> Choice the crt to add
#             ncat_replica = len(model_cat_replica)
#             crt_toadd = np.repeat(0, ncat_replica+1)
#             crt_toadd_cumsum = np.cumsum(crt_toadd)
            
#             #> Add a row to add the last CRT
#             model_cat_replica = np.append(model_cat_replica, np.zeros([1, model_cat.shape[1]]), axis=0)
#             model_cat_replica[:,0] = replica        
#             model_cat_replica[:, 8] = crt_toadd
            
#             #> Add these crt in the path
#             cat_cumsum = np.cumsum(model_cat_replica[:, 5]) 
#             p_array = cat_cumsum + crt_toadd_cumsum
#             model_cat_replica[:, 7] = p_array     
        
#         #> Save array
#         CATCRT_array = np.append(CATCRT_array, model_cat_replica, axis=0)
        
#         #> Select the tuna path according to the parameters
#         tunaPath_array = CATCRT_array
        
#         #> Add a column to point the CAT0
#         tunaPath_array = np.append(tunaPath_array, np.zeros([len(tunaPath_array), 1]), axis=1)
# else:
#     #> Select the tuna path according to the parameters
#     tunaPath_array = cat_array
#     #> Add a column to point the CAT0
#     tunaPath_array = np.append(tunaPath_array, np.zeros([len(tunaPath_array), 3]), axis=1)
     


#~ 4.2. Cut according to the loss rate
#> The cut values
# p_cut_array = lossRate_array 
# p_cut_array = np.append(p_cut_array, np.zeros([len(p_cut_array), 1]), axis=1)
# p_cut_array[:,2] = (p_cut_array[:,1]*step_time)/(24*3600)
    
# CAT0_array = np.zeros([Nreplica2+1, 3])
# for replica in replica_array:
#     tunaPath = tunaPath_array[tunaPath_array[:,0]==replica,:]     
#     p_cut = p_cut_array[p_cut_array[:,0]==replica, 2]
#     delete_row = tunaPath[tunaPath[:,7]>p_cut, :]
       
#     if len(delete_row)==0:
#         #> Calculate the CAT0/CATpartial
#         CAT0 = path_duration - tunaPath[len(tunaPath)-1, 7] + tunaPath[len(tunaPath)-1, 5]
#         CAT0_array[int(replica),:] = np.array([replica, CAT0, 1]) 
#         tunaPath[len(tunaPath)-1, 9] = 1 #to know where there are the CAT0
#         tunaPath[len(tunaPath)-1, 2] =  Npas #p_cut_array[p_cut_array[:,0]==replica, 1]
#         #> Save in the big array 
#         tunaPath_array[tunaPath_array[:,0]==replica, :] = tunaPath
    
#     else:
#         if len(delete_row)>1:
#             #> Delete the events that take place afer the cut du to the Ploss
#             delete_row_num = np.where((tunaPath_array[:,0]==replica) & (tunaPath_array[:,7]>p_cut))[0]
#             tunaPath_array = np.delete(tunaPath_array, delete_row_num[1: len(delete_row_num)], axis=0)
#             tunaPath = tunaPath_array[tunaPath_array[:,0]==replica,:] 
#             delete_row = tunaPath[tunaPath[:,7]>p_cut, :]
    
#         #> Cut the CATdiff or the CRT according to the p_cut/Ploss
#         tocut = tunaPath[len(tunaPath)-1,7] - p_cut
#         last_CATdiff = tunaPath[len(tunaPath)-1, 5]
        
#         #> Cut the CRT, so do not create CAT0
#         if last_CATdiff < tocut:
#             tunaPath[len(tunaPath)-1, 7] = tunaPath[len(tunaPath)-1, 7] - tocut #cut the cumsum of CAT and CRT in days 
#             tunaPath[len(tunaPath)-1, 5] = 0 #last CATdiff delete
#             tocut = tocut - last_CATdiff # the rest to cut after delete the last CAT
#             tunaPath[len(tunaPath)-1, 8] = tunaPath[len(tunaPath)-1, 8] - tocut #cut the last CRT, so no CAT0 in this case
#             tunaPath[len(tunaPath)-1, 2] = p_cut_array[p_cut_array[:,0]==replica, 1] #cut the cumsum of CAT et CRT in step                
#             tunaPath[len(tunaPath)-1, 9] = 2 #To know that there are not a CAT at the and but the last CRT weas cut
#             if p_cut==0: 
#                 tunaPath[len(tunaPath)-1, 1:8] = 0
#                 tunaPath[len(tunaPath)-1, 9] = 1
#                 CAT0_array[int(replica),:] = np.array([replica, path_duration, 2])
#             else: 
#                 CAT0 = path_duration - tunaPath[len(tunaPath)-1, 7]
#                 print(CAT0)
#                 CAT0_array[int(replica),:] = np.array([replica, CAT0, 3])
#         #> Cut the last CATdiff, so create a CAT0
#         else:
#             tunaPath[len(tunaPath)-1, 5] = tunaPath[len(tunaPath)-1, 5] - tocut
#             tunaPath[len(tunaPath)-1, 7] = tunaPath[len(tunaPath)-1, 7] - tocut
#             tunaPath[len(tunaPath)-1, 2] =  p_cut_array[p_cut_array[:,0]==replica, 1]
#             tunaPath[len(tunaPath)-1, 9] = 1 #to know where there are the CAT0
#             CAT0 = path_duration - tunaPath[len(tunaPath)-1, 7] + tunaPath[len(tunaPath)-1, 5]
#             CAT0_array[int(replica),:] = np.array([replica, CAT0, 4])
        
#         #> Save in the big array 
#         tunaPath_array[tunaPath_array[:,0]==replica, :] = tunaPath
        
   

# #> Save CAT0
# CAT0_array = np.delete(CAT0_array, 0, 0)
# if environment=="square":
#     np.save(str(path_machine)+"/modelOutput/"+environment+"_CAT0_v"+str(v)+"_m0.0_distFAD"+str(distFAD_km)+"_Ro"+str(Ro_km)+"_c"+str(c)+".npy", tunaPath_array)
# else:
#     np.save(str(path_machine)+"/modelOutput/"+environment+"_DN_CAT0_v"+str(v)+"_m0.0_Ro"+str(Ro_km)+"_c"+str(c)+".npy", tunaPath_array)


# #> Save the CAT(CRT)
# tunaPath_array = np.delete(tunaPath_array, np.array([1,2]), axis=1)
# if environment=="square":
#     np.save(str(path_machine)+"/modelOutput/"+environment+"_CATs_v"+str(v)+"_m0.0_distFAD"+str(distFAD_km)+"_Ro"+str(Ro_km)+"_c"+str(c)+".npy", tunaPath_array)
# else:
#     np.save(str(path_machine)+"/modelOutput/"+environment+"_DN_CATs_v"+str(v)+"_m0.0_Ro"+str(Ro_km)+"_c"+str(c)+".npy", tunaPath_array)


