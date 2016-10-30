
# Moving the City with Yellow Cabs
## author: Qianqi Kay Shen
## date: "October 28, 2016"

## 1. Summary

This project tells a story about New Yorkers' moving abouts with the Yellow Cab data. As of March 2014, 51,398 men and women licensed to drive medallion taxicabs (a.k.a, yellow cabs) in New York City. Every day, 600,000 people take a cab, accounting to 236 million in a year (reference: New York City Taxi and Limousine Commission). The yellow cabs provide a most convinient option for New Yorkers (and visitors) to go around the city. I ask a series of questions to find out interesting facts about the pattern of New Yorkers' cab usage. 

## 2. Questions

The main question that is driving this project is: How do New Yorkers use yellow cabs? I wonder: Who are they? When and where do they hail a cab? Where do they go? For example, do people take a cab to work? Where do they dine out on weekday nights and Friday nights? Do they go different places after work on weekdays and on weekends? Where do the opera-goers go after the show? Who tip the most, bigger group of young people going around the city or people who live in one of the wealthiest neighborhoods? 

## 3. Data
I use the yellow taxi trip record data from New York City Taxi and Limousine Commission (http://www.nyc.gov/html/tlc/html/about/trip_record_data.shtml) for trip data. This data contains information including trip pick-up and drip-off time and location coordinates, trip distances, fares, tips, and so on. 

In addition, for coordinate location information, I use OpenStreetMap New York City XML OSM data (http://metro.teczno.com/#new-york). After cleaning up the data, I constructed a  dataset contains main description information about each locality nodes (represented by a longitude-latitude pair), including what business it is in (be it school, theatre, restaurants, and so on) and the name of the locality.

For the preliminrary stage, I use a sample of both datasets for quick analysis. For yellow taxi trips, the sample contains all trip information from 2016-01-24 to 2016-01-30. For OSM data, I focus on theatre data. 

## 4. Potential problems with the data
I realize that the majority of New Yorkers may use public transit such as subways and bus instead of cabs for daily commute. Even for the people who use hailing service, yellow cabs do not tell the entire story. There are For-Hire vehicles and UBER cabs. Nevertheless, as of August 2016, yellow cab daily trip number still almost doubles UBER (source: http://toddwschneider.com/posts/taxi-uber-lyft-usage-new-york-city/). The yellow cab data will tell a rather intersting and different story from public transit data about the commute pattern of New Yorkers.


