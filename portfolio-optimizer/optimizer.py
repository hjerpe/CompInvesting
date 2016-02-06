'''
Assessing an optimal equity allocation w.r.t. the Sharpe Ratio.
(this is not a realistic way to build a strong portfolio going forward).
'''

from __future__ import print_function, division
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def portfolio_metrics(date_start, date_end, arr_stock_symbols, arr_allocations):
    '''Returns an array containing the 
    -The cumulative return of the total portfolio.
    -The average daily return of the total portfolio.
    -The standard deviation of the daily returns.
    -The sharpe ratio (assuming 252 trading days/y, risk free rate = 0
     and that stock returns follows a lognormal distribution).'''


    # Get dates
    date_time_of_day = dt.timedelta(hours=16)
    arr_date_time_stamps = du.getNYSEdays(date_start, date_end, date_time_of_day)

    # Read data
    conn_dataobj = da.DataAccess("Yahoo")
    arr_keys = ["open", "high", "low", "close", "volume", "actual_close"]
    arr_dfs_data = conn_dataobj.get_data(arr_date_time_stamps, arr_stock_symbols,
            arr_keys)
    dic_df_data = dict(zip(arr_keys, arr_dfs_data))

    # Compute daily portfolio value
    nd_prices = dic_df_data["close"].values
    nd_prices_normalized = nd_prices / nd_prices[0, :]
    nd_allocations = np.array(arr_allocations)
    nd_allocations.shape = (1, nd_prices_normalized.shape[1])
    nd_prices_weighted = nd_allocations * nd_prices_normalized
    nd_portfolio_value = nd_prices_weighted.sum(axis=1)

    # Compute metrics: average daily return, volatility, cumulative return and
    # sharpe ratio
    nd_returns = tsu.returnize0(nd_portfolio_value.copy())
    vol = nd_returns.std()
    average_return = nd_returns.mean()
    cumulative_return = nd_portfolio_value[-1] / nd_portfolio_value[0]
    # Assumes returns ~ lognormal (Ito process)
    sharpe_ratio = np.sqrt(252)* average_return / vol
    arr_metrics = [cumulative_return, average_return, vol, sharpe_ratio]
    return arr_metrics


def print_metrics():
    arr_symbols = ["AAPL", "GLD", "GOOG", "XOM"]
    dt_start = dt.datetime(2011, 1, 1)
    dt_end = dt.datetime(2011, 12, 31)
    allocations = [0.4, 0.4, 0, 0.2]

    arr_symbols = ['AXP', 'HPQ', 'IBM', 'HNZ']
    dt_start = dt.datetime(2010, 1, 1)
    dt_end = dt.datetime(2010, 12, 31)
    allocations = [0, 0, 0, 1]

    arr_metrics = portfolio_metrics(dt_start, dt_end, arr_symbols, allocations)
    print("Cumulative return: {v}".format(v=arr_metrics[0]))
    print("Average return: {v}".format(v=arr_metrics[1]))
    print("Volatility (stdev daily returns): {v}".format(v=arr_metrics[2]))
    print("Sharpe Ratio (Rf = 0): {v}".format(v=arr_metrics[3]))
