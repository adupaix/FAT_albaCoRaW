#!/usr/bin/env Rscript

library(tidyr)
library(dplyr)
library(gifski)
library(raster)
library(ggplot2)
library(foreach)

#script.dir <- dirname(sys.frame(1)$ofile)

#setwd(script.dir)

args = commandArgs(TRUE)
dist = args[1]

cat("Distance between FAD:", dist)

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

cells <- list()

cat("\n~~~ Reading csv files ~~~\n")

csv_to_cells <- function(k){

  cat(k,"/1000\n")
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

  #~~~ Build matrices with presence/absence of tuna for each timestep
  r = raster::raster(resolution = c(20,20), xmn = 1000, xmx = 4000, ymn = 1000, ymx = 4000)

  # cells in which the tuna is
  cells = cellFromXY(r, traj[,1:2])

  return(cells)
}

cells <- mapply(1:1000, FUN = csv_to_cells)

timesteps <- 1:dim(cells)[1]
maps_ts <- seq(1, dim(cells)[1]/(6*12), 1)


## ~~~ Build a matrix for every 12 hours of the simulation (240 matrices, for a 120 days simulation)

cat("~~~ Building maps ~~~\n")

nb_p_per_mapts <- foreach(i = maps_ts,
                             .packages = c("raster")) %do% {

            r.i = raster::raster(resolution = c(20,20), xmn = 1000, xmx = 4000, ymn = 1000, ymx = 4000)
            r.i[] <- 0

            pos <- as.vector( cells[((6*12) * (i-1) + 1) : (6*12*i) ,] )

            tab <- table(pos)

            r.i[ as.numeric(attr(tab, "dimnames")$pos) ] <- tab

            toplot.i <- as.data.frame(r.i, xy = T) %>% dplyr::filter(layer != 0)

            if (i == 1){ max <- max(toplot.i$layer)}

            rm(r.i) ; invisible(gc())

            cols = topo.colors(10)

            p <- ggplot(toplot.i) +
              geom_raster(aes(x = x, y = y, fill = layer))+
              scale_fill_gradient(name = "Tunas",
                                  low = "blue", high = "red",
                                  trans = "log",
                                  breaks = waiver(),
                                  # values = seq(0,max,max/3),
                                  labels= function(x) round(x),
                                  limits=c(1,max)
                                  )+
              scale_x_continuous("x (km)",limits = c(1000,4000), n.breaks = 30)+
              scale_y_continuous("y (km)",limits = c(1000,4000), n.breaks = 30)+
              theme(panel.background = element_blank(),
                   axis.text.x = element_text(angle = 90, vjust = 0))
#                    axis.title = element_blank(),
#                    axis.ticks = element_blank())

            fname <- paste0("im-",
                             ifelse(i>=100, i, ifelse(i>=10, paste0("0",i), paste0("00",i)))
                             ,".png")

            ggsave(fname,p)

            cat("Saved file:", fname)

                             }


file_list = list.files(path = getwd(), pattern=".png")
file_list = file.path(getwd(),file_list)

file_name = paste0("animation_tunas_d",dist,".gif")
cat("Saved", paste0("animation_tunas_d",dist,".gif"))

gifski(png_files = file_list,
       gif_file = file_name,
       # width=1024, height=700,
       delay = 0.07)

file.remove(file_list)

