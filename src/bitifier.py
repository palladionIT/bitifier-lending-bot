#from configparser import ConfigParser

#from proxy.gpgpu.OCLHandler import OCLHandler
#from .database.DatabaseConnector import DatabaseConnector
from src.databaseconnector import DatabaseConnector

import getpass


class Bitifier:
    DBConnector = None
    ComputeHandler = None
    ConfParser = None

    def __init__(self):
        print('...setting up proxy')

        passphrase = getpass.getpass('Enter the database password: ')

        self.DBConnector = DatabaseConnector(passphrase)

        #parser = ConfigParser()
        #parser.read('config/proxy.ini')
        #self.ConfParser = parser
        #self.DBConnector = DatabaseConnector(parser.get('database_server', 'address'), \
        #                                     parser.get('database_server', 'port').split()[0])
        '''TODO: send full config data to DBConnector and create config object with both DB -> easy switch'''
        #self.ComputeHandler = OCLHandler()

    def setup_components(self):
        '''TODO: self.DBConnector.connect(self.ConfParser.get('database_server', 'databases').split()[0],
        self.ConfParser.get(
            'database_server', 'user').split()[0], self.ConfParser.get('database_server', 'password'))'''
        #self.DBConnector.connect(self.ConfParser.get('database_server', 'database').split()[0],
        #                         self.ConfParser.get('database_server', 'user').split()[0],
        #                         self.ConfParser.get('database_server', 'password').split()[0])
        print('setup')
        pass