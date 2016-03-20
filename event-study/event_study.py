from __future__ import division
import sys
sys.path.append("./../get-market-data")
from get_market_data import dic_df_market_data

import datetime as dt
import numpy as np
import copy

import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkstudy.EventProfiler as ep


class EventHandler:
    '''Returns a frame where each entry (i,j) = 1 encodes that an event
    was triggered for equity j at time stamp i, and where entry (i,j) =
    nan denotes that the event was not triggered.
    ---- 
    The event is, at the moment, triggered when the daily return for 
    an equity drops by more or equal to 3 % while the market is up by 
    2 %.
    '''


    def __init__(self, dic_df_market_data, str_market_symbol, date_start,
            date_end):

        self.df_close = dic_df_market_data['close']
        self.df_market = df_close[str_market_symbol]
        self.df_events = copy.deepcopy(df_close)
        self.df_events = df_events * np.NAN
        self.arr_date_stamps = self.arr_date_stamps()

    def arr_date_stamps(self):
        date_time_of_day = dt.timedelta(hours=16)
        return  du.getNYSEdays(date_start, date_end, date_time_of_day)

    def is_event(dt_today, dt_yest, df_pricesymb, df_price_market): 
        '''Returns True if the event triggered else returns False.'''

        is_event = False
        symbrice_today = df_pricesymb.ix[dt_today]
        symbrice_yest = df_pricesymb.ix[dt_yest]
        marketprice_today = df_price_market.ix[dt_today]
        marketprice_yest = df_price_market.ix[dt_yest]
        symreturn_today = (symbrice_today / symbrice_yest)-1
        marketreturn_today = (marketprice_today / marketprice_yest)-1
        
        if symreturn_today <= -0.03 and marketreturn_today > 0.02:
            is_event = True
        return is_event
    
    def assign_events(self):

        for s_sym in df_close.keys():
            for dt_ind in xrange(1, len(self.arr_date_time_stamps)):
                dt_today = self.arr_date_time_stamps[dt_ind]
                dt_yest = self.arr_date_time_stamps[dt_ind-1]
                is_event = self.is_event(dt_today, dt_yest, 
                        self.df_close[s_sym], self.df_market)

                if is_event: 
                    self.df_events[s_sym].ix[dt_today] = 1

        return df_events

    def get_df_events():
        return self.df_events


def get_event_df(dic_df_market_data, str_market_symbol, date_start, date_end):
    '''Returns a frame where each entry (i,j) = 1 encodes that an event
    was triggered for equity j at time stamp i, and where entry (i,j) =
    nan denotes that the event was not triggered.
    ---- 
    The event is, at the moment, triggered when the daily return for 
    an equity drops by more or equal to 3 % while the market is up by 
    2 %.
    '''


    def is_event_triggered(dt_today, dt_yest, df_pricesymb, df_price_market): 
        '''Returns True if the event triggered else returns False.'''

        is_event = False
        symbrice_today = df_pricesymb.ix[dt_today]
        symbrice_yest = df_pricesymb.ix[dt_yest]
        marketprice_today = df_price_market.ix[dt_today]
        marketprice_yest = df_price_market.ix[dt_yest]
        symreturn_today = (symbrice_today / symbrice_yest)-1
        marketreturn_today = (marketprice_today / marketprice_yest)-1
        
        if symreturn_today <= -0.03 and marketreturn_today > 0.02:
            is_event = True
        return is_event

    
    df_close = dic_df_market_data['close']
    df_market = df_close[str_market_symbol]
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN

    date_time_of_day = dt.timedelta(hours=16)
    arr_date_time_stamps = du.getNYSEdays(date_start, date_end, date_time_of_day)
    for s_sym in df_close.keys():
        for dt_ind in xrange(1, len(arr_date_time_stamps)):
            dt_today = arr_date_time_stamps[dt_ind]
            dt_yest = arr_date_time_stamps[dt_ind-1]
            is_event = is_event_triggered(dt_today, dt_yest,
                    df_close[s_sym], df_market)

            if is_event: 
                df_events[s_sym].ix[dt_today] = 1

    return df_events


def write_event_study_to_disk(date_start, date_end, arr_equity_symbols, 
        str_market_symbol, pdf_to_disk_name):
    '''Writes a plot onto disk illustrating the market relative mean
    return for occuring events in between the dates date_start and 
    date_end for all equities in arr_equity_symbols relative to the 
    market str_market_symbol.'''


    arr_equity_symbols.append(str_market_symbol)
    dic_df = dic_df_market_data(date_start, date_end, arr_equity_symbols)
    eventHandler = EventHandler(dic_df, str_market_symbol, date_start, date_end)
    eventHandler.assign_events()
    df_events = eventHandler.get_df_events()
    #df_events = get_event_df(dic_df, str_market_symbol, date_start, date_end)
    print "Creating Study"
    ep.eventprofiler(df_events, dic_df, i_lookback=20, i_lookforward=20,
                    s_filename=pdf_to_disk_name, b_market_neutral=True,
                    b_errorbars=True,
                    s_market_sym=str_market_symbol)
