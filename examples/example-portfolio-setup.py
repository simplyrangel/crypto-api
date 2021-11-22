import numpy as np
import pandas as pd
from datetime import datetime
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
sys.path.append("/home/jrangel/Projects/crypto/crypto-api")
from cbpro._api import apiwrapper
from cbpro.account import account

# ------------------------------------------
# set up portfolio. 
# ------------------------------------------
# api wrapper setup:
lcc_api_key = "bin/large-cap-coins-key.secret"
cbapi = apiwrapper()
cbapi.read_keyfile(lcc_api_key)

# large cap coin accounts information:
lcc_accounts = cbapi.query("/accounts")
lcc_accounts = pd.DataFrame(lcc_accounts)
lcc_accounts = lcc_accounts.set_index("currency")
lcc_accounts.to_excel("bin/lcc-accounts.xlsx")

# define lcc coins:
lcc_coins = [
    "AAVE",
    "ADA",
    "ALGO",
    "ATOM",
    "AVAX",
    "BNT",
    "BTC",
    "COTI",
    "DASH",
    "DOT",
    "EOS",
    "ETH",
    "FET",
    "LINK",
    "LTC",
    "MATIC",
    "POLY",
    "QNT",
    "SOL",
    "UNI",
    "WLUNA",
    "XTZ",
    "XYO",
    "IOTX",
    ]

# ------------------------------------------
# plot performances. 
# ------------------------------------------
with PdfPages("bin/0-performance.pdf") as pdf:
    for coin in lcc_coins:
        coin_id = lcc_accounts.loc[coin,"id"]
        coin_account = account(coin,coin_id,lcc_api_key)
        coin_account.standard_setup()
        df = coin_account.return_performance_data()
        
        # plot performance:
        plt.figure()
        plt.title("%s account performance"%coin)
        plt.plot(
            df.index,
            df.performance,
            color="blue",
            label="%s return: %.2fx"%(coin,df.performance.iloc[-1])
            )
        plt.axhline(
            1.0,
            color="black",
            label="deposit value norm.",
            )
        plt.legend()
        plt.grid()
        plt.xlabel("datetime")
        plt.ylabel("USD deposits / account value")
        pdf.savefig()
        plt.close()
        
        # plot deposit and account USD values:
        usd_deposits_label= "total USD deposits: $%.2f"%(
            df.usd_deposits.iloc[-1],
            )
        coin_value_label = "%s account USD value: $%.2f"%(
            coin,
            df.coin_usd_value.iloc[-1],
            )
        plt.figure()
        plt.title("%s value and cumulative deposits"%coin)
        plt.plot(
            df.index,
            df.coin_usd_value,
            color="blue",
            label=coin_value_label,
            )
        plt.plot(
            df.index,
            df.usd_deposits,
            color="black",
            label=usd_deposits_label,
            )
        plt.legend()
        plt.grid()
        plt.xlabel("datetime")
        plt.ylabel("USD value [$]")
        pdf.savefig()
        plt.close()
    
    
    








