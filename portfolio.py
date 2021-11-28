"""Portfolio class."""
import numpy as np
import pandas as pd

class portfolio:
    def __init__(self,name):
        self.name = name
        self.all_accounts = []
        self.num_accounts = 0
        
    def add_account(self,account):
        self.all_accounts.append(account)
        self.num_accounts += 1
        self.usd_deposits=pd.DataFrame()
        self.coin_usd_values=pd.DataFrame()
        self.total_performance=pd.DataFrame()
    
    def aggregate_accounts(self):
        deposit_frames = []
        value_frames = []
        coin_names = []
        for account in self.all_accounts:
            coin = account.name
            perf = account.return_performance_data()
            deposit_frames.append(perf.usd_deposits)
            value_frames.append(perf.coin_usd_value)
            coin_names.append(coin)
        
        # USD deposits:
        deposits_df = pd.concat(deposit_frames, axis=1, keys=coin_names)
        deposits_df["total"] = deposits_df.sum(axis=1)
        self.usd_deposits = deposits_df
        
        # coin balance USD values:
        cvalues_df = pd.concat(value_frames, axis=1, keys=coin_names)
        cvalues_df["total"] = cvalues_df.sum(axis=1)
        self.coin_usd_values = cvalues_df
        
        # calculate total return:
        perf_df = pd.DataFrame(
            [cvalues_df.total,deposits_df.total],
            index=["coin_usd_value","deposits_usd"],
            ).transpose()
        perf_df["performance"] = perf_df.coin_usd_value/perf_df.deposits_usd
        self.total_performance = perf_df
        print(perf_df)
        
    def return_total_performance(self):
        return self.total_performance.copy()
        
        
