import requests
import hashlib
import hmac
import time
import json
import base64
import abc

from .common_api import CommonApi


class BFXAPI(CommonApi):
    APIVersion = 'v1'
    BaseURL = 'https://api.bitfinex.com/' + APIVersion
    APIKey = None
    APISecret = None

    @staticmethod
    def byte_to_obj(response):
        return json.loads(bytes.decode(response.content))

    @staticmethod
    def create_url_parameters(parameters):
        keys = list(parameters.keys())
        keys.sort()

        return '&'.join(["%s=%s" % (k, parameters[k]) for k in keys])

    @staticmethod
    def generate_url(url, parameters=None):
        if parameters:
            url = "%s?%s" % (url, BFXAPI.create_url_parameters(parameters))

        return url

    @staticmethod
    def sign_payload(payload, account):
        j = json.dumps(payload)
        data = base64.standard_b64encode(j.encode('utf8'))

        h = hmac.new(account.APISecret.encode('utf8'), data, hashlib.sha384)
        signature = h.hexdigest()
        return {
            "X-BFX-APIKEY": account.APIKey,
            "X-BFX-PAYLOAD": data,
            "X-BFX-SIGNATURE": signature
        }

    @property
    def nonce(self):
        return str(time.time())

    def __init__(self):
        print('...setting up bitfinex api')

        # self.APIKey = key
        # self.APISecret = secret

    def get_request(self, url_path):
        print('...performing GET request on API - ' + url_path)
        try:
            response = requests.get(self.BaseURL + url_path)
            try:
                return response.ok, response.status_code, self.byte_to_obj(response)
            except json.JSONDecodeError:
                print('API ERROR - Could not decode JSON, possibly wrong API path.')
                return False, 404, None
        except ConnectionError as e:
            print('CONNECTION ERROR - a connection error occurred during get request')
            return False, 503, None

    def post_request(self, url_path, account, payload=None):
        print('...performing POST request on API - ' + url_path)
        payload['nonce'] = self.nonce

        try:
            response = requests.post(self.BaseURL + url_path, headers=self.sign_payload(payload, account))

            try:
                return response.ok, response.status_code, self.byte_to_obj(response)
            except json.JSONDecodeError:
                print('API ERROR - Could not decode JSON, possibly wrong API path.')
                return False, 404, None
        except ConnectionError as e:
            print('CONNECTION ERROR - a connection error occurred during post request')
            return False, 503, None

    # =======================
    # Miscellaneous functions
    # =======================

    def check_authentication(self, account):
        # print('...checking login state of account')

        valid = True

        success, return_code = self.get_request(url_path='/symbols')[0:2]
        valid = valid and success

        success, return_code = self.get_acc_info(account)[0:2]

        return valid and success

    # =========================
    # Unauthenticated endpoints
    # =========================

    def get_ticker(self, parameter):
        api_path = '/pubticker/' + parameter['symbol']

        return self.get_request(url_path=self.generate_url(api_path))

    def get_statistics(self, symbol, period=None, volume=None):
        api_path = '/stats/' + symbol

        url_params = {}

        # Todo: remove period && volume - they are return values

        if period:
            url_params['period'] = period  # datetime object

        if volume:
            url_params['volume'] = volume  # integer object - default 50

        return self.get_request(url_path=self.generate_url(api_path, url_params))

    def get_fundingbook(self, currency, limit_bids = None, limit_asks = None):
        api_path = '/lendbook/' + currency

        url_params = {}

        if limit_bids:
            url_params['limit_bids'] = limit_bids # datetime object

        if limit_asks:
            url_params['limit_asks'] = limit_asks # integer object - default 50

        return self.get_request(url_path=self.generate_url(api_path, url_params))

    def get_orderbook(self, symbol, limit_bids = None, limit_asks = None, group = None):
        api_path = '/book/' + symbol

        url_params = {}

        if limit_bids:
            url_params['limit_bids'] = limit_bids # integer object - default 50

        if limit_asks:
            url_params['limit_asks'] = limit_asks # integer object - default 50

        if group:
            url_params['group'] = group # integer 0 / 1 - groups orders by price

        return self.get_request(url_path=self.generate_url(api_path, url_params))

    def get_trades(self, symbol, timestamp=None, limit_trades=None):
        # print('trades')

        api_path = '/trades/' + symbol

        url_params = {}

        if timestamp:
            url_params['timestamp'] = timestamp  # datetime object

        if limit_trades:
            url_params['limit_trades'] = limit_trades  # integer object - default 50

        return self.get_request(url_path=self.generate_url(api_path, url_params))

    def get_lends(self, currency, timestamp = None, limit = None):
        # print('lends')

        api_path = '/lends/' + currency

        url_params = {}

        if timestamp:
            url_params['timestamp'] = timestamp # datetime object

        if limit:
            url_params['limit_lends'] = limit # integer object - default 50

        return self.get_request(url_path=self.generate_url(api_path, url_params))

    def get_symbols(self):
        # print('symbols')

        api_path = '/symbols/'

        return self.get_request(url_path=self.generate_url(api_path))

    def get_symbols_details(self):
        # print('symbols details')

        api_path = '/symbols_details/'

        return self.get_request(url_path=self.generate_url(api_path))

    # =======================
    # Authenticated Endpoints
    # =======================

    def get_acc_info(self, account):
        # print('account info')

        api_path = '/account_infos'

        payload = {'request': '/' + self.APIVersion + api_path}

        return self.post_request(url_path=api_path,
                                 payload=payload,
                                 account=account)

    def get_summary(self):
        # print('30d summary')

        api_path = '/summary'

        payload = {'request': '/' + self.APIVersion + api_path}

        return self.post_request(url_path=api_path,
                                 payload=payload)

    '''
    'Mastercoin' currency only works for verified accounts.
    '''
    def get_deposit_address(self, method, wallet, renew = 0):
        # print('deposit')

        api_path = '/deposit/new'

        payload = {'request': '/' + self.APIVersion + api_path,
                   'method': method,
                   'wallet_name': wallet,
                   'renew': renew}

        return self.post_request(url_path=api_path,
                                 payload=payload)

    def get_api_key_perm(self):
        print('get api key permissions')

        api_path = '/key_info'

        payload = {'request': '/' + self.APIVersion + api_path}

        return self.post_request(url_path=api_path,
                                 payload=payload)

    def get_margin_info(self):
        print('margin info')

        api_path = '/margin_infos'

        payload = {'request': '/' + self.APIVersion + api_path}

        return self.post_request(url_path=api_path,
                                 payload=payload)

    def get_wallet_balance(self):
        api_path = '/balances'

        payload = {'request': '/' + self.APIVersion + api_path}

        return self.post_request(url_path=api_path,
                                 payload=payload)

    def perform_wallet_transfer(self, amount, currency, walletfrom, walletto):
        api_path = '/transfer'

        payload = {'request': '/' + self.APIVersion + api_path,
                   'amount': amount,
                   'currency': currency,
                   'walletfrom': walletfrom,
                   'walletto': walletto}

        return self.post_request(url_path=api_path,
                                 payload=payload)

    def perform_wallet_withdrawal(self,
                                  type,
                                  wallet,
                                  amount,
                                  address,
                                  account_number,
                                  bank_name,
                                  bank_address,
                                  bank_city,
                                  bank_country,
                                  express = None,
                                  account_name = None,
                                  detail_payment = None,
                                  intermed_bank_name = None,
                                  intermed_bank_address = None,
                                  intermed_bank_city = None,
                                  intermed_bank_country = None,
                                  intermed_bank_account = None,
                                  intermed_bank_swift = None,
                                  paymend_id = None):
        #print('wallet withdrawal')

        api_path = '/withdraw'

        payload = {'request': '/' + self.APIVersion + api_path,
                   'withdrawal_type': type,
                   'walletselected': wallet,
                   'amount': amount,
                   'address': address,
                   'account_number': account_number,
                   'bank_name': bank_name,
                   'bank_address': bank_address,
                   'bank_city': bank_city,
                   'bank_country': bank_country}

        if express:
            payload['expressWire'] = express
        if account_name:
            payload['account_name'] = account_name
        if detail_payment:
            payload['detail_payment'] = detail_payment
        if intermed_bank_name:
            payload['intermediary_bank_name'] = intermed_bank_name
        if intermed_bank_address:
            payload['intermediary_bank_address'] = intermed_bank_address
        if intermed_bank_city:
            payload['intermediary_bank_city'] = intermed_bank_city
        if intermed_bank_country:
            payload['intermediary_bank_country'] = intermed_bank_country
        if intermed_bank_account:
            payload['intermediary_bank_account'] = intermed_bank_account
        if intermed_bank_swift:
            payload['intermediary_bank_swift'] = intermed_bank_swift
        if paymend_id:
            payload['payment_id'] = paymend_id

        return self.post_request(url_path=api_path,
                                 payload=payload)

    # ======================
    # Authenticated - Orders
    # ======================

    # Todo: rename - order_new, order_new_multi, order_cancel...

    def perform_new_order(self):
        print('new order')
        # Todo implement symbol detail

    def perform_new_multiorder(self):
        print('new multi order')
        # Todo implement symbol detail

    def perform_cancel_order(self):
        print('cancel order')
        # Todo implement symbol detail

    def perform_cancel_multiorder(self):
        print('cancel multi order')
        # Todo implement symbol detail

    def perform_cancel_all_order(self):
        print('cancel all order')
        # Todo implement symbol detail

    def order_replace(self):
        print('replace order')
        # Todo implement symbol detail

    def order_status(self):
        print('replace order')
        # Todo implement symbol detail

    def order_active_list(self):
        print('replace order')
        # Todo implement symbol detail

    # =========================
    # Authenticated - Positions
    # =========================

    def position_active(self):
        print('active position')
        # Todo implement symbol detail

    def position_claim(self):
        print('claim position')
        # Todo implement symbol detail

    def position_active(self):
        print('active position')
        # Todo implement symbol detail

    # ==========================
    # Authenticated - Historical
    # ==========================

    def history_balance(self, currency, start = None, end = None, limit = None, wallet = None):
        # print('balance history')

        api_path = '/history'

        payload = {'request': '/' + self.APIVersion + api_path,
                   'currency': currency}

        if start:
            payload['since'] = start # datetime object
        if end:
            payload['until'] = end # datetime object
        if limit:
            payload['limit'] = limit # integer
        if start:
            payload['wallet'] = wallet # string 'trading' || 'exchange' || 'deposit'

        return self.post_request(url_path=api_path,
                                 payload=payload)

    def history_deposit_withdraw(self, currency, start = None, end = None, limit = None, wallet = None):
        # print('deposit withdrawal history')

        api_path = '/history/movements'

        payload = {'request': '/' + self.APIVersion + api_path,
                   'currency': currency}

        if start:
            payload['since'] = start # datetime object
        if end:
            payload['until'] = end # datetime object
        if limit:
            payload['limit'] = limit # integer
        if start:
            payload['wallet'] = wallet # string 'trading' || 'exchange' || 'deposit'

        return self.post_request(url_path=api_path,
                                 payload=payload)

    def history_past_trades(self, symbol, timestamp, end = None, limit = None, reverse = None):
        # print('past trades history')

        api_path = '/mytrades'

        payload = {'request': '/' + self.APIVersion + api_path,
                   'symbol': symbol,
                   'timestamp': timestamp}

        if end:
            payload['until'] = end # datetime object
        if limit:
            payload['limit_trades'] = limit # integer
        if reverse:
            payload['reverse'] = reverse # string 'trading' || 'exchange' || 'deposit'

        return self.post_request(url_path=api_path,
                                 payload=payload)

    # ==============================
    # Authenticated - Margin Funding
    # ==============================

    def funding_new_offer(self, currency, amount, rate, period, direction):
        # print('new offer funding')

        api_path = '/offer/new'

        payload = {'request': '/' + self.APIVersion + api_path,
                   'currency': currency,
                   'amount': amount,
                   'rate': rate,
                   'period': period,
                   'direction': direction}

        return self.post_request(url_path=api_path,
                                 payload=payload)

    def funding_cancel_offer(self, id):
        # print('cancel offer funding')

        api_path = '/offer/cancel'

        payload = {'request': '/' + self.APIVersion + api_path,
                   'offer_id': id}

        return self.post_request(url_path=api_path,
                                 payload=payload)

    def funding_offer_status(self, id):
        # print('status offer funding')

        api_path = '/offer/status'

        payload = {'request': '/' + self.APIVersion + api_path,
                   'offer_id': id}

        return self.post_request(url_path=api_path,
                                 payload=payload)

    def funding_active_credit(self):
        # print('active_credit funding')

        api_path = '/credits'

        payload = {'request': '/' + self.APIVersion + api_path}

        return self.post_request(url_path=api_path,
                                 payload=payload)

    def funding_active_offer(self):
        # print('active offer funding')

        api_path = '/offers'

        payload = {'request': '/' + self.APIVersion + api_path}

        return self.post_request(url_path=api_path,
                                 payload=payload)

    def funding_active_funding_used(self):
        # print('active offer used funding')

        api_path = '/taken_funds'

        payload = {'request': '/' + self.APIVersion + api_path}

        return self.post_request(url_path=api_path,
                                 payload=payload)

    def funding_active_funding_unused(self):
        # print('active offer unused funding')

        api_path = '/unused_taken_funds'

        payload = {'request': '/' + self.APIVersion + api_path}

        return self.post_request(url_path=api_path,
                                 payload=payload)

    def funding_taken(self):
        # print('taken funding')

        api_path = '/total_taken_funds'

        payload = {'request': '/' + self.APIVersion + api_path}

        return self.post_request(url_path=api_path,
                                 payload=payload)

    def funding_close(self, id):
        # print('close funding')

        api_path = '/funding/close'

        payload = {'request': '/' + self.APIVersion + api_path,
                   'swap_id': id}

        return self.post_request(url_path=api_path,
                                 payload=payload)