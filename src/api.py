import requests
import hashlib
import hmac
import time
import json
import base64
import urllib.parse

class API:

    APIVersion = 'v1'
    BaseURL = 'https://api.bitfinex.com/' + APIVersion
    APIKey = None
    APISecret = None

    def __init__(self, key, secret):
        print('...setting up api')

        self.APIKey = key
        self.APISecret = secret

    def get_request(self, url_path):
        print('...performing GET request on API - ' + url_path)
        response = requests.get(self.BaseURL + url_path)
        try:
            return response.ok, response.status_code, self.byte_to_obj(response)
        except json.JSONDecodeError:
            print('API ERROR - Could not decode JSON, possibly wrong API path.')
            return False, 404, None

    def post_request(self, url_path, post_params = None):
        print('...performing POST request on API - ' + url_path)
        #response = requests.post(self.BaseURL + url_path, data=post_params, headers=self.generate_auth_headers(url_path))
        response = requests.post(self.BaseURL + url_path, data=urllib.parse.urlencode(post_params), headers=self.generate_auth_headers(url_path))

        try:
            return response.ok, response.status_code, self.byte_to_obj(response)
        except json.JSONDecodeError:
            print('API ERROR - Could not decode JSON, possibly wrong API path.')
            return False, 404, None

    def generate_auth_headers(self, path):
        payload = {'request': '/' + self.APIVersion + path, 'nonce': str(time.time())}
        body = base64.b64encode(json.dumps(payload).encode())

        signature = hmac.new(str.encode(self.APISecret), body, digestmod=hashlib.sha384).hexdigest()

        return {'X-BFX-APIKEY': self.APIKey,
                'X-BFX-PAYLOAD': body,
                'X-BFX-SIGNATURE': signature}

    def byte_to_obj(self, response):
        return json.loads(bytes.decode(response.content))