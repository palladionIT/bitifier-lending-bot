import threading
import time
import math
#import logging

from configparser import ConfigParser
from src.account import Account
from src.api.bfxapi.bfxapi import BFXAPI

class FundingManager(threading.Thread):

    DBConnector = None
    DBLock = None
    API = None
    Accounts = []
    Logger = None
    run_interval = 300

    # Execution Counter for clean tasks
    RunCounter = 0

    # Account information
    # [USD, BTC, ...]
    balance = {'usd': 0, 'btc': 0}
    limit = {'usd': 50, 'btc': -1}

    # Account information
    # [USD, BTC, ...]
    exchange_rate = {'btc': 0}

    # Account Margin Lend Parameters
    # [USD, BTC, ...]
    offers = {'usd': [], 'btc': []}
    loan_time = {'usd': 2, 'btc': 2}
    min_loan_spread = {'usd': 25000, 'btc': 25000}
    max_loan_spread = {'usd': 100000, 'btc': 100000}
    spread_cnt = {'usd': 5, 'btc': 3}
    min_lend_rate = {'usd': 0.05, 'btc': 0.0175}
    high_hold_amount = {'usd': 150, 'btc': 0.1}
    high_hold_limit = {'usd': 0.15, 'btc': 0.1}  # Interest rate / year
    high_hold_threshold = {'usd': 40, 'btc': 40}

    def __init__(self, db_connector, db_lock, accounts, api, config, logger):
        # Todo: pass necessary arguments || create objects here
        super(FundingManager, self).__init__()
        self.DBConnector = db_connector
        self.DBLock = db_lock
        self.Accounts = accounts
        self.API = api
        self.Logger = logger
        self.update_config(config)

    def update_config(self, config):
        self.loan_time = {key: int(val) for (key, val) in config['loan_time'].items()}
        self.min_loan_spread = {key: int(val) for (key, val) in config['min_loan_spread'].items()}
        self.max_loan_spread = {key: int(val) for (key, val) in config['max_loan_spread'].items()}
        self.spread_cnt = {key: int(val) for (key, val) in config['spread_cnt'].items()}
        self.min_lend_rate = {key: float(val) for (key, val) in config['min_lend_rate'].items()}
        self.high_hold_amount = {key: float(val) for (key, val) in config['high_hold_amount'].items()}
        self.high_hold_limit = {key: float(val) for (key, val) in config['high_hold_limit'].items()}
        self.high_hold_threshold = {key: int(val) for (key, val) in config['high_hold_threshold'].items()}

    def run(self):
        while True:
            print('Running ' + str(self.run_interval / 60) + ' minute task')
            self.RunCounter += 1

            if self.RunCounter >= 6:
                for account in self.Accounts:
                    print('Updating configuration settings for funding.')
                    self.update_config(self.load_config(account.UserID))
                    self.RunCounter = 0
            self.run_frequent_task()
            print('Finished Running ' + str(self.run_interval / 60) + ' minute task')
            time.sleep(self.run_interval)

    def run_frequent_task(self):
        '''for account in self.Accounts:
            if account.check_api_connection():
                print('......successful login for - ' + account.UserName)
                account.api_test()
                account.offer_funding()
        '''
        self.offer_funding()

    def offer_funding(self):
        try:
            self.clear_active_offers()
            self.get_available_funds()
            self.load_exchange_rates()
            self.calculate_limts()
            offers = self.calculate_offers()

            for currency, loans in offers.items():  # Todo: write information to database
                for loan in loans:
                    success, return_code, response = self.API.funding_new_offer(currency=currency,
                                                                                amount=loan['amt'],
                                                                                rate=loan['rate'],
                                                                                period=loan['time'],
                                                                                direction='lend')

                    if not success:
                        print('Error ' + return_code + ' creating funding lends.')
                        print (str(response))
        except Exception as e:
            #self.Logger.error('FUNDING MANAGER ')
            print('FUNDING MANAGER: Error while handling recurring task.')
            print(e)


    def clear_active_offers(self,):
        offers = self.get_active_offers()

        for offer in offers:
            success, return_code, response = self.API.funding_cancel_offer(offer['id'])

            if not success:
                print('Error ' + return_code + ' cancelling active funding lends.')
                print(str(response))

    def get_active_offers(self):
        success, return_code, response = self.API.funding_active_offer()

        if not success:
            print('Error ' + return_code + ' retrieving active funding lends.')
            print(str(response))
        else:
            return response

    def get_taken_offers(self):
        pass

    def get_account_history(self):
        pass

    def get_available_funds(self):
        success, return_code, response = self.API.get_wallet_balance()

        if success:
            for info in response:
                if info['type'] == 'deposit':
                    self.balance[info['currency']] = float(info['available'])

    def calculate_offers(self):
        amount_asks = 1000
        amount_bids = 0
        offers = {}

        for currency, balance in self.balance.items():
            loans = []
            if balance >= self.limit[currency]:
                cnt = 1
                available = balance

                fundbook = self.API.get_fundingbook(currency=currency,
                                                    limit_asks=str(amount_asks),
                                                    limit_bids=str(amount_bids))[2]

                # Calculate if lendbook is even in the neighbourhood of our desired high lend position
                do_high_lend = False
                lendbook_aggregate = 0
                for book_entry in fundbook['asks']:
                    lendbook_aggregate += float(book_entry['amount'])
                    if float(book_entry['rate']) >= self.high_hold_limit[currency] * 365:
                        # Todo more sophisticated distance calculation
                        if lendbook_aggregate <= 3 * self.max_loan_spread[currency]:
                            do_high_lend = True
                        else:
                            do_high_lend = False

                if self.high_hold_amount[currency] > self.limit[currency] and do_high_lend:
                    # If we have enough funds place order
                    if available > self.high_hold_amount[currency]:
                        available -= self.high_hold_amount[currency]

                        loans.append({'amt': str(balance if self.high_hold_amount[currency] > balance else self.high_hold_amount[currency]),
                                      'rate': str(self.high_hold_limit[currency] * 365),
                                      'time': 30
                                      })
                    # Else reserve the money and wait
                    else:
                        available -= self.high_hold_amount[currency]

                if available > self.limit[currency]:

                    split_cnt = self.spread_cnt[currency]
                    split_amount = math.floor((available / split_cnt) * 100) / 100
                    while split_amount < self.limit[currency]:  # Todo: also implement min value split behaviour
                        split_cnt -= 1
                        if split_cnt > 0:
                            split_amount = math.floor((available / split_cnt) * 100) / 100
                        else:
                            split_cnt = 1
                            split_amount = available
                            break

                    if split_cnt >= 1:
                        lendbook_aggregate = 0
                        split_climb = ((self.max_loan_spread[currency] - self.min_loan_spread[currency]) / (split_cnt - 1 )) if (split_cnt -1 ) > 0 else 0
                        next_loan = self.min_loan_spread[currency]

                        min_rate_annual = self.min_lend_rate[currency] * 365

                        for book_entry in fundbook['asks']:
                            lendbook_aggregate += float(book_entry['amount'])
                            while lendbook_aggregate >= next_loan and cnt <= split_cnt:
                                loans.append({'amt': str(split_amount),
                                              'rate': str(float(book_entry['rate']) - 0.0001 if (float(book_entry['rate']) - 0.0001) > min_rate_annual else min_rate_annual),
                                              'time': 30 if self.high_hold_threshold[currency] > 0 and float(book_entry['rate']) > self.high_hold_threshold[currency] * 365 else 2
                                              })
                                next_loan += split_climb
                                cnt += 1

                            if cnt > split_cnt:
                                break
            offers[currency] = loans
        return offers

    def usd_from_btc(self, btc):
        btc_price = self.API.get_ticker('btcusd')[2]
        return btc * float(btc_price['last_price'])

    def load_exchange_rates(self):
        symbols = self.API.get_symbols()[2]
        for symbol in symbols:
            if symbol[3:] == 'usd':
                symbol_info = self.API.get_ticker(symbol=symbol)[2]
                self.exchange_rate[symbol[:3]] = float(symbol_info['last_price'])

    def calculate_limts(self):
        for currency, rate in self.exchange_rate.items():
            self.limit[currency] = self.limit['usd'] / rate
            self.min_loan_spread[currency] = self.min_loan_spread['usd'] / rate
            self.max_loan_spread[currency] = self.max_loan_spread['usd'] / rate

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