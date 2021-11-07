import numpy as np
import pandas as pd
idx = pd.IndexSlice

def format_price_history(out):
    df = pd.DataFrame(out)
    df.loc[:,0] = pd.to_datetime(df[0], unit="s")
    df.columns = [
        "date",
        "low",
        "high",
        "open",
        "close",
        "volume",
        ]
    return df.set_index("date")

def ledger2df(ledger_output):
    for adict in ledger_output:
        for key, item in adict.pop("details").items():
            adict[key] = item
    return pd.DataFrame(ledger_output)

def update_ledger(mdf):
    # update multiindex dataframe column 
    # types as necessary:
    mdf.loc[idx[:,:],"created_at"] = pd.to_datetime(
        mdf.loc[
            idx[:,:],
            "created_at",
            ],
        )
    for col in ["amount","balance"]:
        mdf.loc[idx[:,:],col] = mdf.loc[idx[:,:],col].astype(float)

    # remove timezone information for more
    # straightforward IO:
    mdf.loc[idx[:,:],"created_at"] = mdf.created_at.apply(
        lambda x: x.replace(tzinfo=None),
        )

    # reset multiindex as [coin,created_at]:
    mdf = mdf.reset_index().set_index(["coin", "created_at"])
    return mdf
