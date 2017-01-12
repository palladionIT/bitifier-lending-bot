from src.api import API

class BFXAPI(API):
    def __init__(self, key, secret):
        print('...setting up bitfinex api')
        super(BFXAPI, self).__init__(key, secret)

    # =======================
    # Miscellaneous functions
    # =======================

    def check_authentication(self):
        print('...checking login state of account')

        valid = True

        success, return_code = self.get_request(url_path='/symbols')[0:2]
        valid = valid and success

        success, return_code = self.get_acc_info()[0:2]

        return valid and success

    # =========================
    # Unauthenticated endpoints
    # =========================

    def get_ticker(self, symbol):
        # print('ticker')

        api_path = '/pubticker/' + symbol

        return self.get_request(url_path=self.generate_url(api_path))

    def get_statistics(self, symbol, period=None, volume=None):
        # print('stats')

        api_path = '/stats/' + symbol

        url_params = {}

        if period:
            url_params['period'] = period  # datetime object

        if volume:
            url_params['volume'] = volume  # integer object - default 50

        return self.get_request(url_path=self.generate_url(api_path, url_params))

    def get_fundingbook(self, currency, limit_bids = None, limit_asks = None):
        # print('fundingbook')

        api_path = '/lendbook/' + currency

        url_params = {}

        if limit_bids:
            url_params['limit_bids'] = limit_bids # datetime object

        if limit_asks:
            url_params['limit_asks'] = limit_asks # integer object - default 50

        return self.get_request(url_path=self.generate_url(api_path, url_params))

    def get_orderbook(self, symbol, limit_bids = None, limit_asks = None, group = None):
        # print('orderbook')

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

    def get_acc_info(self):
        # print('account info')

        api_path = '/account_infos'

        payload = {'request': '/' + self.APIVersion + api_path}

        return self.post_request(url_path=api_path,
                                 payload=payload)

    def get_summary(self):
        # print('30d summary')

        api_path = '/summary'

        payload = {'request': '/' + self.APIVersion + api_path}

        return self.post_request(url_path=api_path,
                                 payload=payload)

    def get_deposit_address(self):
        print('deposit')
        # Todo implement symbol detail

    def get_api_key_perm(self):
        print('get api key permissions')
        # Todo implement symbol detail

    def get_margin_info(self):
        print('margin info')
        # Todo implement symbol detail

    def get_wallet_balance(self):
        # print('wallet balance')

        api_path = '/balances'

        payload = {'request': '/' + self.APIVersion + api_path}

        return self.post_request(url_path=api_path,
                                 payload=payload)

    def get_wallet_transfer(self):
        print('wallet balance transfer')
        # Todo implement symbol detail

    def get_wallet_withdrawal(self):
        print('wallet withdrawal')
        # Todo implement symbol detail

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