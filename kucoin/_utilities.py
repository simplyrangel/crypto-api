"""Utilities to support KuCoin account class."""
from datetime import datetime

def update_createdAt(df):
    df.loc[:,"createdAt"] = df.createdAt.apply(
        lambda x: datetime.fromtimestamp(x/1000)
        )

def ledger_request_url(
    name,
    ti,
    te,
    page_size=500,
    ): 
    endpoint = "/api/v1/accounts/ledgers"
    options = [
        "currency=%s"%name,
        "startAt=%d"%ti,
        "endAt=%d"%te,
        "pageSize=%d"%page_size,
        ]
    options = "&".join(options)
    return "%s?%s"%(endpoint,options)
    
def fill_request_url(
    symbol,
    ti,
    te,
    page_size=500,
    ):
    endpoint = "/api/v1/fills"
    options = [
        "symbol=%s"%symbol,
        "startAt=%d"%ti,
        "endAt=%d"%te,
        "pageSize=%d"%page_size,
        ]
    options = "&".join(options)
    return "%s?%s"%(endpoint,options)
