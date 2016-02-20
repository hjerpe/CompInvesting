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
import sys
sys.path.append("./../../Combinatorics")
from combinatorics import order_increment_array, \
        ordered_selection_without_repetition


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


def optimizer(date_start, date_end, arr_stock_symbols, weight_increment):
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

    generator_allocations = gen_possible_allocations(num_equities, 
            weight_increment)
    for nd_allocation in generator_allocations:
        nd_allocation.shape = (1, nd_prices_normalized.shape[1])
        nd_prices_weighted = nd_allocation * nd_prices_normalized
        nd_portfolio_value = nd_prices_weighted.sum(axis=1)

        portfolio_metrics = arr_portfolio_metrics(nd_portfolio_value)
        curr_sharpe = portfolio_metrics[-1]
        if curr_sharpe > best_sharpe:
            best_metrics = portfolio_metrics
            best_sharpe = curr_sharpe
            best_allocation = nd_allocation

    return (best_allocation, best_metrics)


def gen_possible_allocations(num_equities, weight_increment):
    '''Returns a generator which yields all possible allocations 
    a1,a2,..,an such that sum(ai) = 1. Each allocation is given as a np array.
    weight_increment must be on form 1/q where q is an integer.
    '''


    num_weight_increments = int(1 / weight_increment)
    weights = np.array([i for i in xrange(num_weight_increments+1)])
    weights = weights * weight_increment

    base_allocation = np.array([0 for i in xrange(num_equities)])
    base_allocation[-1] = num_weight_increments

    set_duplicates = set()
    bol_new_allocation = True
    int_clear_duplicates = 1e5

    # Yield all possible non zero allocation weight combinations
    while bol_new_allocation:

        # Form all possible non zero weight selections
        non_zero_weight_ind = [x for x in base_allocation if x > 0]
        possible_permutations = ordered_selection_without_repetition(
                num_equities, len(non_zero_weight_ind))

        for perm in possible_permutations:
            allocation = [0 for i in xrange(num_equities)]
            # Add all non-zero weight allocations
            for weight_ind, alloc_ind in enumerate(perm):
                allocation[alloc_ind] = weights[non_zero_weight_ind[weight_ind]]

            allocation = tuple(allocation)
            if allocation not in set_duplicates:
                set_duplicates.add(allocation)
                yield np.array(allocation)
                if len(set_duplicates) > int_clear_duplicates: 
                    set_duplicates.clear()
                
        # Increment base allocation array
        bol_new_allocation = order_increment_array(base_allocation,
                num_weight_increments)



def arr_portfolio_metrics(nd_portfolio_value):
    '''Returns an array containing, given an np array of portfolio values 
    over time, 
    -The cumulative return of the total portfolio.
    -The average daily return of the total portfolio.
    -The standard deviation of the daily returns.
    -The sharpe ratio (assuming 252 trading days/y, risk free rate = 0,
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


def plot_performance(dt_start, dt_end, arr_stock_symbols, nd_weights):
    ''''Plot the performance of each individual equity together with the
    portfolio.'''


    dic_df = dic_df_data(dt_start, dt_end, arr_stock_symbols)
    nd_prices = dic_df["close"].values
    nd_prices_normalized = nd_prices / nd_prices[0, :]

    nd_weights.shape = (1, nd_prices_normalized.shape[1])
    nd_prices_weighted = nd_weights * nd_prices_normalized
    nd_portfolio_value = nd_prices_weighted.sum(axis=1)
    nd_portfolio_value = nd_portfolio_value / nd_portfolio_value[0]

    arr_stock_symbols.append("portfolio")
    dt_timeofday = dt.timedelta(hours=16)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
    plt.clf()
    plt.xticks(rotation=70)
    plt.plot(ldt_timestamps, nd_prices_normalized)
    plt.plot(ldt_timestamps, nd_portfolio_value)
    plt.legend(arr_stock_symbols)
    plt.ylabel('Normalized Close')
    plt.xlabel('Date')
    plt.show()
