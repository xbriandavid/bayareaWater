
##########################################
#                                        #   
# Functions for producing leafleat maps  #
#                                        #
##########################################


import pandas as pd
import numpy as np
import json, string
import folium
import vincent
import os
from folium import Map, Marker, GeoJson, LayerControl
from analysis import chlo2014_median, chlo2015_median, chlo2016_median, chlo2017_median, chlo2018_median
from analysis import chlo_2018, chlo_2017, chlo2016, chlo2015, chlo2014
from analysis import station_list, chlo
from main_file import water_quality, DMM_dict
from folium.features import DivIcon
from folium import plugins 


station_names = pd.read_csv('stationnames.csv')
station_names_dict = {k:v for (k,v) in zip(station_names['Station'], station_names['General Location'])}

latlng = [37.739417, -122.254747]

stations = ["Station " + str(x) for x in station_list]
coords = pd.DataFrame({'Station Number': station_list})
coords['coords'] = coords['Station Number'].map(DMM_dict)
coords.drop(coords.index[33], inplace = True)


coordinates = list(coords['coords'])
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

#=================

chlo2018_median_map = chlo2018_median
chlo2017_median_map = chlo2017_median
chlo2016_median_map = chlo2016_median
chlo2015_median_map = chlo2015_median
chlo2014_median_map = chlo2014_median

map_dfs = [chlo2014_median_map, chlo2015_median_map, chlo2016_median_map, chlo2017_median_map, chlo2018_median_map]

color_list = np.array(['#f7fcf5', '#c7e9c0', '#74c476', '#238b45', '#00441b'])
bins = np.array([0.01, 2, 4, 6])
exnum = np.array([0, 0.01, 1.99, 2, 3, 8])

def color_coding(poll, colorPal, bin_edges):    
    idx = np.digitize(poll, bin_edges)
    return colorPal[idx]



chlo2018_median_map['median'] = chlo2018_median_map['median'].replace({np.nan:0})
chlo2017_median_map['median'] = chlo2017_median_map['median'].replace({np.nan:0})
chlo2016_median_map['median'] = chlo2016_median_map['median'].replace({np.nan:0})
chlo2015_median_map['median'] = chlo2015_median_map['median'].replace({np.nan:0})
chlo2014_median_map['median'] = chlo2014_median_map['median'].replace({np.nan:0})

chlo1418_map_list = pd.concat([chlo2014_median_map, chlo2015_median_map, chlo2016_median_map, chlo2017_median_map, chlo2018_median_map])

def prepare_data(df_list):
    print('> Preparing and creating dataframe!!...')
    df_map = []
    for df in df_list:
        df['median'] = df['median'].replace({np.nan: 0})
        df_map.append(df)
    df_map = pd.concat(df_map)
    df_map.reset_index(inplace = True)
    df_map = df_map.sort_values(by = ['Station', 'Date MM/DD/YYYY'])
    
    #df_map = df_map[df_map.Station != 29.5]
    #df_map['Lat_DD'] = df_map['Station'].map(Lat_DD_dict)
    #df_map['Long_DD'] = df_map['Station'].map(Long_DD_dict)
    #df_map['color'] = df_map['median'].apply(color_coding, bin_edges = bins)
    return df_map

chlo1418_map = prepare_data(map_dfs)
#unique_dates = list(chlo1418_map[chlo1418_map.columns[0]].unique())
#print("THESE ARE THE DATES")
#missing2014 = (set(unique_dates).difference(set(chlo1418_map[chlo1418_map['Station'] == 4.0][chlo1418_map.columns[0]])))
datesfor2014 = (chlo1418_map[chlo1418_map['Station'] == 4.0])
unique_dates = (chlo1418_map[chlo1418_map.columns[0]]).unique()
missing_dates = list(set(unique_dates).difference(set((datesfor2014[datesfor2014.columns[0]]).unique())))

testdf = chlo2014_median_map.copy()
testdf.reset_index(inplace = True)

testdf['Station'] = testdf['Station'].astype(int)
missing_stat = [4.0]


def create_geojson_features(df):
    print('> Creating GeoJSON features...')
    features = []
    for _, row in df.iterrows():
        feature = {
            'type': 'Feature',
            'geometry': {
                'type':'Point', 
                'coordinates':[row['Long_DD'],row['Lat_DD']]
            },
            'properties': {
                'time': row['Date MM/DD/YYYY'].date().__str__(),
                'style': {'color' : row['color']},
                'icon': 'circle',
                'iconstyle':{
                    'fillColor': row['color'],
                    'fillOpacity': 0.8,
                    'stroke': 'true',
                    'radius': 10
                }
            }
        }
        features.append(feature)
    return features

feat = create_geojson_features(chlo1418_map)
from folium.plugins import TimestampedGeoJson

#: Station 4.0 not included in year 2014
def make_map(df):
    print('> Making map...')
    bay_area_cord = [37.739417, -122.254747]
    pollution_map = folium.Map(location = bay_area_cord, control_scale=True, zoom_start=10, tiles = 'Stamen Terrain')
    for x,y,labels in zip(coords['Lat_DD'], coords['Long_DD'], coords['Station label']):
        pollution_map.add_child(folium.CircleMarker([x,y], color = '#99b3cc', radius = 15, tooltip = labels))
    features = create_geojson_features(df)
    
    TimestampedGeoJson(
        {'type': 'FeatureCollection',
        'features': features}
        , period='P1M'
        , add_last_point=True
        , auto_play=False
        , loop=True
        , max_speed=10
        , loop_button=True
        , date_options='YYYY/MM'
        , time_slider_drag_update=True
    ).add_to(pollution_map)
    print('> Done.')
    return pollution_map

chlo1418_map['Station Label'] = chlo1418_map['Station'].map(station_names_dict)

cmp = make_map(chlo1418_map)
 
cmp.save('chlo1418time.html')


# ================================
def print_missing_data(listOfDfs):
    for df,year in zip(listOfDfs, ['2014', '2015', '2016', '2017', '2018']):
        if((len(set(station_list).difference(set(df['Station Number'].unique())))) > 0):
            print("DATAFRAME " + year + " HAS MISSING STATIONS: " + str(set(station_list).difference(set(df['Station Number'].unique()))))
        else:
            print("Dataframe has all stations")


def create_data(constituent):
    df_2014 = water_quality.loc['2014-01-01':'2014-12-31'].groupby('Constituent').get_group(constituent)
    df_2015 = water_quality.loc['2015-01-01':'2015-12-31'].groupby('Constituent').get_group(constituent)
    df_2016 = water_quality.loc['2016-01-01':'2016-12-31'].groupby('Constituent').get_group(constituent)
    df_2017 = water_quality.loc['2017-01-01':'2017-12-31'].groupby('Constituent').get_group(constituent)
    df_2018 = water_quality.loc['2018-01-01':'2018-12-31'].groupby('Constituent').get_group(constituent)
    df_years = [df_2014, df_2015, df_2016, df_2017, df_2018]
    print_missing_data(df_years)
    return df_2014, df_2015, df_2016, df_2017, df_2018

#================================= vars to keep: latlng
from analysis import create_median_df

def determine_stations(constituent):
    df14,df15,df16,df17,df18 = create_data(constituent)
    stationLists = []
    for df in [df14,df15,df16,df17,df18]:
        listOfStations = list(set(df['Station Number']))
        stationLists.append(listOfStations)
    return stationLists



def fix_missing_data(df):
    if((len(set(station_list).difference(set(df['Station Number'].unique())))) > 0):
        examine_df = df.copy(deep = True)
        stations_to_fill = list(set(station_list).difference(set(df['Station Number'].unique())))
        for missing_station in stations_to_fill:
                copy = (examine_df.iloc[0,:]).copy()
                copy['Station Number'] = missing_station
                copy['Value'] = np.nan
                copy = pd.DataFrame(copy)
                copy = copy.T
                examine_df = examine_df.append(copy)
                outcome_df = examine_df
    else:
        outcome_df = df

    return outcome_df


#just check in general whether a station has missing dates 
from folium.plugins import TimestampedGeoJson

def print_missing_dates(listofdfs):
    stations_to_fill = []
    for df in listofdfs:
        #listOfStations = list(df['Station'].unique())
        for station in station_list:
            dataFrame = df[df['Station'] == station]
            missingDate = list((set(unique_dates)).difference(set((dataFrame[dataFrame.columns[0]]).unique())))
            if len(missingDate) > 0:                
                print("STATION " + str(station))
                stations_to_fill.append(station)
    return stations_to_fill


def mod1(listOfDfs, palette, numBins):
    map_list = []
    templateDF = prepare_data(listOfDfs)
    missing_stations = print_missing_dates([templateDF])
    
    constit1418_map = templateDF.copy()
    
    for station in missing_stations:
        dataFrame = (templateDF[templateDF['Station'] == station])
        missingDates = list((set(unique_dates)).difference(set((dataFrame[dataFrame.columns[0]]).unique())))
        for missing_date in missingDates:
            copy = (chlo1418_map.iloc[0,:]).copy()
            copy['Date MM/DD/YYYY'] = missing_date
            copy['Station'] = station
            copy['median'] = np.nan
            copy = pd.DataFrame(copy)
            copy = copy.T
            constit1418_map = constit1418_map.append(copy)
            constit1418_map = constit1418_map.sort_values(by = ['Station', 'Date MM/DD/YYYY'])
    
    constit1418_map['median'] = constit1418_map['median'].replace({np.nan: 0})
    
    constit1418_map = constit1418_map[constit1418_map.Station != 29.5]
    constit1418_map['Lat_DD'] = constit1418_map['Station'].map(Lat_DD_dict)
    constit1418_map['Long_DD'] = constit1418_map['Station'].map(Long_DD_dict)
    constit1418_map['color'] = constit1418_map['median'].apply(color_coding, colorPal = palette, bin_edges = numBins)

    return constit1418_map

def create_geojson_features(df):
    print('> Creating GeoJSON features...')
    features = []
    for _, row in df.iterrows():
        feature = {
            'type': 'Feature',
            'geometry': {
                'type':'Point', 
                'coordinates':[row['Long_DD'],row['Lat_DD']]
            },
            'properties': {
                'time': row['Date MM/DD/YYYY'].date().__str__(),
                'style': {'color' : row['color']},
                'icon': 'circle',
                'iconstyle':{
                    'fillColor': row['color'],
                    'fillOpacity': 0.8,
                    'stroke': 'true',
                    'radius': 10
                }
            }
        }
        features.append(feature)
    return features

def make_map(df):
    print('> Making map...')
    bay_area_cord = [37.739417, -122.254747]
    pollution_map = folium.Map(location = bay_area_cord, control_scale=True, zoom_start=10, tiles = 'Stamen Terrain')
    for x,y,labels in zip(coords['Lat_DD'], coords['Long_DD'], coords['Station label']):
        pollution_map.add_child(folium.CircleMarker([x,y], color = '#99b3cc', radius = 15, tooltip = labels))
    features = create_geojson_features(df)
    
    TimestampedGeoJson(
        {'type': 'FeatureCollection',
        'features': features}
        , period='P1M'
        , add_last_point=True
        , auto_play=False
        , loop=True
        , max_speed=10
        , loop_button=True
        , date_options='YYYY/MM'
        , time_slider_drag_update=True
    ).add_to(pollution_map)
    print('> Done.')
    return pollution_map



testStation = print_missing_dates([chlo1418_map])
df = (chlo1418_map[chlo1418_map['Station'] == 3.0])
missingDates = list((set(unique_dates)).difference(set((df[df.columns[0]]).unique())))


testDF = chlo1418_map.copy()

for station in testStation:
    dataFrame = (chlo1418_map[chlo1418_map['Station'] == station])
    missingDates = list((set(unique_dates)).difference(set((dataFrame[dataFrame.columns[0]]).unique())))
    print(str(station))
    #print(missingDates)
    for missing_date in missingDates:
        copy = (chlo1418_map.iloc[0,:]).copy()
        copy['Date MM/DD/YYYY'] = missing_date
        copy['Station'] = station
        copy['median'] = np.nan
        copy = pd.DataFrame(copy)
        copy = copy.T
        testDF = testDF.append(copy)


for missing_date in missingDates:
        copy = (chlo1418_map.iloc[0,:]).copy()
        copy['Date MM/DD/YYYY'] = missing_date
        copy['Station'] = 3.0
        copy['median'] = np.nan
        copy = pd.DataFrame(copy)
        copy = copy.T
        chlo1418_map = chlo1418_map.append(copy)


def prepare_for_data(df_years):
    print('> Creating datasets...')
    medians_df = []
    combined_df = pd.concat(df_years)
    
    for station in station_list:
        series_holder = combined_df[combined_df['Station Number'] == station]['Value'].resample('Y').aggregate(np.mean)
        df = pd.DataFrame({'Value': series_holder.values}, index = series_holder.index)
        df = df.T
        medians_df.append(df)
        
    medians_df = pd.concat(medians_df, axis = 0)
    
    
    medians_df.index = stations
    medians_df.columns = medians_df.columns.astype(str)
    column_labels = [str(x)[:4] for x in medians_df.columns]
    medians_df.columns = column_labels
    medians_df.drop('Station 29.5', axis = 0, inplace = True)
    
    median_df_list = []
    for index,val in medians_df.iterrows():
        median_df_list.append(pd.DataFrame(val).T)
    return median_df_list


def plot_bar_graphs(df_years, html_link, name, color):
    print('>plotting map...')
    listOfMedians = prepare_for_data(df_years)
    barGraphMap = Map(location = latlng, zoom_start = 10, tiles = 'Stamen Terrain')
    for x,y,df,file,station,ttip in zip(coords['Lat_DD'], coords['Long_DD'], listOfMedians, file_names, coords['Station Number'], coords['Station label']):
        bar = vincent.GroupedBar(df)
        bar.axis_titles(x = "Index", y = name)
        bar.width = 900
        bar.height = 250
        bar.legend(title='Year')
        bar.to_json(file)
        vis1 = os.path.join('/Users/fetch/Desktop/ProjectDirectory', file)
        folium.Marker(location=[x,y], 
                      icon = DivIcon(
            icon_size=(28,25),
            icon_anchor=(7, 20),
            html='<div style="font-family: Rockwell; font-size: 9pt; color :#00664b">'+str(station)+'</div>',
            ),
                      popup=folium.Popup(max_width=1100).add_child(
                              folium.Vega(json.load(open(vis1)), width= 1000, height=300))
                      ).add_to(barGraphMap)
        barGraphMap.add_child(folium.CircleMarker([x,y], fill_color = color, color = color, radius = 22, tooltip = ttip))
    
        barGraphMap.save(html_link+'.html')



ch2014, ch2015, ch2016, ch2017, ch2018 = create_data(chlo)

ch2014 = fix_missing_data(ch2014)
ch2018 = fix_missing_data(ch2018)
years = [ch2014, ch2015, ch2016, ch2017, ch2018]
plot_bar_graphs(years, 'chlomap')


co2014, co2015, co2016, co2017, co2018 = create_data('Calculated Oxygen [mg/L]')
co2014 = fix_missing_data(co2014)
co2018 = fix_missing_data(co2018)
co2018 = prepare_for_data(co2018)
plot_bar_graphs([co2014, co2015, co2016, co2017, co2018], 'calcoxy', 'Calculated Oxygen [mg/L]', '#00bfff')
