import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import time
import pickle as pkl
import sys

# pandas Index Slices:
idx = pd.IndexSlice

# plot setup:
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
plt.rcParams.update(
    {"font.size": 14, 
     "figure.figsize": (10,6),
    "lines.linewidth": 3,
    })

# Coinbase API:
sys.path.append("/home/johnrangel/Projects/crypto-api")
from kucoin._api import apiwrapper
from kucoin.account import account
from kucoin.markets import price_history

# ------------------------------------------------------------
# set up portfolio. 
# ------------------------------------------------------------
# api wrapper setup:
lcc_api_key = "bin/kucoin-system76-personal-laptop.secret"
kuapi = apiwrapper()
kuapi.read_keyfile(lcc_api_key)

# large cap coin accounts information:
#lcc_accounts = kuapi.query("/api/v1/accounts")
#lcc_accounts = pd.DataFrame(lcc_accounts["data"])
#lcc_accounts.to_excel("bin/kc-accounts.xlsx")

# ------------------------------------------------------------
# Account ledgers. 
# Note that ledger API requests are restricted to 18 requests 
# per 3 seconds, or 6 requests per second. Each request is
# paginated. The default number of results per request is 50,
# and the maximum number of requests is 500 per page. 
#
# Account ledger requests have optional startAt and endAt 
# time definitions, in UTC milliseconds. The start and end
# time range cannot exceed 24 hours. 
# 
# All this means we have to discretize account ledger requests
# per day, ensure each day's results do not exceed the max
# pagination results bound, and combine the data locally. 
#
# My trading frequency will likely never exceed a few 
# transactions per day, so I can ignore the pagination max 
# results value for now, since I have to discretize my results
# date range per day anyways. 
# ------------------------------------------------------------
def ledger_request(currency,di,de):
    # discretize date range into 24 hour increments:
    date_range = pd.date_range(
        di,
        de,
        freq="D",
        )
    
    # loop over each 24 hour increment:
    ledger_endpoint = "/api/v1/accounts/ledgers"
    request_template = "%s?currency=%s&startAt=%d&endAt=%d"
    frames = []
    for start_date in date_range:
        end_date = start_date + timedelta(days=1)
        te = int(end_date.timestamp()*1000)
        ti = int(start_date.timestamp()*1000)
        request = request_template%(
            ledger_endpoint,
            currency,
            ti,
            te,
            )
        ledger_output = kuapi.query(request)
        ledger_data = ledger_output["data"]
        if ledger_data["totalNum"] > 0:
            for item in ledger_data["items"]:
                s = pd.Series(item)
                frames.append(s)
        
        # make sure we never exceed 6 requests per second:
        time.sleep(0.17)
        
    # concatenate results into single dataframe and process
    # contents as necessary before returning:
    if len(frames) > 0:
        results = pd.concat(frames,axis=1).transpose()
        results.loc[:,"createdAt"] = results.createdAt.apply(
            lambda x: datetime.fromtimestamp(x/1000))
    else:
        results=None
    return results

# let's look at RNDR account ledger:
di = "2021-11-01"
de = "2021-11-27"
#coin_ledger = ledger_request("RNDR",di,de)
#iotx_ledger = ledger_request("IOTX",di,de)
#coin_ledger.to_excel("bin/kc-rndr-ledger.xlsx")
#iotx_ledger.to_excel("bin/kc-iotx-ledger.xlsx")

# ------------------------------------------------------------
# Account fills. 
# Account fills requests allow retrieval of data up to 
# one week from start of last day (7*24 hours).
#
# Requests limited to 9 times every 3 seconds.
# ------------------------------------------------------------
def fills_request(currency_pair,di,de):
    # discretize date range into 7 day increments:
    date_range = pd.date_range(
        di,
        de,
        freq="W",
        )
    
    # loop over each seven day increment:
    fills_endpoint = "/api/v1/fills"
    request_template = "%s?symbol=%s&pageSize=500&startAt=%d&endAt=%d"
    frames = []
    for start_date in date_range:
        end_date = start_date + timedelta(days=7)
        te = int(end_date.timestamp()*1000)
        ti = int(start_date.timestamp()*1000)
        request = request_template%(
            fills_endpoint,
            currency_pair,
            ti,
            te,
            )
        fills_output = kuapi.query(request)
        fills_data = fills_output["data"]
        if fills_data["totalNum"] > 0:
            for item in fills_data["items"]:
                s = pd.Series(item)
                frames.append(s)

    # concatenate results into single dataframe and process
    # contents as necessary before returning:
    if len(frames) > 0:
        results = pd.concat(frames,axis=1).transpose()
        results.loc[:,"createdAt"] = results.createdAt.apply(
            lambda x: datetime.fromtimestamp(x/1000))
    else:
        results=None
    return results

# Let's take a look at RNDR-USDT fills: 
di = "2021-10-01"
de = "2021-11-27"
#rndr_fills = fills_request("RNDR-USDC",di,de)
#print(rndr_fills)

# ------------------------------------------------------------
# KuCoin account() class.
# ------------------------------------------------------------
di = "2021-11-01"
de = "2021-11-27"

# do the same as above, but with the Kucoin account class:
for coin in ["RNDR","IOTX"]:
    coin_account = account(coin,lcc_api_key)
    coin_account.set_date_range(di,de)
    coin_account.get_ledger()
    coin_account.get_usd_fills()
    coin_ledger = coin_account.return_ledger()
    rndr_usd_fills = coin_account.return_usd_fills()
    coin_ledger.to_excel("bin/%s-ledger.xlsx"%coin)
    rndr_usd_fills.to_excel("bin/%s-usd-fills.xlsx"%coin)

    # get USD deposits:
    coin_account.extract_deposits()
    coin_usd_deposits = coin_account.return_deposits()
    print(coin_usd_deposits)

    # get balance sheet:
    coin_account.extract_balance_sheet()
    coin_balance_sheet = coin_account.return_balance_sheet()
    print(coin_balance_sheet)

    # get performance data:
    coin_account.extract_performance()
    perf = coin_account.return_performance_data()
    perf.to_excel("bin/%s-performance.xlsx"%coin)
    print(perf)





