#from configparser import ConfigParser

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
                self.Accounts.append(Account(acc.id, acc.email, acc.name, acc.bfxapikey, acc.bfxapisec))

        child_pid = 0
        # child_pid = os.fork()

        if child_pid == 0:
            while 1:
                print('Running 10 minute task')
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
                account.offer_funding()

    def offer_funding(self, funds):
        pass

if __name__ == '__main__':
    Bitifier()