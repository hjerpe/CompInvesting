from optimizer import optimizer, print_optimization
import datetime as dt


def print_and_test_optimization():

    def check_metrics(
            sharpe, vol, average_ret, cum_ret, allocation,
            cor_sharpe, cor_vol, cor_average_ret, cor_cum_ret, cor_allocation):
        print("deviance from truth, sharpe ratio: {b}".format(
            b=sharpe - cor_sharpe))
        print("deviance from truth, vol: {b}".format(
            b=vol - cor_vol))
        print("deviance from truth, average daily ret: {b}".format(
            b=average_ret - cor_average_ret))
        print("deviance from truth, cum ret: {b}".format(
            b=cum_ret - cor_cum_ret))
        print("deviance from truth, allocation {b}".format(
            b=allocation - cor_allocation))
            
    print("\nFirst test")
    arr_symbols = ["AAPL", "GLD", "GOOG", "XOM"]
    dt_start = dt.datetime(2011, 1, 1)
    dt_end = dt.datetime(2011, 12, 31)
    print_optimization(dt_start, dt_end, arr_symbols)
    allocations, arr_met= optimizer(dt_start, dt_end, arr_symbols)
    v1 = 1.02828403099
    v2 = 0.0101467067654
    v3 = 0.000657261102001
    v4 = 1.16487261965
    v5 = [.4, .4, 0, .2]
    print("\nDeviations from truth:")
    check_metrics(arr_met[3], arr_met[2], arr_met[1], arr_met[0], allocations,
            v1, v2, v3, v4, v5)
    
    print("\nSecond test")
    arr_symbols = ['AXP', 'HPQ', 'IBM', 'HNZ']
    dt_start = dt.datetime(2010, 1, 1)
    dt_end = dt.datetime(2010, 12, 31)
    print_optimization(dt_start, dt_end, arr_symbols)
    allocations, arr_met = optimizer(dt_start, dt_end, arr_symbols)
    v1 = 1.29889334008
    v2 = 0.00924299255937
    v3 = 0.000756285585593
    v4 = 1.1960583568
    v5 = [0, 0, 0, 1]
    print("\nDeviations from truth:")
    check_metrics(arr_met[3], arr_met[2], arr_met[1], arr_met[0], allocations,
            v1, v2, v3, v4, v5)
