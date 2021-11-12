import numpy as np
import pandas as pd
import datetime
import pickle

# internal functions:
import cbpro._utilities as utils
from cbpro._api import apiwrapper

# Pandas index slice:
idx = pd.IndexSlice

class portfolio(apiwrapper):
    def __init__(
        self,
        name,
        save_loc="bin",
        ):
        apiwrapper.__init__(self)
        self.name = name
        self.save_loc = save_loc
        self.holdings = None
        self.ledger = None
        self.daily_history = None
        self.usd_deposits = None
        self.last_save = None
        
    def auto_setup(self):
        self.get_holdings()
        self.get_ledger()
        self.get_daily_history()
        self.get_usd_deposits()
    
    def return_holdings(self):
        if type(self.holdings) is pd.DataFrame:
            return self.holdings.copy()
        else:
            return "Error; holdings not defined."
    
    def return_ledger(self):
        if type(self.ledger) is pd.DataFrame:
            return self.ledger.copy()
        else:
            return "Error; holdings not defined."
    
    def return_daily_history(self):
        if type(self.daily_history) is pd.DataFrame:
            return self.daily_history.copy()
        else:
            return "Error; daily-history not defined."
    
    def return_usd_deposits(self):
        if type(self.usd_deposits) is pd.DataFrame:
            return self.usd_deposits.copy()
        else:
            return "Error; usd-deposits not defined."           
        
    def save(self):
        self.last_save = datetime.datetime.now()
        last_save_str = self.last_save.strftime("%Y-%m-%dT%H-%M-%S")
        if type(self.holdings) is pd.DataFrame:
            self.holdings.to_excel("%s/%s-%s-holdings.xlsx"%(
                self.save_loc,
                last_save_str,
                self.name,
                ))
        if type(self.ledger) is pd.DataFrame:        
            self.ledger.to_excel("%s/%s-%s-ledger.xlsx"%(
                self.save_loc,
                last_save_str,
                self.name,
                ))
        if type(self.daily_history) is pd.DataFrame:        
            self.daily_history.to_excel("%s/%s-%s-daily-history.xlsx"%(
                self.save_loc,
                last_save_str,
                self.name,
                ))
        if type(self.usd_deposits) is pd.DataFrame:        
            self.usd_deposits.to_excel("%s/%s-%s-usd-deposits.xlsx"%(
                self.save_loc,
                last_save_str,
                self.name,
                ))
        pkl_file = "%s/%s-%s.pkl"%(self.save_loc,last_save_str, self.name)
        with open(pkl_file,"wb") as of:
            pickle.dump(self,of)

    def get_holdings(self):
        api_output = self.query("/accounts")
        df = pd.DataFrame(api_output)
        for col in ["balance","hold","available"]:
            df.loc[:,col] = df[col].astype(np.float)
        self.holdings = df.sort_values(
            by="balance",
            ascending=False,
            ).set_index("currency"
            )
        
    def get_ledger(self):
        df = self.holdings
        frames = []
        for coin in df.index:
            coin_id = df.loc[coin,"id"]
            api_output = self.query("/accounts/%s/ledger"%coin_id)
            coin_ledger = utils.ledger2df(api_output)
            frames.append(coin_ledger)
        mdf = pd.concat(
            frames,
            keys=list(df.index),
            names=["coin","transaction_no"],
            )
        self.ledger = utils.update_ledger(mdf)
        
    def get_daily_history(self):
        coins_in_ledger = self.ledger.index.levels[0].tolist()
        
        # create dataframe based on ledger contents:
        di = self.ledger.index.levels[1].min().date()
        de = datetime.datetime.today()
        date_range = pd.date_range(
            start=di,
            end=de,
            freq="D",
            tz=None,
            )
        mdf = pd.DataFrame(
            np.nan,
            index=date_range,
            columns=coins_in_ledger,
            )
        
        # add each coin's contents and return populated
        # multiindex dataframe:
        for coin in coins_in_ledger:
            df = self.ledger.loc[idx[coin,:],:]
            df = df.reset_index().set_index("created_at")
            df = df.resample("D").last().dropna(how="all")
            mdf.loc[df.index,coin] = df.balance
        self.daily_history = mdf.ffill().fillna(0.0)
        
    def get_usd_deposits(self):
        di = self.ledger.index.levels[1].min().date()
        de = datetime.datetime.today()
        date_range = pd.date_range(
            start=di,
            end=de,
            freq="D",
            tz=None,
            )
        deposits = pd.DataFrame(
            np.nan,
            index=date_range,
            columns=["total"],
            )
        deposits.index.names = ["date"]
        deposits.iloc[0,:] = 0.0

        # extract total USD deposits per day:
        usdv = ["USD","USDC","USDT"]
        usd_ledger = self.ledger.loc[idx[usdv,:],:].reset_index(
            ).set_index("created_at",
            )
        usd_ledger = usd_ledger[
            (usd_ledger.type=="deposit")
            | (usd_ledger.type=="transfer")
            ]
        usd_ledger = usd_ledger.resample("D").sum()
        usd_ledger = usd_ledger[usd_ledger.amount>0]

        # add to deposits dataframe and forward fill:
        deposits.loc[
            usd_ledger.index,
            "total",
            ] = usd_ledger.amount.cumsum()
        self.usd_deposits = deposits.ffill()



