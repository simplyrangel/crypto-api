"""Individual KuCoin trading account."""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import time

# KuCoin toolset:
from kucoin._api import apiwrapper
import kucoin._utilities as utils

# Pandas index slices:
idx = pd.IndexSlice

# accounts class:
class account(apiwrapper):
    def __init__(
        self,
        name,
        api_key_file=None,
        ):
        apiwrapper.__init__(self)
        self.read_keyfile(api_key_file)
        self.name=name
        self.ledger=pd.DataFrame()
        self.usd_fills=pd.DataFrame()
        self.deposits=pd.DataFrame()
        self.balance_sheet=pd.DataFrame()
        self.performance_data=pd.DataFrame()
        #self._url_setup()

    def set_date_range(self,di,de):
        self.start_date = di
        self.end_date = de

    def get_ledger(self):
        date_range = self._discretize_date_range("ledger")
        frames = []
        for start_date in date_range:
            end_date = start_date + timedelta(days=1)
            te = int(end_date.timestamp()*1000)
            ti = int(start_date.timestamp()*1000)
            request = utils.ledger_request_url(self.name,ti,te)
            output = self.query(request)
            output_data = output["data"]
            if output_data["totalNum"] > 0:
                for item in output_data["items"]:
                    s = pd.Series(item)
                    frames.append(s)
            
            # make sure we never exceed 6 requests per second:
            time.sleep(0.17)
        
        # concatenate results into single dataframe:
        if len(frames) > 0:
            results = pd.concat(frames, axis=1).transpose()
            utils.update_createdAt(results)
            self.ledger=results
    
    def return_ledger(self):
        return self.ledger.copy()

    def _discretize_date_range(self,request_type):
        freqbin = {
            "ledger": "D",
            "fill": "W",
            }
        return pd.date_range(
            self.start_date,
            self.end_date,
            freq=freqbin[request_type]
            )
    
    
    
    
    
