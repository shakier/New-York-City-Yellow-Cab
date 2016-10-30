
# New York City on the Move: 
##    Stories about New Yorkers' Go-Abouts with Yellow Cab Data 

## Qianqi Kay Shen
## October 28, 2016

## 1. Summary

This project analyses over 500 million New York City cab trip records, combined with the OpenStreetMap data, to tell a story about New Yorkers' move-abouts and daily lives. As of March 2014, 51,398 men and women licensed to drive medallion taxicabs (a.k.a, yellow cabs) in New York City. Every day, 600,000 people take a cab, accounting to 236 million in a year (reference: New York City Taxi and Limousine Commission). The yellow cabs provide a most convenient option for New Yorkers (and visitors) to go around the city. I ask a series of questions to find out interesting facts about the pattern of New Yorkers' cab usage. 

## 2. Questions and Deliverables

The main question that is driving this project is: How do New Yorkers use yellow cabs? I wonder: Who are they? When and where do they hail a cab? Where do they go? For example, do people take a cab to work? Where do they dine out on weekday nights and Friday nights? Do they go different places after work on weekdays and on weekends? Where do the opera-goers go after the show? Who tip the most, bigger group of young people going around the city or people who live in one of the wealthiest neighborhoods? 

The deliverables include a report of data analysis, charts and figures to describe cab usage, and maps to show patterns of movements and activities at destinations. 

A. **Passengers' cab usage descriptions and analyses** include but not limited to: the numbers of trips by weekdays, by months, and by hours each day; numbers of trips on special holidays; average miles, fares, tips by different time and destinations; top destinations and pickup locations by weekdays, by months, and by hours each day; the number of pickups and dropoffs of people at certain places (cab usage by kinds of places), such as schools, restaurants, churches, stores, neighborhoods, and so on; cab usage by different types of the same kind of place--for example, whether people go to fine dining restaurants more likely to take cabs than people go to fast food chains; 

B. **Mapping of movements and activities** include but not limited to: heat maps of cab pickups and dropoffs by weekdays, by monts, by hours, by special holidays; heat maps overlaying with different kinds of locations; plotting of pickup and dropoff locations by different times of the day and days of the week; trip plottings from and to certain locations; plotting of destinations by distances of trips; plotting of trips from and to public transit stations. 

## 3. Data
I use the yellow taxi trip record data from New York City Taxi and Limousine Commission (http://www.nyc.gov/html/tlc/html/about/trip_record_data.shtml) for trip data. This data contains information including trip pick-up and drip-off time and location coordinates, trip distances, fares, tips, and so on. 

In addition, for coordinate location information, I use OpenStreetMap New York City XML OSM data (http://metro.teczno.com/#new-york). After cleaning up the data, I constructed a  dataset contains main description information about each locality nodes (represented by a longitude-latitude pair), including what business it is in (be it school, theatre, restaurants, and so on) and the name of the locality.

For the preliminary stage, I use a sample of both datasets for quick analysis. For yellow taxi trips, the sample contains all trip information from 2016-01-24 to 2016-01-30. For OSM data, I focus on theatre data. 

## 4. Potential problems with the data
I realize that the majority of New Yorkers may use public transit such as subways and bus instead of cabs for daily commute. Even for the people who use hailing service, yellow cabs do not tell the entire story. There are For-Hire vehicles and UBER cabs. Nevertheless, as of August 2016, yellow cab daily trip number still almost doubles UBER (source: http://toddwschneider.com/posts/taxi-uber-lyft-usage-new-york-city/). The yellow cab data will tell a rather interesting and different story from public transit data about the commute pattern of New Yorkers.

## 5. Data Preparation
```{r echo=FALSE, message=FALSE, warning=FALSE, load_and_transform_taxi_data}
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

#used Python to process data; refer to attached Python codes
#subset data with keys of interest
merge_nodes_tags_subset <- merge_nodes_tags[merge_nodes_tags$key %in% c("amenity", "building", "cemetery", "county", "crossing", "cuisine", "denomination", "emergency", "historic", "historical", "history", "hotel", "housenumber", "junction", "highway", "name", "natural", "outdoor_seating", "parking", "park_ride", "public_transport", "religion", "shop", "street", "tourism", "postcode", "postal_code"), ]

#sample data for only amenities with their names
merge_nodes_tags_subset2 <- subset(merge_nodes_tags_subset, merge_nodes_tags_subset$key=="name"|merge_nodes_tags_subset$key=="amenity")

#get all amenity coordinates
amenity_coord <- subset(merge_nodes_tags_subset2, merge_nodes_tags_subset2$key =="amenity")
write.csv(amenity_coord, file = "amentiy_coord_range.csv")

#get all restaurant coordinates
restaurant_coord <- subset(amenity_coord, amenity_coord$value == "restaurant")
restaurant_coord <- merge(restaurant_coord, nodes_name, by = "id")
write.csv(restaurant_coord, file = "restaurant_coord.csv")

#get all theatre coordinates
theater_coord <- subset(amenity_coord, amenity_coord$value == "theatre")
theater_coord <- merge(theater_coord, nodes_name, by = "id")
write.csv(theater_coord, file = "theatre_coord.csv")
```

## 6. Priliminary Analysis:
### 6.1. Data descriptions

There are 2,323,898 trip records in the data sample, which cover all trips from 2016-01-24 to 2016-01-30. Counting trips by weekdays, we find out that the trip numbers increase sequentially from Sunday to Saturday. Sunday has the least trip number, which is 157,344, and Saturday has the largest trip number, 427,577.

![GitHub Logo](/trip_by_weekday.png)

Looking the data by hours, we find out that there are two peak hours. Unsurprisingly, they 
overlap with commute hours, 8 in the morning and 19 in the evening. Interestingly, more people take a cab to go home than go to work.

![GitHub Logo](/trip_by_hour.png)

I also plotted the trip number by hours by weekdays. It turns out that New Yorkers do take cabs to work. As the week goes by, more and more commuters choose to go to work and go home by cab. Friday night is the go out night. Cabs go around town until early morning Saturday. And the fun continues throughout Saturday. However, the city quiets down from Sunday early morning--significantly fewer people go out on cabs throughout Sunday. 

![GitHub Logo](/trip_by_weekday_hour.png)

The OSM data has 5,324,910 unique node ID's. Each node has coordinates longitude and latitude. For each node, the data provides different key and value pairs as description of that node. For example, a node may have a key "street" with a "value" showing the name of the street where the node is at. A node may also have a key "amenity" with a "value" showing what kind of amenity this node is. The top 20 keys are shown below.
```
# A tibble: 20 × 2
           key       n
        <fctr>   <int>
1           NA 5055170
2   created_by  112690
3  housenumber  102588
4       street  102549
5     postcode  100939
6         name   24437
7      amenity   20271
8          ele   16043
9   feature_id   14769
10     created   12462
11     highway   12264
12   county_id   12124
13    state_id   12124
14       power    8733
15    capacity    4683
16       state    3960
17         ref    3744
18    religion    3713
19      source    3551
20 import_uuid    3510
```

For preliminary analysis, I only focus on amenity data. For the bigger project, however, other keys, such as parking, cuisine, religion, and so on, will also provide interesting geographical information. The top amenity values are shown below. Bicycle parking has the highest hit, 4,794. Then it is school, 4,525, place of worship, 3,879, and restaurant, 1,186. In this primary stage, I will use restaurant data to show how I will use this data, combined with the taxi data, to do analysis. In the future, I may also look at other interesting values, such as schools, parking, and bars.

```
# A tibble: 20 × 2
              value     n
             <fctr> <int>
1   bicycle_parking  4794
2            school  4525
3  place_of_worship  3879
4        restaurant  1186
5      fire_station   612
6         fast_food   447
7        grave_yard   411
8              cafe   376
9           parking   346
10            bench   340
11          library   324
12         hospital   311
13             bank   309
14      post_office   305
15   drinking_water   194
16             fuel   192
17         pharmacy   182
18          toilets   159
19         post_box   148
20              bar   134
```

## 6.2. Data plotting

This plot uses all the trips as inputs, and it basically becomes a road map of New York City area! As seen from the map, most cab use concentrates in Manhattan, and then the downtown areas in Queens and Brooklyn. Very little cab use in Bronx. In addition, we notice there is a cab line along a subway line (probably E) connecting to JFK Airport. It's very likely that people coming from and going to airport combine their trips with taxi and subways! 

![GitHub Logo](/nyc-taxi-pickup.png)

![GitHub Logo](/nyc-taxi-dropoff.png)

Let's see where the cab-taking working New Yorkers are coming from and going to work. Manhattan is still the place where more cab use is in. However, pickups are more concentrating on the east side, while dropoffs are all over Manhattan. In addition, dropoffs are more sparse, especially in Queens and Brooklyn areas. 

![GitHub Logo](/nyc-taxi-morning-pickup.png)

![GitHub Logo](/nyc-taxi-morning-dropoff.png)

Where do people go out on Friday night? To my surprise, the dropoff locations do not seem perfectly co-locate with the restaurants. This could be due to that the OSM data is incomplete. Or, people simply do not take cabs to restaurants. But anyway, this will need further investigations, including, but not limited to, analyzing data from other weeks. 


![GitHub Logo](/Friday_night_goout1.png)

![GitHub Logo](/Friday_night_goout2.png)

Then, would New Yorkers be taking cabs in late Friday night? Yes, more New Yorkers are taking cabs after 10 o'clock Friday night. 

![GitHub Logo](/Friday_late_night_pickup.png)

![GitHub Logo](/Friday_late_night_pickup2.png)

Now, let's take a look at the theatre district on Friday night. The map shows where people go after leaving the theatre district on Friday night. Most trips are in Manhattan. Very few go to Queens. And even fewer to other areas. But the data points are too small at this point, so I will need more data to investigate this question. 

![GitHub Logo](/theatre_goers_friday_night.png)

Who are the riders that pay the highest tip? In general, people take a cab within Manhattan tip higher. High tippers tend to be those who go to Times Square and Midtown. They could be visitors or financial bankers. Besides, wealthy people living in Upper East seem to tip more as well.

![GitHub Logo](/plot_high_tip.png)

![GitHub Logo](/plot_high_tip2.png)

# 7. Conclusion
This exciting data exploratory project targets the audiences who are interested in urban life and traffic movements, such as government agencies, businesses interested in consumer behaviors, and anyone who are interested in New York City commutes.  Audience may also find useful information for business and commercial activities--for example, enterprises finding locations for their businesses may find this report informative. With the data of New York cab service, this project tells multiple interesting stories about New Yorkers' commute. Combining with OpenStreetMap data, a lot more interesting questions can be answered. We not only know about the time and locations of people's movement with cabs, but we will also know what kind of activities people engaged in at their destinations.The mapping of the trips and descriptions of the destinations will show a series of stories about the daily life of New Yorkers.
