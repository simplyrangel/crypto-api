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
from kucoin._api import apiwrapper

# ------------------------------------------
# set up portfolio. 
# ------------------------------------------
# api wrapper setup:
lcc_api_key = "bin/kucoin-large-cap-coins-key.secret"
kuapi = apiwrapper()
kuapi.read_keyfile(lcc_api_key)

# large cap coin accounts information:
lcc_accounts = kuapi.query("/api/v1/accounts")
print(lcc_accounts)
#lcc_accounts = pd.DataFrame(lcc_accounts)
#lcc_accounts = lcc_accounts.set_index("currency")
#lcc_accounts.to_excel("bin/lcc-accounts.xlsx")
