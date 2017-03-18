import threading
import time
import logging
import numpy as np

from configparser import ConfigParser
from src.account import Account
from krakenex import API

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
            times = [sublist[0] for sublist in clean_data]
            vw_average = [sublist[5] for sublist in clean_data]

            smooth_vw_average = self.smooth_data([int(i) for i in times], [float(i) for i in vw_average], 5, 'moving_average')
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
        pass

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
            smoothed_data = np.convolve(padding_start+y_dat+padding_end, window, 'same')[x_ind:-x_ind]

        return smoothed_data


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