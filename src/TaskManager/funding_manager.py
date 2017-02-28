import threading
import time

from configparser import ConfigParser
from src.account import Account
from src.appi.bfxapi import BFXAPI

class FundingManager(threading.Thread):

    DBConnector = None
    DBLock = None
    API = None
    Accounts = []

    RunCounter = 0

    def __init__(self, db_connector, db_lock, accounts, api):
        # Todo: pass necessary arguments || create objects here
        self.DBConnector = db_connector
        self.DBLock = db_lock
        self.Accounts = accounts
        self.API = api

    def run(self):
        # Todo: refactor time loop code to be run here
        # Todo: implement exception handling that restarts everything after upon next run
        while True:
            print('Running 10 minute task')
            self.run_counter += 1

            if self.run_counter >= 6:
                for account in self.Accounts:
                    account.update_config(self.load_config(account.UserID))
                    self.run_counter = 0
            self.run_frequent_task()
            print('Finished Running 10 minute task')
            time.sleep(600)

    def run_frequent_task(self):
        for account in self.Accounts:
            if account.check_api_connection():
                print('......successful login for - ' + account.UserName)
                account.api_test()
                account.offer_funding()

    # TODO: remove this debugging function
    def arch_change(self):
        for acc in self.Accounts:
            # self.API.check_authentication(acc)
            success, code, response = self.API.get_ticker({'symbol': 'USD'})

            # TODO: CONTINUE HERE AFTER AWS OUTAGE - TEST ALL API CALLS && UPDATE METHODS

            if success != True:
                print('shit!')

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