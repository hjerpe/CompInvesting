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
from itertools import permutations


def dic_df_data(date_start, date_end, arr_stock_symbols):
    '''Returns a dictionary with keys open, high, low, close, volume, 
    actual_close and where each value being a data frame for every equity 
    in arr_stock_symbols.'''


    date_time_of_day = dt.timedelta(hours=16)
    arr_date_time_stamps = du.getNYSEdays(date_start, date_end, date_time_of_day)
    conn_dataobj = da.DataAccess("Yahoo")
    arr_keys = ["open", "high", "low", "close", "volume", "actual_close"]
    arr_dfs_data = conn_dataobj.get_data(arr_date_time_stamps, arr_stock_symbols,
            arr_keys)
    return dict(zip(arr_keys, arr_dfs_data))


def optimizer(date_start, date_end, arr_stock_symbols):
    '''Returns an optimal equity allocation over the equities in
    arr_stock_symbols w.r.t. the sharpe ratio.'''


    dic_df = dic_df_data(date_start, date_end, arr_stock_symbols)
    nd_prices = dic_df["close"].values
    nd_prices_normalized = nd_prices / nd_prices[0, :]

    # Get best allocation w.r.t. the shape ratio
    num_equities = len(arr_stock_symbols)
    best_metrics = [0 for i in xrange(num_equities)]
    best_sharpe = 0
    best_allocation = [0 for i in xrange(num_equities)]

    arr_possible_allocations = all_possible_allocations(num_equities)
    for nd_allocation in arr_possible_allocations:
        nd_allocation.shape = (1, nd_prices_normalized.shape[1])
        nd_prices_weighted = nd_allocation * nd_prices_normalized
        nd_portfolio_value = nd_prices_weighted.sum(axis=1)

        portfolio_metrics = li_portfolio_metrics(nd_portfolio_value)
        curr_sharpe = portfolio_metrics[-1]
        if curr_sharpe > best_sharpe:
            best_metrics = portfolio_metrics
            best_sharpe = curr_sharpe
            best_allocation = nd_allocation

    return (best_allocation, best_metrics)
    

def all_possible_allocations(num_equities):
    '''Returns an array of all possible allocations a1, a2, .., an such that
    sum(ai) = 1. Each allocation is given as a np array.'''


    weights = [0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1]
    base_allocation = [0 for i in xrange(num_equities)]
    base_allocation[-1] = 10
    li_allocations = []
    set_duplicates = set()
    bol_new_allocation = True
    while bol_new_allocation:
        # Add all possible permutations of the base allocation
        arr_weights = tuple([weights[i] for i in base_allocation])
        gen_weights = permutations(arr_weights)
        for allocation in gen_weights:
            if allocation not in set_duplicates:
                li_allocations.append(np.array(allocation))
                set_duplicates.add(allocation)
                
        # Increment base allocation array
        bol_new_allocation = _ordered_increment_array(base_allocation)

    return li_allocations


def _ordered_increment_array(arr_ord_numbers):
    '''Mutates the list of numbers [a1,..,an] such that all numbers satisfy
    a1 <= a2 <= .. <= an and sum(ai) = 10. The increment is the smallest 
    increment such that the total order is satisfied.
    arr_ord_numbers must start at a valid configuration (a1<=a2<=..<=an).
    
    Value: bool
    True if the input array is mutated and the increment is valid, and else 
    False.'''


    ind_dec = 0
    ind_inc = 0
    for i in xrange(len(arr_ord_numbers)-1, 0, -1):
        if arr_ord_numbers[i] > arr_ord_numbers[i-1]:
            ind_dec = i
            break
    for j in xrange(ind_dec-1, -1, -1):
        ind_inc = j
        if arr_ord_numbers[ind_dec] - arr_ord_numbers[ind_inc] > 1:
            break

    # Check if relation a1 <= a2 <=... <= an holds after increment
    if ind_inc == 0:
        value_first_numbers = arr_ord_numbers[0]+1
        last_value = 10-(value_first_numbers * (len(arr_ord_numbers)-1))

        if value_first_numbers > last_value:
            return False

    arr_ord_numbers[ind_inc] += 1
    arr_ord_numbers[ind_dec] -= 1
    if arr_ord_numbers[ind_inc] + arr_ord_numbers[ind_dec] == 10: return True
    
    s = sum(arr_ord_numbers[0:ind_inc])
    for i in range(ind_inc+1, len(arr_ord_numbers)):
        s += arr_ord_numbers[ind_inc]
        if i == len(arr_ord_numbers)-1:
            arr_ord_numbers[i] = 10 - s
        else:
            arr_ord_numbers[i] = arr_ord_numbers[ind_inc]
    return True


def li_portfolio_metrics(nd_portfolio_value):
    '''Returns an array containing given an np array of portfolio value at over
    time. The returned array contains,
    -The cumulative return of the total portfolio.
    -The average daily return of the total portfolio.
    -The standard deviation of the daily returns.
    -The sharpe ratio (assuming 252 trading days/y, risk free rate = 0
     and that stock returns follows a lognormal distribution).'''


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


def print_optimization(dt_start, dt_end, arr_symbols):
    '''Prints the optimal allocation w.r.t. the sharpe ratio for
    m equities, where the set of possible allocations ranges from
    0 to 1 by 0.1 increments.'''


    allocations, arr_metrics = optimizer(dt_start, dt_end, arr_symbols)
    str_dt_start = dt_start.strftime("%B %d, %Y")
    str_dt_end = dt_end.strftime("%B %d, %Y")
    print("Start Date: {v}".format(v=str_dt_start))
    print("End Date: {v}".format(v=str_dt_end))
    print("Symbols: {v}".format(v=arr_symbols))
    print("Optimal Allocations: {v}".format(v=allocations))
    print("Sharpe Ratio (Rf = 0): {v}".format(v=arr_metrics[3]))
    print("Volatility (stdev daily returns): {v}".format(v=arr_metrics[2]))
    print("Average return: {v}".format(v=arr_metrics[1]))
    print("Cumulative return: {v}".format(v=arr_metrics[0]))
