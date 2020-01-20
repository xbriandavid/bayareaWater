import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")

# Main dataframe that we will perform  analysis on
waterQuality = pd.read_pickle("waterQualityData.pkl")

# A list of all the stations present in water_quality
station_list = sorted(list(set(list(waterQuality[waterQuality.columns[0]]))))

# Tags: Station
def missingDates(meanDataframe, FreestationList):
    '''Determines which dates in a year are missing'''
    for station in FreestationList:
        missing_date = ({station: meanDataframe.groupby('Station').get_group(station)[meanDataframe.groupby('Station').get_group(station).isnull().any(axis = 1)].index})
        print(station, missing_date)

def missingStations(groupedDataframe):
    '''Determines which stations in a dataframe are missing'''
    return set(station_list).difference(set([k[0] for k,v in groupedDataframe]))

def monthlyMean(yearGroup, constituent):
    '''Returns a dataframe object displaying average values by month 
    for given constituent
    '''
    listOfStations = set(station_list).difference(missingStations(yearGroup))
    monthlyMeans = []
    for station in listOfStations:
        dataframe = yearGroup.get_group((station, constituent)).resample('M')['Value'].aggregate([np.mean])
        dataframe['Station'] = [station] * (dataframe.size)
        monthlyMeans.append(dataframe)
    monthlyMeans = pd.concat(monthlyMeans)
    monthlyMeans = monthlyMeans[['Station', 'mean']]
    return monthlyMeans

# Must already have a monthlyMean Dataframe object to use for parameter yearGroup
def monthlyMeanPlot(yearGroupedMeans):
    '''Plots the average value of the constituent input by month
    '''
    index = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep', 'Oct', 'Nov', 'Dec']
    figure, axis = plt.subplots(1, 1, figsize = (10, 8))
    for k,v in yearGroupedMeans.groupby('Station'):
        v['mean'].plot(kind = 'line', ax = axis, legend= False)
    #plt.xticks([0,1,2,3,4,5,6,7,8,9,10,11], index)
    plt.ylim([0,60])


def monthlyMedian(yearGroup, constituent):
    '''Returns a dataframe object displaying median values by month 
    for given constituent
    '''
    monthlyMedians = []
    listOfStations = set(station_list).difference(missingStations(yearGroup))
    for station in listOfStations:
        dataframe = yearGroup.get_group((station, constituent)).resample('M')['Value'].aggregate([np.median])
        dataframe['Station'] = [station]*dataframe.size
        monthlyMedians.append(dataframe)
    monthlyMedians = pd.concat(monthlyMedians)
    monthlyMedians = monthlyMedians[['Station', 'mean']]
    return monthlyMedians

def printOutliers(yearGroup, constituent):
    pass

# Tags: Stations
def stationSwarmPlot(yearGroup, stations, constituent):
    '''Plots swarmplots for each station specified in the stations parameter
    of the provided constituent
    '''
    swarmPlotDf = []
    for station in stations:
        df_to_append = yearGroup.get_group((station, constituent))
        swarmPlotDf.append(df_to_append)
    swarmPlotDf = pd.concat(swarmPlotDf)
    swarmPlotDf['Station Number'] = swarmPlotDf['Station Number'].astype(str)
    swarmPlotDf['Station Number'] = ["Station " + x for x in swarmPlotDf['Station Number']]
    fig, axs = plt.subplots(figsize = (13,7))
    swarmplot = sns.boxplot(x = 'Value', y = 'Station Number', data = swarmPlotDf, ax = axs)
    return swarmplot

# Tags: Stations 
def stationDepthPlots(yearGroup, stations, constituent):
    '''Plots constituent value vs depth for four stations
    '''
    first_station = yearGroup.get_group((stations[0], constituent))[['Depth [meters]', 'Value']]
    second_station = yearGroup.get_group((stations[1], constituent))[['Depth [meters]', 'Value']]
    third_station = yearGroup.get_group((stations[2], constituent))[['Depth [meters]', 'Value']]
    fourth_station = yearGroup.get_group((stations[3], constituent))[['Depth [meters]', 'Value']]
    fig, axs = plt.subplots(nrows = 2, ncols = 2, figsize = (12,7))
    first_graph = sns.barplot(x = first_station.groupby('Depth [meters]').median().index, y = 'Value', data = first_station.groupby('Depth [meters]').median(), ax=axs[0,0])
    second_graph = sns.barplot(x = second_station.groupby('Depth [meters]').median().index, y = 'Value', data = second_station.groupby('Depth [meters]').median(), ax=axs[0,1])
    third_graph =  sns.barplot(x = third_station.groupby('Depth [meters]').median().index, y = 'Value', data = third_station.groupby('Depth [meters]').median(), ax=axs[1,0])
    fourth_graph =  sns.barplot(x = fourth_station.groupby('Depth [meters]').median().index, y = 'Value', data = fourth_station.groupby('Depth [meters]').median(), ax=axs[1,1])
    slist = [first_station, second_station, third_station, fourth_station]
    glist = [first_graph, second_graph, third_graph, fourth_graph]
    max_num = []
    for item in slist:
        max_value = item['Value'].max()
        max_num.append(max_value)
    ylim = max(max_num)
    for station_ax, station in zip(glist, station_list):
        station_ax.set_ylim([0, ylim])
        station_ax.set_title("STATION " + str(station), loc = 'left')
    plt.tight_layout()