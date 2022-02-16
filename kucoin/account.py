"""Individual KuCoin trading account.

Assumes USD fills made with USDT. 
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import time

# KuCoin toolset:
from kucoin._api import apiwrapper
from kucoin.markets import price_history
import kucoin._utilities as utils
import kucoin._messages as messages

# Pandas index slices:
idx = pd.IndexSlice

# accounts class:
class account(apiwrapper):
    def __init__(
        self,
        name,
        api_key_file=None,
        verbose=True,
        ):
        apiwrapper.__init__(self)
        self.read_keyfile(api_key_file)
        self.name=name
        self.verbose_flag = verbose
        self.usd_pair="%s-USDT"%name
        self.ledger=pd.DataFrame()
        self.usd_fills=pd.DataFrame()
        self.deposits=pd.DataFrame()
        self.balance_sheet=pd.DataFrame()
        self.performance_data=pd.DataFrame()

    def set_date_range(self,di,de):
        self.start_date = di
        self.end_date = de

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
        fi = "%s/%s-kucoin-data.xlsx"%(loc,self.name)
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
        date_range = self._discretize_date_range("ledger")
        frames = []
        for start_date in date_range:
            end_date = start_date + timedelta(days=1)
            messages.ledger(
                self.verbose_flag,
                self.name,
                start_date,
                end_date,
                )
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
            results = results.set_index("createdAt")
            for col in ["amount","fee","balance"]:
                results.loc[:,col] = results[col].apply(float)
            results = results.sort_index()
            
            # multiply purchase amounts by negative 1:
            negid = results[
                (results.direction=="out")
                & (results.accountType=="TRADE")
                ].index
            results.loc[negid,"amount"] *= -1.0
            
            # calculate balance and return:
            results.loc[:,"balance"] = results.amount.cumsum()
            self.ledger=results
    
    def return_ledger(self):
        return self.ledger.copy()

    def get_usd_fills(self):
        date_range = self._discretize_date_range("fill")
        frames = []
        for start_date in date_range:
            end_date = start_date + timedelta(days=7)
            messages.usd_fills(
                self.verbose_flag,
                self.name,
                start_date,
                end_date,
                )
            te = int(end_date.timestamp()*1000)
            ti = int(start_date.timestamp()*1000)
            request = utils.fill_request_url(self.usd_pair,ti,te)
            output = self.query(request)
            output_data = output["data"]
            if output_data["totalNum"] > 0:
                for item in output_data["items"]:
                    s = pd.Series(item)
                    frames.append(s)
            
            # make sure we never exceed 3 requests per second:
            time.sleep(0.33)
        
        # concatenate results into single dataframe:
        if len(frames) > 0:
            results = pd.concat(frames,axis=1).transpose()
            utils.update_createdAt(results)
            results = results.set_index("createdAt")
            for col in ["price","size","funds","fee"]:
                results.loc[:,col] = results[col].apply(float)
            self.usd_fills = results
    
    def return_usd_fills(self):
        return self.usd_fills.copy()

    def extract_deposits(self):
        usd_fills = self.return_usd_fills()
        usd_fills["usd_volume"] = usd_fills.funds + usd_fills.fee
        usd_fills = usd_fills[
            (usd_fills.side=="buy")
            ].resample("D"
            ).sum(
            )
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
        return self.deposits.copy()

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
        return self.balance_sheet.copy()

    def extract_performance(
        self,
        granularity=86400, #daily
        ):
        ph = price_history(
            pair="%s-USDT"%self.name,
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
        balance_sheet = self.return_balance_sheet()
        num_coins = balance_sheet["num_%s"%self.name].copy()
        df.loc[deposits.index,"usd_deposits"] = deposits.usd.cumsum()
        df.loc[balance_sheet.index,"number_of_coins"] = num_coins
        df["coin_price"] = ph.open.copy()
        df = df.ffill()
        df["coin_usd_value"] = df.coin_price*df.number_of_coins
        df["performance"] = df.coin_usd_value/df.usd_deposits
        self.performance_data = df
    
    def return_performance_data(self):
        return self.performance_data.copy()

    def _discretize_date_range(self,request_type):
        freqbin = {
            "ledger": "D",
            "fill": "7D",
            }
        return pd.date_range(
            self.start_date,
            self.end_date,
            freq=freqbin[request_type]
            )
    
    
    
    
    
