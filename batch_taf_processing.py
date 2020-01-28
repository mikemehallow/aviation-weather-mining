import requests
import pandas as pd
import avwx
from taf_to_dataframe import get_taf_dict

# Create list of stations using ICAO codes
station_list = ['KBOS', 'KJFK']

# Create URL Request
station_string = 'stationString= ' + ' '.join(station_list)

params = {}
params["dataSource"] = 'tafs'
params["requestType"] = 'retrieve'
params["format"] = 'xml'
params["hoursBeforeNow"] = '2'


def batch_process_tafs(station_list, params):

    url = "https://aviationweather.gov/adds/dataserver_current/httpparam"

    # Pass station list to URL params
    params["stationString"] = ' '.join(station_list)

    # Run HTML Request
    r = requests.get(url, params)
    content = str(r.content)

    # Split content into indvidual TAFs
    split_content = content.split('<raw_text>')

    # Use avwx to parse individual tafs
    tafs = []
    for text in split_content[1:]:
        # Initialize TAF object with ICAO station code, from first 4 characters
        taf = avwx.Taf(text[:4])
        
        # Parse TAF
        taf.data, taf.parsed = avwx.taf.parse(text[:4], text)
        
        # Append taf to list of tafs
        tafs.append(taf)

    # Create list of TAF dictionaries
    taf_dicts = {}
    for taf in tafs:
        taf_dicts.update(get_taf_dict(taf))

    # Convert list of dictionaries to dataframe
    df = pd.DataFrame.from_dict(taf_dicts, orient='index').reset_index() \
                     .rename(columns={'level_0': 'station',
                                      'level_1': 'forecast_time',
                                      'level_2': 'forecast_id'})

    return df
