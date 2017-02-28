import abc
import krakenex
import logging

from .common_api import CommonApi
from src.accountt import Account

class KrakenAPI(CommonApi):

    api = None

    def __init__(self, key, secret):
        print('...setting up bitfinex api')

        self.APIKey = key
        self.APISecret = secret

        self.api = krakenex.API()

    def update_credentials(self, account):
        self.api.key = account.APIKey
        self.api.secret = account.APISecret

    def invalidate_credentials(self):
        self.api.key = ''
        self.api.secret = ''


    def query_public(self, path, parameters, account):
        self.update_credentials(account)

        response = self.api.query_public(path, parameters)
        # Todo: request shit and process it to create 3 tuple return

        self.invalidate_credentials()
        return ['stuff', 'to', 'return']


    # Checks if authentication is possible
    def check_authentication(self, account):

        self.update_credentials(account)

        valid = True

        success, return_code = self.query_public('AssetPairs', {'info': 'fees'})[0:2]
        valid = valid and success

        # Todo: access account_info endpoint and query to check for login connection
        # success, return_code = self.

        return valid and success

    # =========================
    # Unauthenticated endpoints
    # =========================

    # Get ticker information of exchange
    # Kraken - get ticker information
    def get_ticker(self, asset):
        return

    # Get tradeable assets
    # Kraken  - get tradeable asset pairs
    def get_symbols(self):
        return

    # Get asset information
    # Kraken - get asset info
    def get_symbols_details(self, asset, info=None, aclass=None):
        return

    # Get statistics about symbol
    # Kraken - get OHCL data
    def get_statistics(self, symbol, interval=None, since=None):
        return

    # Get order book of symbol
    # Kraken - get order book
    def get_orderbook(self, symbol, limit_bids=None, limit_asks=None):
        return

    # Get trades for symbol
    # Kraken - get recent trades
    def get_trades(self, symbol, timestamp=None, limit_trades=None):
        return