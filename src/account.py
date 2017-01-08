from configparser import ConfigParser
import hmac
import hashlib
import time
import json
import base64

from .api import API as api
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
        self.API = api(key, secret)

    def check_api_connection(self):
        print('...checking login state of account')

        api_path = '/account_infos'
        valid = True

        success, return_code = self.API.get_request(url_path='/symbols')[0:2]
        valid = valid and success
        success, return_code = self.API.post_request(url_path=api_path)[0:2]

        return valid and success

    def get_active_offers(self):
        success, return_code, response = self.API.post_request(url_path='/offers')

        for offer in response:
            print('process order')
            #Todo: process active orders

    def get_taken_offers(self):
        success, return_code, response = self.API.post_request(url_path='/credits')

        for offer in response:
            print('process order')
            #Todo: process active orders

    def get_account_history(self, currency, start = None, end = None, limit = None, wallet = None):

        post_data = {}
        post_data['currency'] = currency
        if start:
            post_data['since'] = start # datetime object
        if end:
            post_data['until'] = end # datetime object
        if limit:
            post_data['limit'] = limit # integer
        if start:
            post_data['wallet'] = wallet # string 'trading' || 'exchange' || 'deposit'

        # Todo: CONTINUE fix post data encoding problem

        success, return_code, response = self.API.post_request(url_path='/history', post_params=post_data)

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