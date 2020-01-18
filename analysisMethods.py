import pandas as pd
import numpy as np

# Main dataframe that we will perform  analysis on
waterQuality = pd.read_pickle("waterQualityData.pkl")

# A list of all the stations present in water_quality
station_list = sorted(list(set(list(waterQuality[waterQuality.columns[0]]))))

def missingDates(meanDataframe, FreestationList):
    '''Determines which dates in a year are missing'''
    #holder_dict = {}
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
