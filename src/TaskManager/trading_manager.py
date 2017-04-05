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
        # Todo: check buy/sell parameters
        # Todo: do orders && write to DB
        self.check_market_data()
        '''for account in self.Accounts:
            if account.check_api_connection():
                print('......successful login for - ' + account.UserName)
                account.api_test()
                account.offer_funding()
        '''

    def check_market_data(self):
        trading_pair = 'XXBTZEUR'
        interval = '1' # in minutes

        market_state = self.API.query_public('OHLC', {'pair': trading_pair,
                                                      'interval': interval})

        if len(market_state['error']) == 0:
            market_data = market_state['result'][trading_pair]

            # Data extraction of compound list
            current_period = market_data[-1]
            clean_data = market_data[:-1]
            clean_data = self.interpolate_nan(clean_data, 5)
            times = [sublist[0] for sublist in clean_data]
            vw_average = [float(sublist[5]) for sublist in clean_data]

            print('Period Start: ' + time.ctime(times[0]))
            print('Period End: ' + time.ctime(times[-1]))

            smooth_vw_average = self.smooth_data([int(i) for i in times], [float(i) for i in vw_average], 5, 'moving_average')
            derivative = self.centered_derivative(smooth_vw_average, times)
            dderivative = self.centered_derivative(derivative, times)
            zeros = self.find_zeros(derivative)
            current_val = clean_data[-1]
            plt.figure()
            plt.plot(times, [float(i) for i in vw_average], 'b--', label='original_data')
            plt.plot(times, smooth_vw_average, 'k', label='smoothed_data')
            plt.plot(times, derivative, 'r--', label='derivative')
            plt.plot(times, dderivative, 'g--', label='2nd order derivative')
            plt.show(block=True)
            # plt.show(block=True)
            print('done')
            # Todo: handle this data - compute minima/maxima
            # Todo: fit curve to market data
            # Todo: calculate maxima/minima && trend
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
        pass

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