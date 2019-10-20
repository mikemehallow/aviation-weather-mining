import avwx
import pandas as pd


def get_forecast_dict(forecast):
    attributes = ['start_time', 'end_time', 'altimeter', 'clouds',
                  'flight_rules', 'visibility', 'wind_direction',
                  'wind_gust', 'wind_speed', 'turbulence', 'wind_shear',
                  'icing']

    fcst_dict = {}

    # Dump attributes into dictionary
    for attribute in attributes:
        try:
            fcst_dict[attribute] = getattr(forecast, attribute)
        except AttributeError:
            fcst_dict[attribute] = None

    # Reformat clouds and handle cases where there are up to 3 different types
    heirarchy = ['pri', 'sec', 'ter']
    cloud_attributes = ['type', 'base', 'top', 'modifier', 'direction']

    for i in range(len(fcst_dict['clouds'])):
        for attribute in cloud_attributes:
            prefix = heirarchy[i]
            fcst_dict[prefix + '_' + attribute] = getattr(fcst_dict['clouds'][i], attribute)

    fcst_dict.pop('clouds')

    # Pull time from Timestamp data types
    for attribute in ['start_time', 'end_time']:
        if fcst_dict[attribute] is not None:
            fcst_dict[attribute] = fcst_dict[attribute].dt
        else:
            fcst_dict[attribute] = None

    # Pull values from Number data types
    for attribute in ['wind_speed', 'wind_direction', 'visibility', 'wind_gust']:
        if fcst_dict[attribute] is not None:
            fcst_dict[attribute] = fcst_dict[attribute].value
        else:
            fcst_dict[attribute] = None

    return fcst_dict


def get_taf_dict(taf):
    taf_dict = {}
    
    # Handle case where there is no TAF
    if taf.data is None:
        return taf_dict

    # Create dictionary of all forecasts within this taf
    for i in range(len(taf.data.forecast)):
        station = taf.data.station
        forecast_time = taf.data.time.dt
        taf_dict[(station, forecast_time, i)] = get_forecast_dict(taf.data.forecast[i])

    return taf_dict


def get_taf_dataframe(station_list):
    stations_tafs = {}

    # Request TAF for all stations in station list
    for station in station_list:
        # Read station's TAF
        taf = avwx.Taf(station)
        taf.update()

        # Create dictionary for this station and add
        taf_dict = get_taf_dict(taf)
        stations_tafs.update(taf_dict)

    # Create dataframe from dictionary
    df = pd.DataFrame.from_dict(stations_tafs, orient='index').reset_index() \
                     .rename(columns={'level_0': 'Station',
                                      'level_1': 'Forecast_Time',
                                      'level_2': 'Forecast_Idx'})

    return df

