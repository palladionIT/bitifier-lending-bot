import threading
import time
import logging
import numpy as np

from configparser import ConfigParser
from src.account import Account
from krakenex import API

# debug imports
import matplotlib.pyplot as plt

class TradingManager(threading.Thread):

    DBConnector = None
    DBLock = None
    API = None
    Accounts = []
    Logger = None
    run_interval = 60

    RunCounter = 0

    def __init__(self, db_connector, db_lock, accounts, api, logger):
        # Todo: pass necessary arguments || create objects here
        self.DBConnector = db_connector
        self.DBLock = db_lock
        self.Accounts = accounts
        self.API = api
        self.Logger = logger

    def run(self):
        # Todo: implement exception handling that restarts everything after upon next run
        while True:
            print('Running ' + str(self.run_interval / 60) + ' minute task')
            self.RunCounter += 1

            if self.RunCounter >= 6:
                for account in self.Accounts:
                    account.update_config(self.load_config(account.UserID))
                    self.RunCounter = 0
            self.run_frequent_task()
            print('Finished Running  ' + str(self.run_interval / 60) + '  minute task')
            time.sleep(self.run_interval)

    def run_frequent_task(self):
        # Todo: get last order from DB
        #       RETURN last order type && amount / value, DIFFERENCE
        # Todo: get market data and analyze - DONE
        #       CALL (difference)
        #       RETURN [INTERVALS, MARKET_DATA, EXTREMA]
        # Todo: check buy/sell parameters
        #       CALL (intervals, market_data, extrema)
        #       get current asset info from exchange
        #       does last order and current market combination require an action?
        #       RETURN ACTION to do
        # Todo: do orders && write to DB
        #       CALL (action)
        #       do ACTION and calculate the properties of order
        last_trade = self.get_last_action()
        market_state = self.check_market_data(3)
        action = self.check_conditions(market_state[0], market_state[1], market_state[2], market_state[3])
        '''for account in self.Accounts:
            if account.check_api_connection():
                print('......successful login for - ' + account.UserName)
                account.api_test()
                account.offer_funding()
        '''

    def get_last_action(self):
        # Todo: return last action from database
        trade = None
        try:
            trade = self.DBConnector.ExchangeTrades.select().order_by(self.DBConnector.ExchangeTrades.id.desc()).get()
        except self.DBConnector.ExchangeTrades.DoesNotExist:
            print('ERROR - TRADING MANAGER - could not retrieve last trade.')
            trade = None
        #User.select().order_by(User.id.desc()).get()
        return trade

    def check_market_data(self, diff):
        market_dat = None

        trading_pair = 'XXBTZEUR'
        interval_size = '1' # in minutes

        market_state = self.API.query_public('OHLC', {'pair': trading_pair,
                                                      'interval': interval_size})

        if len(market_state['error']) == 0:
            market_data = market_state['result'][trading_pair]

            # Data extraction of compound list
            current_period = market_data[-1]
            clean_data = market_data[:-1]
            clean_data = self.interpolate_nan(clean_data, 5)
            interval_times = [sublist[0] for sublist in clean_data]
            vw_average = [float(sublist[5]) for sublist in clean_data]  # volume weighted data

            print('Period Start: ' + time.ctime(interval_times[0]))
            print('Period End: ' + time.ctime(interval_times[-1]))

            smooth_vw_average = self.smooth_data([int(i) for i in interval_times], [float(i) for i in vw_average], 15, 'moving_average')
            derivative = self.centered_derivative(smooth_vw_average, interval_times)
            # dderivative = self.centered_derivative(derivative, times)
            # zeros = self.find_zeros(derivative)
            filtered_z = self.find_extrema(interval_times, smooth_vw_average, diff)
            # current_val = clean_data[-1]

            market_dat = [current_period, interval_times, smooth_vw_average, filtered_z]

            self.display_graph(interval_times, smooth_vw_average, filtered_z)
            # Todo: handle this data - compute minima/maxima - DONE
            # Todo: fit curve to market data
            # Todo: calculate maxima/minima - DONE
            # Todo: calculate trend
            # Todo: return something (buy? sell?)
            # methods:
            # https://stackoverflow.com/questions/7061071/finding-the-min-max-of-a-stock-chart
            # https://en.wikipedia.org/wiki/Moving_average#Other_weightings
            # en.wikipedia.org/wiki/Local_regression
            # https://en.wikipedia.org/wiki/Kernel_smoother
            # https://en.wikipedia.org/wiki/Moving_least_squares
            #
            ###############
            # Further applied reading:
            # http://connor-johnson.com/2014/11/23/time-series-forecasting-in-python-and-r/
            # https://www.quantstart.com/articles/Forecasting-Financial-Time-Series-Part-1
            # http://fluid-turb.wikidot.com/time-series-analysis
            # https://www.quantstart.com/articles/Beginners-Guide-to-Time-Series-Analysis
            # chrome-extension://lnagobkdlgiobpknboclgafebmkoocce/scripts/externalLibraries/pdf/web/viewer.html?file=http%3A%2F%2Fwww.petertessin.com%2FTimeSeries.pdf
            # chrome-extension://lnagobkdlgiobpknboclgafebmkoocce/scripts/externalLibraries/pdf/web/viewer.html?file=http%3A%2F%2Fconference.scipy.org%2Fscipy2011%2Fslides%2Fmckinney_time_series.pdf
            # https://nbviewer.jupyter.org/github/changhiskhan/talks/blob/master/pydata2012/pandas_timeseries.ipynb
            # https://nbviewer.jupyter.org/github/jvns/talks/blob/master/pyconca2013/pistes-cyclables.ipynb
            # https://nbviewer.jupyter.org/github/lge88/UCSD_BigData/blob/master/notebooks/weather/Weather%20Analysis.ipynb
            #
            ###############
            # Indicators (trend)
            # RSI relative strength index
        return market_dat

    def check_conditions(self, current_interval, interval_times, market_data, extrema):
        # Todo: check current conditions
        # Todo: check *current* market price
        # Todo: check SAFEGUARD (no loss)
        # Todo: return action
        return None

    def interpolate_nan(self, data, row):
        for i, d in enumerate(data):
            if float(d[row]) == 0:
                # Check for borders
                if i != 0 and i < len(data):
                    p = data[i - 1]
                    n = data[i + 1]
                if i == 0:
                    p = data[i + 1]
                    n = data[i + 1]
                if i == len(data) - 1:
                    p = data[i - 1]
                    n = data[i - 1]

                # Check for 0 values
                if float(p[row]) == 0 or float(n[row]) == 0:
                    # Interpolate <open, close> and se
                    if i != 0 and i < len(data):
                        p[row] = str((float(data[i - 1][1]) + float(data[i - 1][4])) / 2)
                        n[row] = str((float(data[i + 1][1]) + float(data[i + 1][4])) / 2)
                    if i == 0:
                        p[row] = str((float(data[i + 1][1]) + float(data[i + 1][4])) / 2)
                        n[row] = str((float(data[i + 1][1]) + float(data[i + 1][4])) / 2)
                    if i == len(data) - 1:
                        p[row] = str((float(data[i - 1][1]) + float(data[i - 1][4])) / 2)
                        n[row] = str((float(data[i - 1][1]) + float(data[i - 1][4])) / 2)
                data[i][row] = str((float(p[row]) + float(n[row])) / 2)

        return data

    def smooth_data(self, x_dat, y_dat, interval, type):
        smoothed_data = None
        if type == 'moving_average':
            # Adds border extension to avoid artifacts for convolution
            # Gets size of window for given timeframe
            # Convolves and trims padding elements
            interval_s = interval * 60
            x_ind = np.argmax(np.asarray([x - x_dat[0] for x in x_dat]) >= interval_s)
            window = np.ones(int(x_ind))/float(x_ind)
            padding_start = [y_dat[0]] * x_ind # To extend at the border to remove border error
            padding_end = [y_dat[-1]] * x_ind
            smoothed_data = np.convolve(padding_start+y_dat+padding_end, window, 'same')[x_ind:-x_ind].tolist()

        return smoothed_data

    def centered_derivative(self, x_dat, t, type='centered'):
        d = []
        if type == 'forward':
            d_t = t[1] - t[0]
            x_dat = [x_dat[0], x_dat]
            d = (np.diff(x_dat) / d_t).tolist()

        if type == 'centered':
            # Maybe normalize with t
            d = np.gradient(x_dat).tolist()
        return d

    def find_zeros(self, x_dat):
        zeros = []
        for i in range(len(x_dat) - 1):
            if x_dat[i] > 0 and x_dat[i + 1] < 0:
                zeros.append([i, i + 1, -1])
            if x_dat[i] < 0 and x_dat[i + 1] > 0:
                zeros.append([i, i + 1, 1])
        return zeros
        # return np.where(np.array(list(map(abs, x_dat))) <= margin)[0]

    def clean_extrema(self, zeros, y_dat, diff=None):
        z = []
        # Calculate correct position of extrema
        for i, d in enumerate(zeros):
            if d[2] < 0:
                if y_dat[d[0]] < y_dat[d[1]]:
                    zeros[i].insert(0, d[1])
                else:
                    zeros[i].insert(0, d[0])
            else:
                if y_dat[d[0]] > y_dat[d[1]]:
                    zeros[i].insert(0, d[1])
                else:
                    zeros[i].insert(0, d[0])

        # Remove small intermediary minima
        if diff:
            for i, d in enumerate(zeros):
                if i > 0:
                    prev = (y_dat[z[-1][1]] + y_dat[z[-1][2]]) / 2
                    curr = (y_dat[d[1]] + y_dat[d[2]]) / 2
                    # check if next is alternating extrema
                    # if yes -> add
                    # if no -> check if new is better
                    if z[-1][3] == d[3]:
                        if d[3] > 0:  # minimum
                            if curr < prev:
                                z[-1] = d
                        else:  # maximum
                            if curr > prev:
                                z[-1] = d
                    else:
                        if abs(curr - prev) > diff:
                            z.append(d)
                    '''if abs(curr - prev) > diff:
                        # check if is alternating extrema
                        # if yes -> add
                        # if no -> check if new is better
                        if z[-1][2] == d[2]:
                            if d[2] > 0: # minimum
                                if curr < prev:
                                    z[-1] = d
                            else: # maximum
                                if curr > prev:
                                    z[-1] = d
                        else:
                            z.append(d)'''
                else:
                    z.append(d)
        else:
            z = zeros

        return z

    def find_extrema(self, x_dat, y_dat, diff=None):
        derivative = self.centered_derivative(y_dat, x_dat)
        extrema = self.clean_extrema(self.find_zeros(derivative), y_dat, diff)
        return extrema

    def display_graph(self, x_dat, y_dat, extrema=None):
        plt.figure()
        # plt.plot(times, [float(i) for i in vw_average], 'b--', label='original_data')
        plt.plot(x_dat, y_dat, 'k', label='smoothed_data')
        # plt.plot(times, derivative, 'r--', label='derivative')
        # plt.axhline(y=0)
        # plt.plot(times, dderivative, 'g--', label='2nd order derivative')
        '''for z in zeros:
            pass
            # plt.axvline(x=times[z[0]], color='r')'''
        for z in extrema:
            c = 'b'
            if z[3] < 0:
                c = 'g'
            plt.axvline(x=x_dat[z[0]], color=c)
        '''for z in zeros:
            plt.axvline(x=times[z[1]])'''
        plt.xticks([x_dat[i] for i in range(0, len(x_dat), 30)],
                   [time.ctime(x_dat[i]) for i in range(0, len(x_dat), 30)])
        plt.show(block=True)
        # plt.show(block=True)
        print('done')

    @staticmethod
    def load_config(acc_id):
        config = {}

        account = 'acc_' + str(acc_id)

        parser = ConfigParser()
        parser.read('config/config.ini')

        for name, value in parser.items(account):
            item = name.split('-')
            currency = item[-1]
            item = item[0]

            if item not in config:
                config[item] = {}

            config[item][currency] = value

        return config