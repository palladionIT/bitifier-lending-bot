import requests

class API:

    BaseURL = 'https://api.bitfinex.com/v1'

    def __init__(self):
        print('...setting up api')

        # TODO: get info from config and setup database

    def get_request(self, url_path):
        print('...performing GET request on API')
        return requests.get(self.BaseURL + url_path)

    def post_request(self, url_path, post_params = None, head = None):
        print('...performing POST request on API')
        return requests.post(self.BaseURL + url_path, data=post_params, headers=head)