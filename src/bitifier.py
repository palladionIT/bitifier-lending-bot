#from configparser import ConfigParser

#from proxy.gpgpu.OCLHandler import OCLHandler
#from .database.DatabaseConnector import DatabaseConnector
import re
from src.databaseconnector import DatabaseConnector

import getpass


class Bitifier:
    DBConnector = None
    ComputeHandler = None
    ConfParser = None

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

        # Todo: write API connection functionality

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

if __name__ == '__main__':
    Bitifier()