from __future__ import division
from optimizer import optimizer, print_optimization, plot_performance
import datetime as dt


def print_and_test_optimization(
        dt_start, dt_end, 
        arr_stock_symbols, weight_increment,
        true_sharpe, true_vol, true_average_ret, true_cum_ret, 
        true_allocation):

    def check_metrics(
            sharpe, vol, average_ret, cum_ret, allocation,
            true_sharpe, true_vol, true_average_ret, true_cum_ret, 
            true_allocation):
        print("deviance from truth, sharpe ratio: {b}".format(
            b=sharpe - true_sharpe))
        print("deviance from truth, vol: {b}".format(
            b=vol - true_vol))
        print("deviance from truth, average daily ret: {b}".format(
            b=average_ret - true_average_ret))
        print("deviance from truth, cum ret: {b}".format(
            b=cum_ret - true_cum_ret))
        print("deviance from truth, allocation {b}".format(
            b=allocation - true_allocation))

        
    str_start_dt = "date_start: %s" % dt_start
    str_end_dt = "date_end: %s" % dt_end
    str_stock_symbols = "stock symbols: %s" % arr_stock_symbols
    print("\nTest\n{dt_start}\n{dt_end}\n{symbols}".format(
        dt_start=str_start_dt,
        dt_end=str_end_dt,
        symbols=str_stock_symbols))
    allocations, arr_met = optimizer(dt_start, dt_end, arr_stock_symbols, 0.1)
    check_metrics(arr_met[3], arr_met[2], arr_met[1], arr_met[0], allocations,
            true_sharpe, true_vol, true_average_ret, true_cum_ret, 
            true_allocation)
    plot_performance(dt_start, dt_end, arr_stock_symbols, allocations)
    


def main(dic_inputs, dic_true_metrics):

    print_and_test_optimization(
            dic_inputs["dt_start"], dic_inputs["dt_end"], 
            dic_inputs["arr_stock_symbols"], dic_inputs["weight_increment"],
            dic_true_metrics["sharpe"], dic_true_metrics["vol"],
            dic_true_metrics["average_ret"], dic_true_metrics["cum_ret"],
            dic_true_metrics["allocation"])


if __name__ == "__main__":
    arr_dic_inputs = []
    arr_dic_true_metrics = []
    # Add test case
    arr_dic_inputs.append(
            {"dt_start": dt.datetime(2011, 1, 1),
            "dt_end": dt.datetime(2011, 12, 31),
            "arr_stock_symbols": ["AAPL", "GLD", "GOOG", "XOM"],
            "weight_increment": 0.1}
            )
    arr_dic_true_metrics.append(
            {"sharpe": 1.02828403099,
            "vol": 0.0101467067654,
            "average_ret": 0.000657261102001,
            "cum_ret": 1.16487261965,
            "allocation": [.4, .4, 0, .2]}
            )
    # Add test case
    arr_dic_inputs.append(
            {"dt_start": dt.datetime(2010, 1, 1),
            "dt_end": dt.datetime(2010, 12, 31),
            "arr_stock_symbols": ['AXP', 'HPQ', 'IBM', 'HNZ'],
            "weight_increment": 0.1}
            )
    arr_dic_true_metrics.append(
            {"sharpe": 1.29889334008,
            "vol": 0.00924299255937,
            "average_ret": 0.000756285585593,
            "cum_ret": 1.1960583568,
            "allocation": [0, 0, 0, 1]}
            )

    for dic_inputs, dic_true_metrics in zip(arr_dic_inputs,
            arr_dic_true_metrics):
        main(dic_inputs, dic_true_metrics)
