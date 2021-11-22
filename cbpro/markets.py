import numpy as np
import pandas as pd
import datetime

# internal functions:
from cbpro._api import apiwrapper
import cbpro._utilities as utils

# Pandas index slice:
idx = pd.IndexSlice

def price_history(
    pair,
    start,
    end,
    granularity,
    debug=False,
    ):
    # The max number of data per request is 300 candles. 
    # If the request is larger than 300 candles, the API 
    # will reject it. 
    # 
    # granularity must be one of these values:
    # 60         (one minute)
    # 300         (five minutes)
    # 900         (fifteen minutes)
    # 3600         (one hour)
    # 21600     (six hours)
    # 86400     (one day)
    # 
    # create empty dataframe for the prices:
    mdf_index = pd.date_range(
        start=start,
        end=end,
        freq="%dS"%granularity,
        )
    
    # discretize the datetime index into groups of 300
    # if necessary:
    index_slices = []
    if len(mdf_index) >= 300:
        start = 0
        end = 299
        num_slices,remainder = divmod(len(mdf_index),300)
        for ii in range(num_slices):
            index_slices.append([
                mdf_index[start],
                mdf_index[end],
                ])
            start += 300
            end += 300
        index_slices.append([
            mdf_index[-remainder],
            mdf_index[-1]
            ])
    else:
        index_slices.append([
            mdf_index[0],
            mdf_index[-1],
            ])
    
    # iterate over each (start, end) pair:
    cbapi = apiwrapper()
    endpoint_template = "/products/{product_id}/candles?{options}"
    frames = []
    for start, end in index_slices:
        iso_start = start.strftime("%Y-%m-%dT%H:%M:%SZ")
        iso_end = end.strftime("%Y-%m-%dT%H:%M:%SZ")
        query_options = "start=%s&end=%s&granularity=%d"%(
            iso_start,
            iso_end,
            granularity,    
            )
        endpoint = endpoint_template.format(
            product_id=pair,
            options=query_options,
            )
        
        # query API:
        api_output = cbapi.query(endpoint,debug=debug)
        
        # store in multiindex dataframe:
        df = pd.DataFrame(api_output)
        frames.append(df)
    
    # create and return multiindex dataframe:
    results = pd.concat(frames)
    results.loc[:,0] = pd.to_datetime(results[0], unit="s")
    results.columns = [
        "date",
        "low",
        "high",
        "open",
        "close",
        "volume",
        ]
    return results.set_index("date")








