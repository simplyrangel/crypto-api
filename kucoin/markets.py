"""KuCoin price history."""
import numpy as np
import pandas as pd
from datetime import datetime

# internal functions:
from kucoin._api import apiwrapper
import kucoin._utilities as utils

# pandas index slices:
idx = pd.IndexSlice

# price history function:
def price_history(
    pair,
    start,
    end,
    granularity=86400, #default    
    ):
    # The max number of data per request is 1500. 
    # 
    # granularity: Type of candlestick patterns: 
    # - 1min, 3min, 5min, 15min, 30min
    # - 1hour, 2hour, 4hour, 6hour, 8hour
    # - 12hour, 1day, 1week
    # 
    # check to make sure the number of data points
    # is within 1500. If not within 1500, discretize. 
    df_index = pd.date_range(
        start=start,
        end=end,
        freq="%dS"%granularity
        )
    index_slices = []
    if len(df_index) >= 1500:
        start=0
        end=1499
        num_slices,remainder = divmod(len(df_index),1500)
        for ii in range(num_slices):
            index_slices.append([
                df_index[start],
                df_index[end],
                ])
            start += 1500
            end += 1500
        index_slices.append([
            df_index[-remainder],
            df_index[-1]
            ])
    else:
        index_slices.append([
            df_index[0],
            df_index[-1],
            ])
    
    # iterate over each (start,end) pair:
    kuapi = apiwrapper()
    endpoint = "/api/v1/market/candles"
    frames = []
    for di,de in index_slices:
        utc_start = int(di.timestamp())
        utc_end = int(de.timestamp())
        options = [
            "type=1day",
            "symbol=%s"%pair,
            "startAt=%d"%utc_start,
            "endAt=%d"%utc_end,
            ]
        options = "&".join(options)
        request_url = "%s?%s"%(endpoint,options)
        
        # query api:
        api_output = kuapi.query(request_url)
        df = pd.DataFrame(api_output["data"])
        frames.append(df)
    
    # create and return dataframe:
    results = pd.concat(frames)
    results.loc[:,0] = pd.to_datetime(results[0],unit="s")
    results.columns = [
        "time",
        "open",
        "close",
        "high",
        "low",
        "volume",
        "turnover",
        ]
    results = results.set_index("time")
    for col in results.columns:
        results.loc[:,col] = results[col].apply(float)
    return results
    
    
    
    
    



