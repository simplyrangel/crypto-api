"""Individual Coinbase Pro trading account."""
import numpy as np
import pandas as pd
from datetime import datetime

# cbpro toolset:
from cbpro.markets import price_history
from cbpro._api import apiwrapper
import cbpro._utilities as utils

# Pandas Index Slices:
idx = pd.IndexSlice

# accounts class:
class account(
    apiwrapper,
    ):
    def __init__(
        self,
        name,
        account_id,
        api_key_file=None,
        ):
        apiwrapper.__init__(self)
        self.read_keyfile(api_key_file)
        self.name = name
        self.account_id = account_id
        self.ledger=pd.DataFrame()
        self.usd_fills=pd.DataFrame()
        self.deposits=pd.DataFrame()
        self.balance_sheet=pd.DataFrame()
        self.performance_data=pd.DataFrame()
        self._url_setup()

    def standard_setup(self):
        if self.name=="USD":
            self.get_ledger()
            self.extract_balance_sheet()
        else:
            self.get_ledger()
            self.get_usd_fills()
            self.extract_deposits()
            self.extract_balance_sheet()
            self.extract_performance()

    def save_as_spreadsheet(self,loc):
        fi = "%s/%s-cbpro-data.xlsx"%(loc,self.name)
        with pd.ExcelWriter(fi) as writer:
            ledger = self.return_ledger()
            usd_fills = self.return_usd_fills()
            deposits = self.return_deposits()
            balance_sheet = self.return_balance_sheet()
            perf = self.return_performance_data()
            ledger.to_excel(writer,sheet_name="ledger")
            usd_fills.to_excel(writer,sheet_name="usd_fills")
            deposits.to_excel(writer,sheet_name="deposits")
            balance_sheet.to_excel(writer,sheet_name="balance_sheet")
            perf.to_excel(writer,sheet_name="portfolio_performance")

    def get_ledger(self):
        try:
            query_output = self.query(self.LEDGER_URL)
            self._setup_ledger(query_output)
            print("%s account loaded successfully..."%self.name)
        except:
            self.ledger = None
            print("%s account empty..."%self.name)

    def return_ledger(self):
        if type(self.ledger) is pd.DataFrame:
            return self.ledger.copy()
        else:
            return None

    def get_usd_fills(self):
        query_output = self.query(self.USD_FILLS_URL)
        self._setup_fills(query_output)
    
    def return_usd_fills(self):
        if type(self.usd_fills) is pd.DataFrame:
            return self.usd_fills.copy()
        else:
            return None

    def extract_deposits(self):
        usd_fills = self.return_usd_fills()
        sell_idx = usd_fills[usd_fills.side=="sell"].index
        usd_fills.loc[sell_idx,"usd_volume"] *= -1.0
        usd_fills = usd_fills.resample("D").sum()
        cols = [
            "usd",
            "coin",
            ]
        deposits = utils.new_history_df(
            cols,
            start=self.start_date,
            end=self.end_date,
            )
        tdates = usd_fills.index
        deposits.loc[tdates,"usd"] = usd_fills.usd_volume
        self.deposits = deposits

    def return_deposits(self):
        if type(self.deposits) is pd.DataFrame:
            return self.deposits.copy()
        else:
            return None

    def extract_balance_sheet(self,frequency="D"):
        col = "num_%s"%self.name
        df = utils.new_history_df(
            [col],
            start=self.start_date,
            end=self.end_date,
            frequency=frequency,
            )
        ledger = self.return_ledger().resample(frequency).last()
        df.loc[ledger.index,col] = ledger.balance.copy()
        df = df.ffill()
        self.balance_sheet = df

    def return_balance_sheet(self):
        if type(self.balance_sheet) is pd.DataFrame:
            return self.balance_sheet.copy()
        else:
            return None    

    def extract_performance(
        self,
        granularity=86400, #daily
        ):
        ph = price_history(
            pair="%s-USD"%self.name,
            start=self.start_date,
            end=self.end_date,
            granularity=granularity,
            )
        cols = [
            "usd_deposits",
            "number_of_coins",
            ]
        df = utils.new_history_df(
            cols,
            start=self.start_date,
            end=self.end_date,
            )
        deposits = self.return_deposits()
        ledger = self.return_ledger().resample("D").last()
        df.loc[deposits.index,"usd_deposits"] = deposits.usd.cumsum()
        df.loc[ledger.index,"number_of_coins"] = ledger.balance.copy()
        df["coin_price"] = ph.open.copy()
        df = df.ffill()
        df["coin_usd_value"] = df.coin_price*df.number_of_coins
        df["performance"] = df.coin_usd_value/df.usd_deposits
        self.performance_data = df
    
    def return_performance_data(self):
        if type(self.performance_data) is pd.DataFrame:
            return self.performance_data.copy()
        else:
            return None

    def _setup_ledger(self,query_output):
        df = pd.DataFrame(query_output)
        df.loc[:,"id"] = df.id.apply(int)
        self._unnest_dict(df)
        self._correct_datetime(df)
        for col in ["amount","balance"]:
            df.loc[:,col] = df[col].apply(float)
        self.ledger=df.set_index("created_at")
        self.start_date = df.created_at.iloc[-1].date()
        self.end_date = datetime.now().date()
    
    def _setup_fills(self,query_output):
        df = pd.DataFrame(query_output)
        self._correct_datetime(df)
        for col in ["price","size","fee","usd_volume"]:
            df.loc[:,col] = df[col].apply(float)
        self.usd_fills = df.set_index("created_at")

    def _unnest_dict(self,df):
        for col in ["order_id","product_id","trade_id"]:
            try:
                data = df.details.apply(lambda x: x[col])
                df[col] = data
            except:
                pass

    def _correct_datetime(self,df):
        df.loc[:,"created_at"] = pd.to_datetime(df.created_at)
        df.loc[:,"created_at"] = df.created_at.apply(
            lambda x: x.replace(tzinfo=None),
            )

    def _url_setup(self,fills_number=100):
        self.LEDGER_URL = "/accounts/%s/ledger"%(self.account_id)
        self.USD_FILLS_URL = "/fills?product_id=%s-USD"%(self.name)







