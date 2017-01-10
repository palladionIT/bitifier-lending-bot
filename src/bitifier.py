#from configparser import ConfigParser

#from proxy.gpgpu.OCLHandler import OCLHandler
#from .database.DatabaseConnector import DatabaseConnector
import re
from src.databaseconnector import DatabaseConnector
from src.account import Account

import getpass


class Bitifier:
    DBConnector = None
    Accounts = []

    def __init__(self):
        print('...setting up proxy')

        # Todo: replace fixed password with prompt - WARNING copy data from old DB
        #passphrase = getpass.getpass('Enter the database password: ')
        passphrase = 'testphun123'

        self.DBConnector = DatabaseConnector(passphrase)

        if self.first_run():
            username = getpass.getpass('Enter the bitfinex username: ')
            while True:
                mail = getpass.getpass('Enter the bitfinex email: ')
                if re.match('[^@]+@[^@]+\.[^@]+', mail):
                    break
                else:
                    print('Enter a valid email.')
            userpass = getpass.getpass('Enter the bitfinex password: ')
            while True:
                bfxkey = getpass.getpass('Enter the bitfinex api key: ')
                if len(bfxkey)==43:
                    break
                else:
                    print('Enter a valid bitfinex api key.')
            while True:
                bfxsec = getpass.getpass('Enter the bitfinex api secret: ')
                if len(bfxsec)==43:
                    break
                else:
                    print('Enter a valid bitfinex api secret:')

            try:
                self.DBConnector.User.get(self.DBConnector.User.name == username)
            except self.DBConnector.User.DoesNotExist:
                print(username)
                self.DBConnector.User.create(name=username,
                                             email=mail,
                                             password=userpass,
                                             bfxapikey=bfxkey,
                                             bfxapisec=bfxsec,
                                             status=True)
        else:
            for acc in self.DBConnector.User.select():
                self.Accounts.append(Account(acc.id, acc.name, acc.email, acc.bfxapikey, acc.bfxapisec))

        #for account in self.Accounts:
        #    account.check_api_connection()

        self.run_frequent_task()
        # Todo: focus on simple re-offering
        # Todo: do analysis later

    def first_run(self):
        print('...checking if first run')
        try:
            meta = self.DBConnector.BotMetaInfo.get(self.DBConnector.BotMetaInfo.id == 1)
            if meta.firstrun:
                return True
            else:
                return False
        except self.DBConnector.BotMetaInfo.DoesNotExist:
            self.DBConnector.BotMetaInfo.create(firstrun=False)
            return True

    def run_frequent_task(self):
        for account in self.Accounts:
            if account.check_api_connection():
                #account.get_active_offers()
                #account.get_taken_offers()
                #account.get_account_history('usd')
                # Todo: do tasks
                #account.api_test()

                funds = account.get_available_funds()

                if funds['usd'] < 50:
                    del funds['usd']
                if account.usd_from_btc(funds['btc']) < 50:
                    del funds['btc']

                account.offer_funding(funds)

    def offer_funding(self, funds):
        pass

if __name__ == '__main__':
    Bitifier()