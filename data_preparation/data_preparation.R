library(lubridate)
library(fields)
library(sp)
library(maptools)
library(lattice)
library(xtable)
library(ggplot2)
library(foreign)
library(stringr)
library(lubridate)
library(dplyr)
library(xtable)
library(scales)
library(RColorBrewer)
library(grid)
library(ggmap)
library(gridExtra)
library(rgeos)
library(ggrepel)
if (!require(gpclib)) install.packages("gpclib", type="source")
gpclibPermit()
library(rgdal)
library(sp)
library(raster)
library(sqldf)
library(reshape2)



#use nyc planning department neighborhood shapefiles
nyc_shapefile <- spTransform(shapefile('../data/nynta.shp'), CRS("+proj=longlat +datum=WGS84"))
nyc_shapefile <- subset(nyc_shapefile, !grepl("park-cemetery-etc", nyc_shapefile@data$NTAName))
nyc_shapefile@data$id <- as.character(as.numeric(rownames(nyc_shapefile@data))+1)
nyc.points <- fortify(nyc_shapefile, region = "id")
nyc.map <-inner_join(nyc.points, nyc_shapefile@data, by = "id")

# use zillow shapefile for neighborhood identification
nyc_shapefile_zl <-readShapeSpatial('../data/ZillowNeighborhoods-NY.shp')
mht_shapefile <- subset(nyc_shapefile_zl, str_detect(CITY, 'New York City-Manhattan'))
queens_shapefile <- subset(nyc_shapefile_zl, str_detect(CITY, 'New York City-Queens'))
bronx_shapefile <- subset(nyc_shaplefile_zl, str_detect(CITY, 'New York City-Bronx'))
brooklyn_shapefile <- subset(nyc_shaplefile_zl, str_detect(CITY, 'New York City-Brooklyn'))
staten_shapefile <- subset(nyc_shaplefile_zl, str_detect(CITY, 'New York City-Staten Island'))



df_taxi <- read.csv("../data/yellow_tripdata_2016-01.csv")
#subset data within sample date range 
taxi_sample <- subset(df_taxi, day(as.POSIXlt(df_taxi$tpep_pickup_datetime, format = "%Y-%m-%d"))>=24 & day(as.POSIXlt(df_taxi$tpep_pickup_datetime, format = "%Y-%m-%d"))<= 30 )
#drop trips with invalid coordinates
taxi_sample <- taxi_sample[!(taxi_sample$pickup_longitude == 0 | taxi_sample$pickup_latitude == 0 | taxi_sample$dropoff_longitude ==0 | taxi_sample$dropoff_latitude ==0), ]

#create a unique ID for each ride
taxi_sample$RideID <- seq.int(nrow(taxi_sample))

#add variables showing time
taxi_sample$hour <- hour(as.POSIXlt(taxi_sample$tpep_pickup_datetime, format = "%Y-%m-%d %H:%M:%S"))
taxi_sample$wday <- wday(as.POSIXlt(taxi_sample$tpep_pickup_datetime, format = "%Y-%m-%d %H:%M:%S"))
taxi_sample$minute <- minute(as.POSIXlt(taxi_sample$tpep_pickup_datetime, format = "%Y-%m-%d %H:%M:%S"))

#add variables to show pickup and dropoff neighborhoods
# take only the coordinate columns, and replace NAs with 0
data_coords_pickup <- transmute(taxi_sample,
                                long = ifelse(is.na(pickup_longitude), 0, pickup_longitude),
                                lat = ifelse(is.na(pickup_latitude), 0, pickup_latitude))

# specify the columns that correspond to the coordinates
coordinates(data_coords_pickup) <- c('long', 'lat')
# returns the neighborhoods based on coordinates
nhoods_pickup <- over(data_coords_pickup, nyc_shapefile_zl)

# rename the column names in nhoods
names(nhoods_pickup) <- paste('pickup', tolower(names(nhoods_pickup)), sep = '_')
# combine the neighborhood information with the original data
taxi_sample <- cbind(taxi_sample, nhoods_pickup[, grep('name|city', names(nhoods_pickup))])

data_coords_dropoff <- transmute(taxi_sample,
                                 long = ifelse(is.na(dropoff_longitude), 0, dropoff_longitude),
                                 lat = ifelse(is.na(dropoff_latitude), 0, dropoff_latitude))
# specify the columns that correspond to the coordinates
coordinates(data_coords_dropoff) <- c('long', 'lat')
# returns the neighborhoods based on coordinates
nhoods_dropoff <- over(data_coords_dropoff, nyc_shapefile_zl)

# rename the column names in nhoods
names(nhoods_dropoff) <- paste('dropoff', tolower(names(nhoods_dropoff)), sep = '_')
# combine the neighborhood information with the original data
taxi_sample <- cbind(taxi_sample, nhoods_dropoff[, grep('name|city', names(nhoods_dropoff))])

# calculate trip length
taxi_sample$trip_length <- as.numeric(as.POSIXlt(taxi_sample$tpep_dropoff_datetime, format = "%Y-%m-%d %H:%M:%S") - as.POSIXlt(taxi_sample$tpep_pickup_datetime, format = "%Y-%m-%d %H:%M:%S"))

head(taxi_sample)

write.csv(taxi_sample, file = "taxi_sample.csv")

#used Python to process data; refer to attached Python codes
nodes <- read.csv("nodes.csv")
nodes_tag <- read.csv("nodes_tags.csv")
ways <- read.csv("ways.csv")
ways_tags <- read.csv("ways_tags.csv")
ways_nodes <- read.csv("ways_nodes.csv")

merge_ways_ways_tag <- merge(ways_nodes, ways_tags, by = "id" )
colnames(merge_ways_ways_tag)[1:2] <- c("way_id", "id")

merge_nodes_tags <- merge(nodes, nodes_tag, by = "id", all = TRUE)

#find all keys
table(merge_nodes_tags$key)

#subset data with keys of interest
merge_nodes_tags_subset <- merge_nodes_tags[merge_nodes_tags$key %in% c("amenity", "building", "cemetery", "county", "crossing", "cuisine", "denomination", "emergency", "historic", "historical", "history", "hotel", "housenumber", "junction", "highway", "name", "natural", "outdoor_seating", "parking", "park_ride", "public_transport", "religion", "shop", "street", "tourism", "postcode", "postal_code"), ]