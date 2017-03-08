from src.TaskManager.funding_manager import FundingManager
from src.TaskManager.trading_manager import TradingManager
from src.accountt import Account
from src.appi.bfxapi import BFXAPI
from src.appi.krakenapi import KrakenHighLevel

class ManagerFactory:

    @staticmethod
    def make_funding_manager(db_connector, db_lock, exchange):

        api = None
        accounts = []

        db_lock.acquire()
        for acc in db_connector.User.select():
            if acc.account_type == 'funding' and acc.status is True:
                accounts.append(
                    Account(acc.id, acc.email, acc.name, acc.apikey, acc.apisec, acc.account_type, acc.exchange, acc.status))
        db_lock.release()

        # Todo: change API initialization to init all API's that are saved in acc.exchange

        if exchange == 'bitfinex':
            api = BFXAPI()
        elif exchange == 'kraken':
            api = KrakenHighLevel()

        return FundingManager(db_connector, db_lock, accounts, api)

    @staticmethod
    def make_trading_manager(db_connector, db_lock, exchange):

        api = None
        accounts = []

        db_lock.acquire()
        for acc in db_connector.User.select():
            if acc.account_type == 'trading' and acc.status is True:
                accounts.append(
                    Account(acc.id, acc.email, acc.name, acc.apikey, acc.apisec, acc.account_type, acc.status))
        db_lock.release()

        # Todo: change API initialization to init all API's that are saved in acc.exchange

        if exchange == 'bitfinex':
            api = BFXAPI()
        elif exchange == 'kraken':
            api = KrakenHighLevel()

        return TradingManager(db_connector, db_lock, accounts, api)