from configparser import ConfigParser
import hmac
import hashlib
import time
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

    def __init__(self, id, mail, name, key, secret):
        print('...setting up account')

        self.UserID = id
        self.UserMail = mail
        self.UserName = name
        self.API = bfxapi(key, secret)

    def check_api_connection(self):
        print('...checking login state of account')

        return self.API.check_authentication()

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