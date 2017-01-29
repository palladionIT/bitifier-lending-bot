from configparser import ConfigParser

#from proxy.gpgpu.OCLHandler import OCLHandler
#from .database.DatabaseConnector import DatabaseConnector
import getpass
import re
import time
import os

from src.account import Account
from src.databaseconnector import DatabaseConnector


# Todo: add database storage for analysis
# Todo: add web interface for easy overview

class Bitifier:
    DBConnector = None
    Accounts = []

    run_counter = 0

    def __init__(self):
        print('...setting up bitifier bot')

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
                self.DBConnector.User.create(name=username,
                                             email=mail,
                                             password=userpass,
                                             bfxapikey=bfxkey,
                                             bfxapisec=bfxsec,
                                             status=True)
        else:
            for acc in self.DBConnector.User.select():
                self.Accounts.append(Account(acc.id, acc.email, acc.name, acc.bfxapikey, acc.bfxapisec, self.load_config(acc.id)))

        child_pid = 0
        # child_pid = os.fork()

        if child_pid == 0:
            while 1:
                print('Running 10 minute task')
                self.run_counter += 1

                if self.run_counter >= 6:
                    for account in self.Accounts:
                        account.update_config(self.load_config(account.UserID))
                        self.run_counter = 0
                self.run_frequent_task()
                print('Finished Running 10 minute task')
                time.sleep(600)
        else:
            print('Child PID: ' + str(child_pid))
            pass

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
                print('......successful login for - ' + account.UserName)
                account.api_test()
                account.offer_funding()

    def offer_funding(self, funds):
        pass

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

if __name__ == '__main__':
    Bitifier()