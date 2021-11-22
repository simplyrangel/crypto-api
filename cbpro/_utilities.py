import numpy as np
import pandas as pd
idx = pd.IndexSlice

def new_history_df(
    columns,
    start,
    end,
    frequency="D",
    ):
    df_index = pd.date_range(
        start,
        end,
        freq=frequency,
        tz=None,
        )
    return pd.DataFrame(
        np.nan,
        index=df_index,
        columns=columns,
        )
    
