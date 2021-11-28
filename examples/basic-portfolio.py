import numpy as np
import pandas as pd
import sys

# KuCoin API:
sys.path.append("/home/johnrangel/Projects/crypto-api")
from kucoin.account import account as kuaccount

# Coinbase API:
from cbpro._api import apiwrapper
from cbpro.account import account as cbaccount

# generic portfolio:
from portfolio import portfolio

# create portfolio object:
lcc_portfolio = portfolio("lcc_portfolio")

# ----------------------------------------------------------------
# # KuCoin accounts.
# ----------------------------------------------------------------
# get kucoin accounts and add to the large cap coin portfolio:
kucoin_api_key = "bin/kucoin-system76-personal-laptop.secret"
di = "2021-11-01"
de = "2021-11-28"
kucoin_accounts = ["RNDR","IOTX"]
for coin in kucoin_accounts:
    coin_account = kuaccount(coin,kucoin_api_key)
    coin_account.set_date_range(di,de)
    coin_account.standard_setup()
    lcc_portfolio.add_account(coin_account)

# ----------------------------------------------------------------
# # Coinbase accounts.
# ----------------------------------------------------------------
# define coinbase pro accounts:
cbpro_coins = [
    "BTC",
    "XYO",
    "ETH",
    "AVAX",
    "ALGO",
    "WLUNA",
    "SOL",
    "LTC",
    "ADA",
    "MATIC",
    "POLY",
    "DOT",
    "LINK",
    "BNT",
    "DASH",
    "UNI",
    "XTZ",
    "AAVE",
    "COTI",
    "QNT",
    "FET",
    "EOS",
    "ATOM",
    ]

# extract coinbase pro account id's:
coinbase_api_key = "bin/coinbase-pro-system76-laptop.secret"
cbapi = apiwrapper()
cbapi.read_keyfile(coinbase_api_key)
cb_accounts = cbapi.query("/accounts")
cb_accounts = pd.DataFrame(cb_accounts).set_index("currency")

# add each coinbase pro account to the portfolio:
for coin in cbpro_coins:
    coin_id = cb_accounts.loc[coin,"id"]
    coin_account = cbaccount(coin,coin_id,coinbase_api_key)
    coin_account.standard_setup()
    lcc_portfolio.add_account(coin_account)

# ----------------------------------------------------------------
# # Portfolio performance.
# ----------------------------------------------------------------
lcc_portfolio.aggregate_accounts()





