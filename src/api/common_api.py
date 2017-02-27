import abc


class CommonApi(object):
    __metaclass__ = abc.ABCMeta

    # Checks if authentication is possible
    @abc.abstractmethod
    def check_authentication(self, account):
        return

    # =========================
    # Unauthenticated endpoints
    # =========================

    # Get ticker information of exchange
    # BFX - get_ticker
    # Kraken - get ticker information
    @abc.abstractmethod
    def get_ticker(self, asset):
        return

    # Get tradeable assets
    # BFX - get_symbols
    # Kraken  - get tradeable asset pairs
    @abc.abstractmethod
    def get_symbols(self):
        return

    # Get asset information
    # BFX - get_symbols_details
    # Kraken - get asset info
    @abc.abstractmethod
    def get_symbols_details(self, asset, info = None, aclass = None):
        return

    # Get statistics about symbol
    # BFX - get_statistics
    # Kraken - get OHCL data
    @abc.abstractmethod
    def get_statistics(self, symbol, interval=None, since=None):
        return

    # Get order book of symbol
    # BFX - get_orderbook
    # Kraken - get order book
    @abc.abstractmethod
    def get_orderbook(self, symbol, limit_bids=None, limit_asks=None):
        return

    # Get trades for symbol
    # BFX - get_trades
    # Kraken - get recent trades
    @abc.abstractmethod
    def get_trades(self, symbol, timestamp=None, limit_trades=None):
        return