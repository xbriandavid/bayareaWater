import pandas as pd
import numpy as np
from analysisMethods import station_list

station_names = pd.read_csv('stationnames.csv')
station_names_dict = {k:v for (k,v) in zip(station_names['Station'], station_names['General Location'])}
stations = ["Station " + str(x) for x in station_list]

#Column names: 'Station Number', 'North Longitude Degrees', 'North Latitude Minutes', 'West Longitude #Degrees','West Longitude Minutes', & 'Comments'
StationLocations = pd.read_csv("SFBay_TableofStationLocations.csv")

#Create a list of tuples, each containing the coordinates: (NL Deg NL Min, WL Deg, WL Min)
DMM_coordinates = [(str(x)+ " " + str(y), str(z) + " " + str(a)) for x, y, z, a in zip(StationLocations[StationLocations.columns[1]], StationLocations[StationLocations.columns[2]], StationLocations[StationLocations.columns[3]], StationLocations[StationLocations.columns[4]])]

#Create a dictionary where the station number is the key, coordinate of the associated section is the value. 
DMM_dict = {int(Station): Coordinates for Station,Coordinates in zip(StationLocations[StationLocations.columns[0]], DMM_coordinates)}

stations = ["Station " + str(x) for x in station_list]
coords = pd.DataFrame({'Station Number': station_list})
coords['coords'] = coords['Station Number'].map(DMM_dict)
coords.drop(coords.index[33], inplace = True)

coords.dropna(inplace=True)
Lat_M = [x[0] for x in coords['coords']]
coords['Lat_D'] = [int((x.replace(" ", ""))[:2]) for x in Lat_M]
coords['Lat_M'] = [float(((x.replace(" ", ""))[2:]).replace("'", "")) for x in Lat_M]
coords['Lat_DD'] = [(x + (y / 60)) for x,y in zip(coords['Lat_D'], coords['Lat_M'])]

Long_M = [x[1] for x in coords['coords']]
coords['Long_D'] = [int((x.replace(" ", ""))[:4]) for x in Long_M]
coords['Long_M'] = [float(((x.replace(" ", ""))[4:]).replace("'", "")) for x in Long_M]
coords['Long_DD'] = [(x - (y/60)) for x,y in zip(coords['Long_D'], coords['Long_M'])]
file_names = ["Map" + str(k) + ".json" for k,v in enumerate(coords['Long_M'])]
coords['Station label'] = coords['Station Number'].map(station_names_dict)
coords.replace(np.nan, 'N/A Station Name', inplace = True)

Lat_DD_dict = {station:lat for station,lat in zip(coords['Station Number'], coords['Lat_DD'])}
Long_DD_dict = {station:long for station,long in zip(coords['Station Number'], coords['Long_DD'])}