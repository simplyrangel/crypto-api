import numpy as np
import pandas as pd
import datetime

# internal functions:
import cbpro._utilities as utils
from cbpro._api import apiwrapper

# Pandas index slice:
idx = pd.IndexSlice

class markets(apiwrapper):
    def __init__(
        self,
        name,
        ):
        apiwrapper.__init__(self)
        self.name=name

    def available_products(self):
        api_output = self.query("/products")
        return pd.DataFrame(api_output)
    
    def usd_products(self):
        df = self.available_products()
        return df[df.quote_currency=="USD"].reset_index(drop=True)
        
    def stablecoin_products(self):
        df = self.available_products()
        return df[df.fx_stablecoin==True].reset_index(drop=True)

    def price_history(
        self,
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
        mdf = pd.DataFrame(
            np.nan,
            index=mdf_index,
            columns=[
                "low",
                "high",
                "open",
                "close",
                "volume",
                ],
            )
        #mdf = mdf.set_index("time")
        
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
        endpoint_template = "/products/{product_id}/candles?{options}"
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
            api_output = self.query(endpoint,debug=debug)
            
            # store in multiindex dataframe:
            df = utils.format_price_history(api_output)
            mdf.loc[start:end] = df
        
        # return multiindex dataframe:
        return mdf








