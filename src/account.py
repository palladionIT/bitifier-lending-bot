from configparser import ConfigParser
import hmac
from hashlib import sha384

from .api import API as api
from .database import Database as db

class Account:

    UserID = None
    UserMail = None
    UserName = None
    APIKey = None
    APISecret = None
    BFXToken = None

    def __init__(self):
        print('...setting up account')

        # TODO: get info from config and setup database

        #parser = ConfigParser()
        #parser.read('config/proxy.ini')
        #self.ConfParser = parser
        #self.DBConnector = DatabaseConnector(parser.get('database_server', 'address'), \
        #                                     parser.get('database_server', 'port').split()[0])


    def check_login_state(self):
        print('...checking login state of account')
        # TODO: check if the session is stil valid
        # TODO: if not -> unset session information

    def log_in(self):
        print('...logging in user')
        # TODO: get user info from database/config and login and set session information

        # Login in JS: http://docs.bitfinex.com/v1/docs/rest-auth
        # hmac python: https://docs.python.org/2/library/hmac.html
        # hashlib python: https://docs.python.org/2/library/hashlib.html#module-hashlib

    def log_out(self):
        print('...logging out user')
        # TODO: logout and remove all session information

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