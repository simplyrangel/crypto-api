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
        api_key_file,
        save_loc="bin",
        ):
        apiwrapper.__init__(self,api_key_file)
        self.name = name
        self.save_loc = save_loc
        self.holdings = None
        self.ledger = None
        self.daily_history = None
        self.usd_deposits = None
        
    def auto_setup(self):
        self.get_holdings()
        self.get_ledger()
        self.get_daily_history()
        self.get_usd_deposits()
        
    def save(self):
        self.holdings.to_excel("%s/%s-holdings.xlsx"%(
            self.save_loc,
            self.name,
            ))
        self.ledger.to_excel("%s/%s-ledger.xlsx"%(
            self.save_loc,
            self.name,
            ))
        self.daily_history.to_excel("%s/%s-daily-history.xlsx"%(
            self.save_loc,
            self.name,
            ))
        self.usd_deposits.to_excel("%s/%s-usd-deposits.xlsx"%(
            self.save_loc,
            self.name,
            ))
        with open("%s/%s.pkl"%(self.save_loc,self.name),"wb") as of:
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
        usd_ledger = self.ledger.loc[idx["USD",:],:].reset_index(
            ).set_index("created_at",
            )
        usd_ledger = usd_ledger[usd_ledger.transfer_type=="deposit"]
        usd_ledger = usd_ledger.resample("D").sum()
        usd_ledger = usd_ledger[usd_ledger.amount>0]

        # add to deposits dataframe and forward fill:
        deposits.loc[
            usd_ledger.index,
            "total",
            ] = usd_ledger.amount.cumsum()
        self.usd_deposits = deposits.ffill()



