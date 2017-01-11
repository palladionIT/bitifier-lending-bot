from configparser import ConfigParser
import hmac
import hashlib
import time
import math
import json
import base64

from .bfxapi import BFXAPI as bfxapi
from .databaseconnector import DatabaseConnector as db

class Account:

    UserID = None
    UserMail = None
    UserName = None
    BFXToken = None
    API = None

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
    min_lend_rate = {'usd': 0.05, 'btc': 0.045}
    high_hold_amount = {'usd': 200, 'btc': 0.1}
    high_hold_limit = {'usd': 0.2, 'btc': 0.1}  # Interest rate / year
    high_hold_threshold = {'usd': 40, 'btc': 40}

    def __init__(self, id, mail, name, key, secret):
        print('...setting up account')

        self.UserID = id
        self.UserMail = mail
        self.UserName = name
        self.API = bfxapi(key, secret)

    def check_api_connection(self):
        print('...checking login state of account')

        return self.API.check_authentication()

    def offer_funding(self):

        self.get_available_funds()
        self.load_exchange_rates()
        self.calculate_limts()
        offers = self.calculate_offers()

        for currency, loans in offers.items():  # Todo: write information to database
            for loan in loans:
                self.API.funding_new_offer(currency=currency,
                                           amount=loan['amt'],
                                           rate=loan['rate'],
                                           period=loan['time'],
                                           direction='loan')


    def get_active_offers(self):
        success, return_code, response = self.API.funding_active_offer()

        for offer in response:
            print('process order')
            #Todo: process active orders

    def get_taken_offers(self):
        success, return_code, response = self.API.funding_active_funding_used()

        for offer in response:
            print('process order')
            #Todo: process active orders

    def get_account_history(self, currency, start = None, end = None, limit = None, wallet = None):

        success, return_code, response = self.API.history_balance(currency='usd')

        for entry in response:
            print('process order')
            #Todo: process active orders

    def get_day_returns(self):
        print('...retrieving 1 day returns of account')
        # TODO: access database

    def get_30day_returns(self):
        print('...retrieving 30 day returns of account')
        # TODO: access database

    def get_all_returns(self):
        print('...retrieving all returns of account')
        # TODO: access database

    def get_return_info(self):
        print('...retrieving full return information of account')
        # TODO: access database

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

        # Todo: update loan spread interval for currencies

        for currency, balance in self.balance.items():
            loans = []
            if balance != self.limit[currency]:  # Todo: fix this condition to >=
                cnt = 1
                available = balance
                available = 500

                if self.high_hold_amount[currency] > self.limit[currency]:
                    available -= self.high_hold_amount[currency]

                    loans.append({'amt': balance if self.high_hold_amount[currency] > balance else self.high_hold_amount[currency],
                                  'rate': self.high_hold_limit[currency] * 365,
                                  'time': 30
                                  })

                if available > self.limit[currency]:
                    fundbook = self.API.get_fundingbook(currency=currency,
                                                        limit_asks=str(amount_asks),
                                                        limit_bids=str(amount_bids))[2]

                    split_cnt = self.spread_cnt[currency]
                    split_amount = math.floor((available / split_cnt) * 100) / 100
                    while split_amount < self.limit[currency]:
                        split_cnt -= 1
                        split_amount = math.floor((available / split_cnt) * 100) / 100

                    if split_cnt >= 1:
                        lendbook_aggregate = 0
                        split_climb = ((self.max_loan_spread[currency] - self.min_loan_spread[currency]) / (split_cnt -1 ))
                        next_loan = self.min_loan_spread[currency]

                        min_rate_annual = self.min_lend_rate[currency] * 365

                        for book_entry in fundbook['asks']:
                            lendbook_aggregate += float(book_entry['amount'])
                            while lendbook_aggregate >= next_loan and cnt <= split_cnt:
                                loans.append({'amt': split_amount,
                                              'rate': float(book_entry['rate']) - 0.0001 if (float(book_entry['rate']) - 0.0001) > min_rate_annual else min_rate_annual,
                                              'time': 30 if self.high_hold_threshold[currency] > 0 and float(book_entry['rate']) > self.high_hold_threshold[currency] * 365 else 2
                                              })
                                next_loan += split_climb
                                cnt += 1
            offers[currency] = loans
        return offers

    def usd_from_btc(self, btc):
        btc_price = self.API.get_ticker('btcusd')[2]
        return btc * float(btc_price['last_price'])

    def load_exchange_rates(self):
        # Todo: get all symbols
        # Todo: get exchangerates for all symbols
        # Todo: set rate for all symbols
        symbols = self.API.get_symbols()[2]
        for symbol in symbols:
            if symbol[3:] == 'usd':
                symbol_info = self.API.get_ticker(symbol=symbol)[2]
                self.exchange_rate[symbol[:3]] = float(symbol_info['last_price'])

    def calculate_limts(self):
        for currency, rate in self.exchange_rate.items():
            self.limit[currency] = self.limit['usd'] / rate

    def calculate_spread_limits(self):
        # Todo: iterated all cryptocurrencies
        # Todo: calculate equivalent value
        # Todo: update in list
        pass

    def api_test(self):
        self.get_active_offers()
        self.get_taken_offers()
        self.get_account_history('usd')
        print('TEST - history deposit withdraw')
        success, return_code, response = self.API.history_deposit_withdraw(currency='usd')
        print('RESULT - success: ' + str(success)
              + ' | response code: ' + str(return_code) + ' | response: ' + str(response))

        print('TEST - history past trades')
        success, return_code, response = self.API.history_past_trades(symbol='BTCUSD',timestamp=str(time.time()-1000000000))
        print('RESULT - success: ' + str(success)
              + ' | response code: ' + str(return_code) + ' | response: ' + str(response))
        print('TEST - history past trades')

        success, return_code, response = self.API.funding_active_funding_unused()
        print('RESULT - success: ' + str(success)
              + ' | response code: ' + str(return_code) + ' | response: ' + str(response))

        success, return_code, response = self.API.funding_taken()
        print('RESULT - success: ' + str(success)
              + ' | response code: ' + str(return_code) + ' | response: ' + str(response))

        # Todo: test when funding available
        #success, return_code, response = self.API.funding_new_offer('USD', 300, 40, 2, 'lend')
        print('RESULT - success: ' + str(success)
              + ' | response code: ' + str(return_code) + ' | response: ' + str(response))

        # Todo: test when offer available
        #success, return_code, response = self.API.funding_cancel_offer(10000)
        print('RESULT - success: ' + str(success)
              + ' | response code: ' + str(return_code) + ' | response: ' + str(response))

        success, return_code, response = self.API.funding_offer_status(10000)
        print('RESULT - success: ' + str(success)
              + ' | response code: ' + str(return_code) + ' | response: ' + str(response))

        success, return_code, response = self.API.funding_active_credit()
        print('RESULT - success: ' + str(success)
              + ' | response code: ' + str(return_code) + ' | response: ' + str(response))

        success, return_code, response = self.API.funding_active_offer()
        print('RESULT - success: ' + str(success)
              + ' | response code: ' + str(return_code) + ' | response: ' + str(response))

        success, return_code, response = self.API.funding_active_funding_used()
        print('RESULT - success: ' + str(success)
              + ' | response code: ' + str(return_code) + ' | response: ' + str(response))

        print('\n\n=========GET REQUESTS========\n\n')

        success, return_code, response = self.API.get_lends(currency='USD', limit=500)
        print('RESULT - success: ' + str(success)
              + ' | response code: ' + str(return_code) + ' | response: ' + str(response))

        success, return_code, response = self.API.get_fundingbook(currency='USD', limit_bids=500, limit_asks=0)
        print('RESULT - success: ' + str(success)
              + ' | response code: ' + str(return_code) + ' | response: ' + str(response))

        success, return_code, response = self.API.get_orderbook('btcusd')
        print('RESULT - success: ' + str(success)
              + ' | response code: ' + str(return_code) + ' | response: ' + str(response))

        success, return_code, response = self.API.get_symbols()
        print('RESULT - success: ' + str(success)
              + ' | response code: ' + str(return_code) + ' | response: ' + str(response))

        success, return_code, response = self.API.get_symbols_details()
        print('RESULT - success: ' + str(success)
              + ' | response code: ' + str(return_code) + ' | response: ' + str(response))

        success, return_code, response = self.API.get_trades('btcusd')
        print('RESULT - success: ' + str(success)
              + ' | response code: ' + str(return_code) + ' | response: ' + str(response))

        success, return_code, response = self.API.get_ticker('btcusd')
        print('RESULT - success: ' + str(success)
              + ' | response code: ' + str(return_code) + ' | response: ' + str(response))

        success, return_code, response = self.API.get_statistics('btcusd')
        print('RESULT - success: ' + str(success)
              + ' | response code: ' + str(return_code) + ' | response: ' + str(response))

        success, return_code, response = self.API.get_wallet_balance()
        print('RESULT - success: ' + str(success)
              + ' | response code: ' + str(return_code) + ' | response: ' + str(response))

        success, return_code, response = self.API.get_summary()
        print('RESULT - success: ' + str(success)
              + ' | response code: ' + str(return_code) + ' | response: ' + str(response))