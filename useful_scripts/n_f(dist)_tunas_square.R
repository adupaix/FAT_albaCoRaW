#!/usr/bin/env Rscript

library(tidyr)
library(dplyr)
library(gifski)
library(raster)
library(ggplot2)
library(foreach)
library(abind)

#script.dir <- dirname(sys.frame(1)$ofile)

#setwd(script.dir)

args = commandArgs(TRUE)
dist = args[1]
n_tunas = args[2]

cat("Distance between FAD:", dist)
cat("\nNumber of tunas:", n_tunas)

###~~~~~ Fonctionne uniquement si m = 0
m = 0


#cbind_na <- function(X1,x2){
#
#  if (length(x2) == dim(X1)[1]){
#    return(cbind(X1, x2))
#  } else if (length(x2) > dim(X1)[1]) {
#    return( cbind( rbind(d, matrix(nrow = length(x2)-dim(X1)[1], ncol = dim(X1)[2])), x2) )
#  }

#  length(x1) = length(x2) = max(length(x1),length(x2))
#  return(cbind(x1,x2))
#}

cat("\n\n~~~ Reading tuna paths ~~~\n")

csv_to_traj <- function(k, n_tunas){

  cat(k,"/",n_tunas,"\r")
  traj <- read.csv(paste0("tuna_n",k,".csv"), h = F)
  names(traj) <- c("x","y","alpha","theta","step","asso_FAD")

  traj %>% dplyr::select(x,y,step) %>%
    dplyr::mutate(step = step + 1) -> traj

  #~~~ Complete tuna trajectories, to fill in "jumps"

  # a: positions to fill in (when tuna "jumps")
  a <- which(traj$x == 0)
  if (length(a) != 0){

    ends <- a[ which(dplyr::lead(a)-a != 1 | is.na(dplyr::lead(a)-a)) ]
    starts <- a[ which(dplyr::lag(a)-a != -1 | is.na(dplyr::lag(a)-a)) ]

    # starts and beginning of segments to fill in:
    es <- data.frame(cbind(starts = starts, ends = ends))

    for (i in 1:dim(es)[1]){
      pos1 <- traj[es$starts[i]-1,]
      pos2 <- traj[es$ends[i]+1,]

      traj$x[(starts[i]-1):(ends[i]+1)] <- seq(pos1$x, pos2$x, length.out = pos2$step - pos1$step +1)
      traj$y[(starts[i]-1):(ends[i]+1)] <- seq(pos1$y, pos2$y, length.out = pos2$step - pos1$step +1)

    }
  }

  #~~~ Sub-sample the trajectory to keep only a position every 10 minutes
  timestep = 100
  traj <- traj[seq( 1, dim(traj)[1], (60*10)/timestep ), ]

  # #~~~ Build matrices with presence/absence of tuna for each timestep
  # r = raster::raster(resolution = c(20,20), xmn = 1000, xmx = 4000, ymn = 1000, ymx = 4000)
  # 
  # # cells in which the tuna is
  # cells = cellFromXY(r, traj[,1:2])

  return(traj)
}

#returns a list of matrices
cells <- lapply(1:n_tunas, FUN = csv_to_traj, n_tunas = n_tunas)

# we bind the matrices along the 3rd dimension
# dim1: steps
# dim2: c(longitude, latitude, step_number)
# dim3: tunas
cells <- abind(cells, along = 3)

#get the initial position
init_FAD <- cells[1,1:2,1]

timesteps <- 1:dim(cells)[1]
maps_ts <- seq(1, dim(cells)[1]/(6*12), 1)


## ~~~ Build a matrix for every 12 hours of the simulation (240 matrices, for a 120 days simulation)

cat("~~~ Building histograms ~~~\n")

nb_p_per_mapts <- foreach(i = maps_ts,
                             .packages = c("raster")) %do% {

            #get the positions of the tunas, for the timestep of interest
            pos <- t(cells[((6*12) * (i-1) + 1) , 1:2, ])
            
            # initial position
            init_pos <- cbind(rep(init_FAD[1], dim(pos)[1]), rep(init_FAD[2], dim(pos)[1]))
            
            #calculate the distance with the initial position
            distances.i <- as.data.frame( sqrt((pos[,1] - init_pos[,1])^2 + (pos[,2] - init_pos[,2])^2) )
            names(distances.i) <- "dist"
            
            # cols = topo.colors(10)

            p <- ggplot(distances.i) +
              geom_bar(aes(x = as.numeric(dist)))+
              # scale_fill_gradient(name = "Tunas",
              #                     low = "blue", high = "red",
              #                     trans = "log",
              #                     breaks = waiver(),
              #                     # values = seq(0,max,max/3),
              #                     labels= function(x) round(x),
              #                     limits=c(1,max)
              #                     )+
              scale_x_binned("Distance to initial position (km)",limits = c(0,1000), n.breaks = 50)+
              scale_y_continuous("Number of tunas", limits = c(0,1000), n.breaks = 20)+
              ggtitle(paste0("Time: ", (i-1)/2, "days"))+
              theme(panel.background = element_blank(),
                    axis.text.x = element_text(angle = 90, vjust = 0),
                    plot.title = element_text(hjust = 0.5))
#                    axis.ticks = element_blank())

            fname <- paste0("im-",
                             ifelse(i>=100, i, ifelse(i>=10, paste0("0",i), paste0("00",i)))
                             ,".png")

            ggsave(fname,p)

            cat("Saved file:", fname)

                             }


file_list = list.files(path = getwd(), pattern=".png")
file_list = file.path(getwd(),file_list)

file_name = paste0("n_tunas_f(d)_dFAD",dist,".gif")
cat("Saved", paste0("n_tunas_f(d)_dFAD",dist,".gif"))

gifski(png_files = file_list,
       gif_file = file_name,
       # width=1024, height=700,
       delay = 0.07)

file.remove(file_list)

