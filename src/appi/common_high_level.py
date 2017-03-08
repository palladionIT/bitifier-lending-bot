import abc


class CommonHighLevel(object):
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
    def get_ticker(self, parameter):
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
    def get_symbols_details(self, parameter):
        return

    # Get statistics about symbol
    # BFX - get_statistics
    # Kraken - get OHCL data
    @abc.abstractmethod
    def get_statistics(self, parameter):
        return

    # Get order book of symbol
    # BFX - get_orderbook
    # Kraken - get order book
    @abc.abstractmethod
    def get_orderbook(self, parameter):
        return

    # Get trades for symbol
    # BFX - get_trades
    # Kraken - get recent trades
    @abc.abstractmethod
    def get_trades(self, parameter):
        return