import sys
sys.path.append("./../get-market-data")
from get_market_data import dic_df_data

import datetime as dt
import numpy as np
import copy

import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkstudy.EventProfiler as ep


def get_event_df(dic_df_share_prices, str_market_symbol, date_start, date_end):
    
    df_close = dic_df_share_prices['close']
    df_market = df_close[str_market_symbol]

    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN

    date_time_of_day = dt.timedelta(hours=16)
    arr_date_time_stamps = du.getNYSEdays(date_start, date_end, date_time_of_day)

    arr_symbols = [sym for sym in df_close.keys() if sym != str_market_symbol]
    for s_sym in arr_symbols:

        for dt_ind in xrange(1, len(arr_date_time_stamps)):

            dt_today = arr_date_time_stamps[dt_ind]
            dt_yest = arr_date_time_stamps[dt_ind-1]

            symprice_today = df_close[s_sym].ix[dt_today]
            symprice_yest = df_close[s_sym].ix[dt_yest]
            marketprice_today = df_market.ix[dt_today]
            marketprice_yest = df_market.ix[dt_yest]

            symreturn_today = (symprice_today / symprice_yest)-1
            marketreturn_today = (marketprice_today / marketprice_yest)-1

            if symreturn_today <= -0.03 and marketreturn_today > 0.02:
                df_events[s_sym].ix[dt_today] = 1

    return df_events


ls_symbols = ["IBM", "GOOG", "XOM", "MSFT", "GS", "JP"]
str_market_symbol = "SPY"
ls_symbols.append(str_market_symbol)
dt_start = dt.datetime(2006, 1, 1)
dt_end = dt.datetime(2010, 12, 31)


dic_df = dic_df_data(dt_start, dt_end, ls_symbols)
df_events = get_event_df(dic_df, str_market_symbol, dt_start, dt_end)
dic_df_close = dic_df["close"]

print "Creating Study"
ep.eventprofiler(df_events, dic_df, i_lookback=20, i_lookforward=20,
                s_filename='MyEventStudy.pdf', b_market_neutral=True,
                b_errorbars=True,
                s_market_sym=str_market_symbol)
