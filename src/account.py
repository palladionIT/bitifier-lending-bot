from configparser import ConfigParser
import hmac
import hashlib
import time
import json
import base64

from .api import API as api
from .databaseconnector import DatabaseConnector as db

class Account:

    UserID = None
    UserMail = None
    UserName = None
    APIKey = None
    APISecret = None
    BFXToken = None
    API = None

    def __init__(self, id, mail, name, key, secret, api):
        print('...setting up account')

        self.UserID = id
        self.UserMail = mail
        self.UserName = name
        self.APIKey = key
        self.APISecret = secret
        self.API = api

    def check_login_state(self):
        print('...checking login state of account')
        # TODO: check if the session is stil valid
        # TODO: if not -> unset session information

    def log_in(self):
        print('...logging in user')
        api_path = '/account_infos'

        payload = {'request': '/v1/account_infos', 'nonce': str(time.time())}
        body = base64.b64encode(json.dumps(payload).encode())

        signature = hmac.new(str.encode(self.APISecret), body, digestmod=hashlib.sha384).hexdigest()

        headers = {'X-BFX-APIKEY': self.APIKey,
                   'X-BFX-PAYLOAD': body,
                   'X-BFX-SIGNATURE': signature}

        response = self.API.post_request(url_path=api_path, head=headers)

        print(response) # 200 if ok
        #Todo: refactor code to represent actual API authentication

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