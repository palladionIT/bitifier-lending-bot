import threading
import time
import logging

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
        # Todo: get current market data
        #
        trading_pair = 'XXBTZEUR'

        market_state = self.API.query_public('OHLC', {'pair': trading_pair,
                                                      'interval': '15'})

        if len(market_state['error']) == 0:
            market_data = market_state['result'][trading_pair]
            # Todo: handle this data - compute minima/maxima
            # Todo: fit curve to market data
            # Todo: calculate maxima/minima && trend
            # Todo: return something (buy? sell?)
        pass

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