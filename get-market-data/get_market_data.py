import datetime as dt
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da


def dic_df_market_data(date_start, date_end, arr_stock_symbols):
    '''Returns a dictionary with keys 
    'open', 'high, 'low', 'close', 'volume', 'actual_close' 
    and where each value is a data frame with the latter data, 
    specified by the key, for all equities in arr_stock_symbols.'''


    date_time_of_day = dt.timedelta(hours=16)
    arr_date_time_stamps = du.getNYSEdays(date_start, date_end, date_time_of_day)
    conn_dataobj = da.DataAccess("Yahoo")
    arr_keys = ["open", "high", "low", "close", "volume", "actual_close"]
    arr_dfs_data = conn_dataobj.get_data(arr_date_time_stamps, arr_stock_symbols,
            arr_keys)
    return dict(zip(arr_keys, arr_dfs_data))
