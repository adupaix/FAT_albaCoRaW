### Interpolation buoy trajectory for one csv file

library(dplyr)
library(tidyr)
library(pracma)
library(progress)

DATA_PATH <- "/media/adupaix/DD_Dupaix1/Data/Echodata/Processed/2020/Final_Filtered_Data/"
OUTPUT_PATH <- "/home/adupaix/Documents/CRW/CRW_model/files/"

buoysList <- list.files(DATA_PATH)

cat("\14")
cat("~~~ Interpolation of buoys trajectories ~~~\n\n")

xmin = 45
xmax = 65
ymin = -10
ymax = 5

interpolation_method = "linear"

timestep = 100 #seconds
path_duration = 120 #days
n_steps_per_file = 10000

# !!! must be equal to N * timesteps with N integer !!!
interpolation_time = 12 #hours

RESET = T

tuna_release_date = as.POSIXct("2020-01-01 12:00:00")

# tuna_position_date: ensemble des timestamps pour lesquels on veut les positions des DCP
tuna_position_date <- seq(from = tuna_release_date,
                          to = tuna_release_date + as.difftime(path_duration, units = "days"),
                          by = timestep)
tuna_position_date %>% as.data.frame() %>% mutate(timestep = seq(from = 0,
                                                                 by = 1,
                                                                 length.out = length(tuna_position_date))) -> total_timesteps

### On reconstruit les trajectoires en prenant en plus les donnees 12h avant et apres les dates d'interets
### pour etre surs d'avoir tous les points au moment du depart
### sinon on commence a interpoler a partir de la premiere emission de la balise (ie un peu apres le depart)
# interpolation_date: ensemble des timestamps de l'interpolation
interpolation_time = as.difftime(interpolation_time, units = "hours")
interpolation_date <- seq(from = tuna_release_date - interpolation_time,
                          to = tuna_release_date + as.difftime(path_duration, units = "days") + interpolation_time,
                          by = timestep)

# Create output files (they will be appended in the "for" bellow)
steps_for_files <- seq(from = 0, to = length(tuna_position_date)-1, n_steps_per_file) # to generate file names
dir.create(file.path(OUTPUT_PATH, "drifting_fadArray"), showWarnings = F) #create the main directory

existing_files <- list.files(file.path(OUTPUT_PATH, "drifting_fadArray")) #if the directory is not empty, delete files
if (RESET == T){
  unlink(file.path(OUTPUT_PATH, "drifting_fadArray", existing_files))
}


# ~~~~ Sub-function to save files
var_names <- c("x","y","id")
col_names <- c("longitude", "latitude", "FAD_id")

save.csv.traj <- function(var_names, col_names, k, steps_for_files){
  
  interp_data %>%
    dplyr::filter(timestep >= steps_for_files[k] & timestep < steps_for_files[k+1]) -> data.k
  
  for (i in 1:length(var_names)){
    write.table(round(t(data.k[,col_names[i]]), digits = 5),
                file = file.path(OUTPUT_PATH, "drifting_fadArray",
                                 paste0("FADs.",var_names[i],"_", format(steps_for_files[k], scientific = F),
                                        "to",
                                        format(steps_for_files[k+1]-1, scientific = F),
                                        ".csv")),
                sep = ",", append = T, row.names = F, col.names = F
    )
  }
  
  
}


# header = c("longitude","latitude","position_date","timestep", "FAD_id","\n")


# create the output files
# for (j in 1:length(var_names)){
# for (k in 1:(length(steps_for_files)-1)){
#   
#       file.create(file.path(OUTPUT_PATH, "drifting_fadArray",
#                         paste0(var_names[j],format(steps_for_files[k], scientific = F),
#                                "to",
#                                format(steps_for_files[k+1]-1, scientific = F),
#                                ".csv")))
#       
# }
# 
#     file.create(file.path(OUTPUT_PATH, "drifting_fadArray",
#                      paste0(var_names[j],format(steps_for_files[length(steps_for_files)]-1, scientific = F),
#                             "to",
#                             format(length(tuna_position_date), scientific = F),
#                             ".csv"))
# )
# }
# file.create(file.path(OUTPUT_PATH, "drifting_fadArray", "FADs.x.csv"),
#             file.path(OUTPUT_PATH, "drifting_fadArray", "FADs.y.csv"),
#             file.path(OUTPUT_PATH, "drifting_fadArray", "FADs.id.csv"))


#Initialize progress bar
pb <- progress_bar$new(
  format = "Buoy: :id_buoy [:bar] :current / :n_buoys",
  total = length(buoysList)
)

# Create summary
buoysSummary <- data.frame(matrix(ncol = 5, nrow = length(buoysList)))
names(buoysSummary) <- c("buoy_id", "FAD_id", "is_notEmpty", "is_inAreaOfInterest", "is_inPeriodOfInterest")

for (i in 1:length(buoysList)){
  
  # tick progress bar
  pb$tick(tokens = list(id_buoy = buoysList[i],
                        current = i,
                        n_buoys = length(buoysList)))
  
  if( file.exists(file.path(DATA_PATH,buoysList[i],"buoys_data_location_filtered.RData")) ){
    
    # load RData
    load(file.path(DATA_PATH,buoysList[i],"buoys_data_location_filtered.RData"))
    
    if(dim(buoysDataLocation)[1] <= 1){
      buoysSummary[i,] <- c(buoysList[i], i, F, NA, NA)
    } else {
      
      # first filter, to delete on board and on land positions
      buoysDataLocation %>% 
        dplyr::filter(!is_onLand & !is.na(is_onLand) & !is_onBoardShip & !is.na(is_onBoardShip)) %>%
        dplyr::select(buoy_id, position_date, latitude, longitude) %>%
        # second filter, to delete positions which are not in the area of interest
        dplyr::filter(longitude >= xmin & longitude <= xmax & latitude >= ymin & latitude <= ymax) -> data
      # If there is no position (or just one) in the area of interest, save in the summary and go directly to the following buoy
      if (dim(data)[1] <= 1){
        buoysSummary[i,] <- c(buoysList[i], i, T, F, NA)
      } else {
        
        # Third filter, to delete the positions which are not in the period of interest
        data %>% mutate(position_date = as.POSIXct(position_date)) %>%
          dplyr::arrange(position_date) %>%
          dplyr::filter(position_date < max(interpolation_date) & position_date > min(interpolation_date)) -> data
        
        # path_data is generated to test if there are positions in the period of interest
        # the data frame "data" can contain positions which are only in the 12h before or after the period of interest
        data %>%
          dplyr::filter(position_date < max(tuna_position_date) & position_date > min(tuna_position_date)) -> path_data
        
        # If there is no data left (or just one point), save in the summary and go directly to the following buoy
        if (dim(path_data)[1] <= 1){
          buoysSummary[i,] <- c(buoysList[i], i, T, T, F)
        } else{
          
          # times of interest
          start_fad_path <- min(interpolation_date[which((interpolation_date > min(data$position_date)))])
          if (max(interpolation_date) > max(data$position_date)){
            end_fad_path <- max(interpolation_date[which(interpolation_date < max(data$position_date))])
          } else {
            end_fad_path <- max(interpolation_date)
          }
          
          # timesteps of interpolation
          interp_t <- seq(from = start_fad_path, to = end_fad_path, by = timestep)
          
          #interpolate x and y positions
          interp_long <- interp1(as.numeric(data$position_date), data$longitude, xi = as.numeric(interp_t), method = interpolation_method)
          interp_lat <- interp1(as.numeric(data$position_date), data$latitude, xi = as.numeric(interp_t), method = interpolation_method)
          
          #bind interpolated positions with timestamps
          data.frame(cbind(interp_long, interp_lat)) %>%
            rename("latitude" = "interp_lat",
                   "longitude" = "interp_long") %>%
            bind_cols(position_date = interp_t) %>%
            # remove the beginning and the end of the interpolated path (to have only the path corresponding the tuna_position_date)
            dplyr::filter(position_date <= max(tuna_position_date) & position_date >= min(tuna_position_date)) %>%
            mutate(timestep = seq(from = which(min(position_date) == tuna_position_date),
                                  by = 1, length.out = length(position_date)),
                   FAD_id = i) %>%
            # change timestep so that it starts from 0 (for the model in Python)
            mutate(timestep = timestep - 1) %>%
            right_join(total_timesteps, by = "timestep") %>%
            select(longitude, latitude, position_date, timestep, FAD_id) -> interp_data
          
          # Fill in summary
          buoysSummary[i,] <- c(buoysList[i], i, T, T, T)
          
          # Save positions
          for (k in 1:(length(steps_for_files)-1)){
              
              save.csv.traj(var_names, col_names, k, steps_for_files)
          
          }
          
          
          interp_data %>%
            dplyr::filter(timestep >= steps_for_files[length(steps_for_files)] & timestep <= length(tuna_position_date)-1 ) -> data.k
          
          for (i in 1:length(var_names)){
            write.table(round(t(data.k[,col_names[i]]), digits = 5),
                        file = file.path(OUTPUT_PATH, "drifting_fadArray",
                                         paste0("FADs.",var_names[i],"_",
                                                format(steps_for_files[length(steps_for_files)], scientific = F),
                                                "to",
                                                format(length(tuna_position_date)-1, scientific = F),
                                                ".csv")),
                        sep = ",", append = T, row.names = F, col.names = F
            )
          }
          
          
            
            

          
          
          # Save positions
         # write.table(round(t(interp_data$longitude), digits = 5),
         #             file = file.path(OUTPUT_PATH, "drifting_fadArray", "FADs.x.csv"),
         #             sep = ",", append = T, row.names = F, col.names = F)
         # write.table(round(t(interp_data$latitude), digits = 5),
         #             file = file.path(OUTPUT_PATH, "drifting_fadArray", "FADs.y.csv"),
         #             sep = ",", append = T, row.names = F, col.names = F)
         # write.table(round(t(interp_data$FAD_id), digits = 5),
         #             file = file.path(OUTPUT_PATH, "drifting_fadArray", "FADs.id.csv"),
         #             sep = ",", append = T, row.names = F, col.names = F)
         #  
          
          
          
          # ggplot()+geom_path(data = interp_data, aes(x = longitude, y = latitude, color = timestep))
          
          
        }
        
      }
      
    }
    
    
  }
  
  
  
}


## Save summary
write.table(buoysSummary, file = file.path(OUTPUT_PATH, "drifting_fadArray", "buoysSummary.csv"), sep = ";", row.names = F)
