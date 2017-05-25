import threading
import time
import datetime
import decimal
import logging
import numpy as np

from configparser import ConfigParser
from src.account import Account
from krakenex import API

# debug imports
import matplotlib.pyplot as plt


class TradingManager(threading.Thread):
    DBConnector = None
    DBLock = None
    API = None
    Accounts = []
    Logger = None
    run_interval = 60
    rsi_limit = 15

    RunCounter = 0

    ## TODO REMOVE DEBUG
    chart_stuff = True
    chart_stuff_switch = False
    chart_enforced = False
    order_oszillator = 1
    order_price = 1642.5515
    order_min_price = 1651.126939

    def __init__(self, db_connector, db_lock, accounts, api, logger):
        # Todo: pass necessary arguments || create objects here
        self.DBConnector = db_connector
        self.DBLock = db_lock
        self.Accounts = accounts
        self.API = api
        self.Logger = logger

    def run(self):
        # Todo: implement exception handling that restarts everything after upon next run
        while True:
            print('Running ' + str(self.run_interval / 60) + ' minute task')
            self.RunCounter += 1

            if False and self.RunCounter >= 6:
                for account in self.Accounts:
                    account.update_config(self.load_config(account.UserID))
                    self.RunCounter = 0
            self.run_frequent_task()
            print('Finished Running  ' + str(self.run_interval / 60) + '  minute task')
            time.sleep(self.run_interval)

    def run_frequent_task(self):
        try:
            last_trade = self.get_last_action()
            # account_state = self.get_account_state()
            market_state = self.check_market_data(3)
            self.rsi_limit = self.calculate_adaptive_rsi_lim(market_state[3])
            print('RSI LIMIT: ' + str(self.rsi_limit))
            # market_state = self.check_market_data()
            action = self.check_conditions(market_state[0], market_state[1], market_state[2], market_state[3], market_state[4], last_trade)
            if action['type'] == 'buy' and action['check']:
                self.create_buy_order(action)
            if action['type'] == 'sell' and action['check']:
                self.create_sell_order(action, last_trade)
        except Exception as e:
            print('ERROR - while performing trading')
            print(e)

    def create_buy_order(self, order):

        trading_pair = 'XXBTZEUR'
        order_book = self.API.query_public('Depth', {'pair': trading_pair,
                                                     'count': 20})

        if len(order_book['error']) > 0:
            return

        buy_orders = order_book['result'][trading_pair]['bids']
        sell_orders = order_book['result'][trading_pair]['asks']

        funds = float(self.API.query_private('Balance')['result']['ZEUR'])

        expire_time = 60  # in seconds

        immediate_order = True

        # TODO REMOVE AFTER DEBUG
        lowest_sell = float(sell_orders[0][0])
        # sell_diff = float(sell_orders[1][0]) - float(sell_orders[0][0])
        highest_buy = float(buy_orders[0][0])
        price = (highest_buy + lowest_sell) / 2

        if immediate_order:
            # funds -> in BTC
            order_info = self.API.query_private('AddOrder', {'pair': trading_pair,
                                                             'type': 'buy',
                                                             'ordertype': 'market',
                                                             'volume': funds,
                                                             'expiretm': '+'+str(expire_time),
                                                             'oflags': 'viqc'})
            tx = order_info['result']
            tx_id = order_info['result']['txid'][0]
            tx_info = self.API.query_private('QueryOrders', {'txid': tx_id})

            price = tx_info['result'][tx_id]['price']
            usd_vol = tx_info['result'][tx_id]['cost']
            btc_vol = tx_info['result'][tx_id]['vol']
            fee = tx_info['result'][tx_id]['fee']
            # debug id: 'OKPYKZ-EV6YD-WWMT4I'
            # Todo: get and set price
        else:
            lowest_sell = float(sell_orders[0][0])
            # sell_diff = float(sell_orders[1][0]) - float(sell_orders[0][0])
            highest_buy = float(buy_orders[0][0])
            price = (highest_buy + lowest_sell) / 2

            order_info = self.API.query_private('AddOrder', {'pair': trading_pair,
                                                             'type': 'buy',
                                                             'ordertype': 'limit',
                                                             'price': price,
                                                             'volume': funds,
                                                             'expiretm': '+'+str(expire_time),
                                                             'validate': 'true'})

        # Todo: get order info from account (using order_info)
        # Todo: write to database
        min_sell = self.calculate_min_sell_margin(decimal.Decimal(price), decimal.Decimal(funds))
        # order_info['result']['txid'] -> get txid -> get tx info from account
        print('BUY ORDER DONE! - WRITING DB STUFF')
        self.DBConnector.ExchangeTrades.create(exchange='kraken',
                                               src_currency='USD',
                                               trg_currency='BTC',
                                               amount_src=usd_vol,
                                               amount_real=btc_vol,
                                               rate=price,
                                               fee=fee,
                                               extrema_time=0,
                                               min_sell_margin=min_sell,
                                               date=datetime.datetime.now())
        '''self.order_oszillator = 1
        self.order_price = price
        self.order_min_price = self.calculate_min_sell_margin(price, 50, 0.0026)
        self.write_to_order_to_file(price, funds, 'b')
        self.chart_stuff_switch = True'''

    def create_sell_order(self, order, last_trade):
        # Todo: check *current* market price - DONE
        # Todo: if satisfies -> sell -
        # Todo: else loop (with 10 sec wait) and get current book -> create sell order
        # Todo: write info to DB
        trading_pair = 'XXBTZEUR'
        order_time = time.time() + 60
        status = 'open'

        while status != 'closed' and order_time > time.time():
            order_book = self.API.query_public('Depth', {'pair': trading_pair,
                                                         'count': 20})

            if len(order_book['error']) > 0:
                return

            buy_orders = order_book['result'][trading_pair]['bids']
            sell_orders = order_book['result'][trading_pair]['asks']

            lowest_sell = float(sell_orders[0][0])
            # sell_diff = float(sell_orders[1][0]) - float(sell_orders[0][0])
            highest_buy = float(buy_orders[0][0])
            price = (highest_buy + lowest_sell) / 2

            # if highest_buy > order['min_price'] and highest_buy > self.calculate_min_sell_margin():

            # Todo get account balance
            funds = float(self.API.query_private('Balance')['result']['XXBT'])
            # funds = 50

            if price > self.calculate_min_sell_margin(last_trade.rate, last_trade.amount_src, self.get_current_fee(trading_pair)):
                expire_time = 10  # in seconds
                order_info = self.API.query_private('AddOrder', {'pair': trading_pair,
                                                                 'type': 'sell',
                                                                 'ordertype': 'limit',
                                                                 'price': price,
                                                                 'volume': funds,
                                                                 'expiretm': '+'+str(expire_time)})


                time.sleep(expire_time)

                tx = order_info['result']
                tx_id = order_info['result']['txid'][0]
                tx_info = self.API.query_private('QueryOrders', {'txid': tx_id})

                status = tx_info['result'][tx_id]['status']
                '''self.order_oszillator = 0
                self.order_price = 0
                self.order_min_price = 0
                self.chart_stuff_switch = True'''
            else:
                return

        if status == 'closed':

            # OBKGWN-SEUT2-2IBMOC
            #tx_id = 'OBKGWN-SEUT2-2IBMOC'
            #tx_info = self.API.query_private('QueryOrders', {'txid': tx_id})
            price = tx_info['result'][tx_id]['price']
            usd_vol = tx_info['result'][tx_id]['cost']
            btc_vol = tx_info['result'][tx_id]['vol']
            fee = tx_info['result'][tx_id]['fee']

            self.write_to_order_to_file(price, funds, 's')
            print('SELL ORDER DONE! - WRITING DB STUFF')
            self.DBConnector.ExchangeTrades.create(exchange='kraken',
                                                   src_currency='BTC',
                                                   trg_currency='USD',
                                                   amount_src=funds,
                                                   amount_real=usd_vol,
                                                   rate=price,
                                                   fee=fee,
                                                   extrema_time=0,
                                                   min_sell_margin=0,
                                                   date=datetime.datetime.now())

    def send_order(self, pair, type, order_type, funds, expire_time):
        pass

    def get_last_action(self):
        try:
            trade = self.DBConnector.ExchangeTrades.select().order_by(self.DBConnector.ExchangeTrades.id.desc()).get()
        except self.DBConnector.ExchangeTrades.DoesNotExist:
            print('ERROR - TRADING MANAGER - could not retrieve last trade.')
            trade = None
        # User.select().order_by(User.id.desc()).get()
        # return self.DBConnector.ExchangeTrades()
        return trade

    def get_account_state(self):

        try:
            account_balance = self.API.query_private('Balance')

            if len(account_balance['error']) > 0:
                print('ERROR - Trade Manager: could not retrieve account balance')
                return None

            # Todo: for all balances -> create valid trading pairs
            # Todo: query fees for these pairs

            trading_pair = 'XXBTZEUR'
            fee_flag = 'fees'  # in minutes

            fee_schedule = self.API.query_private('TradeVolume', {'fee-info': fee_flag,
                                                                  'pair': trading_pair})  # Todo: catch socket.timout exception

            if len(fee_schedule['error']) > 0:
                print('ERROR - Trade Manager: could not retrieve fee schedule')
                return None

            # Todo: create return object
            return {'balance': account_balance,
                    'account_fees': fee_schedule}
        except ConnectionError:
            print('ERROR - Trade Manager: ConnectionError in get_account_state()')
            return None

    def check_market_data(self, diff=None):
        market_dat = None

        trading_pair = 'XXBTZEUR'
        interval_size = '1'  # in minutes
        err_cnt = 0

        while err_cnt < 3:
            try:
                market_state = self.API.query_public('OHLC', {'pair': trading_pair,
                                                              'interval': interval_size}) # Todo: fix JSONDecodeError
                if len(market_state['error']) == 0:
                    market_data = market_state['result'][trading_pair]

                    # Data extraction of compound list
                    current_period = market_data[-1]
                    clean_data = market_data[:-1]
                    clean_data = self.interpolate_nan(clean_data, 5)
                    interval_times = [sublist[0] for sublist in clean_data]
                    vw_average = [float(sublist[5]) for sublist in clean_data]  # volume weighted data

                    # print('Period Start: ' + time.ctime(interval_times[0]))
                    # print('Period End: ' + time.ctime(interval_times[-1]))

                    smooth_vw_average = self.smooth_data([int(i) for i in interval_times], [float(i) for i in vw_average],
                                                         15,
                                                         'moving_average')
                    derivative = self.centered_derivative(smooth_vw_average, interval_times)
                    # dderivative = self.centered_derivative(derivative, times)
                    # zeros = self.find_zeros(derivative)
                    filtered_z = self.find_extrema(interval_times, smooth_vw_average, diff)
                    # current_val = clean_data[-1]

                    # market_dat = [current_period, interval_times, smooth_vw_average, zeros]
                    market_dat = [current_period, interval_times, smooth_vw_average, vw_average, filtered_z]

                    # self.display_graph(interval_times, smooth_vw_average, filtered_z)
                    ### self.display_graph(interval_times, smooth_vw_average, zeros)
                    if self.chart_enforced and (self.chart_stuff and self.chart_stuff_switch):
                        self.display_graph(interval_times, smooth_vw_average, filtered_z)
                        # Todo: handle this data - compute minima/maxima - DONE
                        # Todo: fit curve to market data - DONE
                        # Todo: calculate maxima/minima - DONE
                        # Todo: calculate trend - DONE
                        # Todo: return something (buy? sell?) - DONE
                        # methods:
                        # https://stackoverflow.com/questions/7061071/finding-the-min-max-of-a-stock-chart
                        # https://en.wikipedia.org/wiki/Moving_average#Other_weightings
                        # en.wikipedia.org/wiki/Local_regression
                        # https://en.wikipedia.org/wiki/Kernel_smoother
                        # https://en.wikipedia.org/wiki/Moving_least_squares
                        #
                        ###############
                        # Further applied reading:
                        # http://connor-johnson.com/2014/11/23/time-series-forecasting-in-python-and-r/
                        # https://www.quantstart.com/articles/Forecasting-Financial-Time-Series-Part-1
                        # http://fluid-turb.wikidot.com/time-series-analysis
                        # https://www.quantstart.com/articles/Beginners-Guide-to-Time-Series-Analysis
                        # chrome-extension://lnagobkdlgiobpknboclgafebmkoocce/scripts/externalLibraries/pdf/web/viewer.html?file=http%3A%2F%2Fwww.petertessin.com%2FTimeSeries.pdf
                        # chrome-extension://lnagobkdlgiobpknboclgafebmkoocce/scripts/externalLibraries/pdf/web/viewer.html?file=http%3A%2F%2Fconference.scipy.org%2Fscipy2011%2Fslides%2Fmckinney_time_series.pdf
                        # https://nbviewer.jupyter.org/github/changhiskhan/talks/blob/master/pydata2012/pandas_timeseries.ipynb
                        # https://nbviewer.jupyter.org/github/jvns/talks/blob/master/pyconca2013/pistes-cyclables.ipynb
                        # https://nbviewer.jupyter.org/github/lge88/UCSD_BigData/blob/master/notebooks/weather/Weather%20Analysis.ipynb
                        #
                        ###############
                        # Indicators (trend)
                        # RSI relative strength index

                err_cnt = 3
            except Exception as e:
                print('ERROR - could not check market data')
                print(e)
                err_cnt += 1

        '''try:
            market_state = self.API.query_public('OHLC', {'pair': trading_pair,
                                                          'interval': interval_size}) # Todo: fix JSONDecodeError
            if len(market_state['error']) == 0:
                market_data = market_state['result'][trading_pair]

                # Data extraction of compound list
                current_period = market_data[-1]
                clean_data = market_data[:-1]
                clean_data = self.interpolate_nan(clean_data, 5)
                interval_times = [sublist[0] for sublist in clean_data]
                vw_average = [float(sublist[5]) for sublist in clean_data]  # volume weighted data

                print('Period Start: ' + time.ctime(interval_times[0]))
                print('Period End: ' + time.ctime(interval_times[-1]))

                smooth_vw_average = self.smooth_data([int(i) for i in interval_times], [float(i) for i in vw_average],
                                                     15,
                                                     'moving_average')
                derivative = self.centered_derivative(smooth_vw_average, interval_times)
                # dderivative = self.centered_derivative(derivative, times)
                # zeros = self.find_zeros(derivative)
                filtered_z = self.find_extrema(interval_times, smooth_vw_average, diff)
                # current_val = clean_data[-1]

                # market_dat = [current_period, interval_times, smooth_vw_average, zeros]
                market_dat = [current_period, interval_times, smooth_vw_average, vw_average, filtered_z]

                # self.display_graph(interval_times, smooth_vw_average, filtered_z)
                ### self.display_graph(interval_times, smooth_vw_average, zeros)
                if self.chart_enforced and (self.chart_stuff and self.chart_stuff_switch):
                    self.display_graph(interval_times, smooth_vw_average, filtered_z)
                    # Todo: handle this data - compute minima/maxima - DONE
                    # Todo: fit curve to market data - DONE
                    # Todo: calculate maxima/minima - DONE
                    # Todo: calculate trend - DONE
                    # Todo: return something (buy? sell?) - DONE
                    # methods:
                    # https://stackoverflow.com/questions/7061071/finding-the-min-max-of-a-stock-chart
                    # https://en.wikipedia.org/wiki/Moving_average#Other_weightings
                    # en.wikipedia.org/wiki/Local_regression
                    # https://en.wikipedia.org/wiki/Kernel_smoother
                    # https://en.wikipedia.org/wiki/Moving_least_squares
                    #
                    ###############
                    # Further applied reading:
                    # http://connor-johnson.com/2014/11/23/time-series-forecasting-in-python-and-r/
                    # https://www.quantstart.com/articles/Forecasting-Financial-Time-Series-Part-1
                    # http://fluid-turb.wikidot.com/time-series-analysis
                    # https://www.quantstart.com/articles/Beginners-Guide-to-Time-Series-Analysis
                    # chrome-extension://lnagobkdlgiobpknboclgafebmkoocce/scripts/externalLibraries/pdf/web/viewer.html?file=http%3A%2F%2Fwww.petertessin.com%2FTimeSeries.pdf
                    # chrome-extension://lnagobkdlgiobpknboclgafebmkoocce/scripts/externalLibraries/pdf/web/viewer.html?file=http%3A%2F%2Fconference.scipy.org%2Fscipy2011%2Fslides%2Fmckinney_time_series.pdf
                    # https://nbviewer.jupyter.org/github/changhiskhan/talks/blob/master/pydata2012/pandas_timeseries.ipynb
                    # https://nbviewer.jupyter.org/github/jvns/talks/blob/master/pyconca2013/pistes-cyclables.ipynb
                    # https://nbviewer.jupyter.org/github/lge88/UCSD_BigData/blob/master/notebooks/weather/Weather%20Analysis.ipynb
                    #
                    ###############
                    # Indicators (trend)
                    # RSI relative strength index
        except Exception as e:
            print('ERROR - could not check market data')
            print(e)


        return market_dat

    def check_conditions(self, current_interval, interval_times, market_data, real_market_data, extrema, last_trade):
        window_size = 10
        current_time = time.time()
        window_start_index = max([i for i, t in enumerate(interval_times) if t <= current_time - window_size * 60])
        window_end_index = len(market_data) - 3

        # extrema = self.extrema_in_interval(extrema, window_start_index, len(interval_times) - 1)
        matching_extrema = [d for d in reversed(extrema) if d[0] >= window_start_index and d[0] < window_end_index]

        print('LAST EXTREMA INDEX: ' + str(extrema[-1][0]) + ' | WINDOW START INDEX: ' + str(window_start_index) + ' | WINDOW END INDEX: ' + str(window_end_index))
        self.write_extrema_to_file(extrema[-1], window_start_index)

        margin = self.calculate_min_sell_margin(1684, 50, 0.0026)

        ### TODO: remove *debug* code
        #if len(matching_extrema) < 1:
        #    matching_extrema = [extrema[-1]]
        #rsi = self.relative_strength_index(market_data, 0.8)
        #self.display_graph(interval_times, rsi, extrema=extrema, yhlines=[15, 50, 70])

        # Todo: filter minor extrema
        # Todo: if there is a matching extrema -> check if current price is even higher
        # Todo: check for min && max
        # Todo: check if current price is higher/lower && if it is within a very small
        # Todo: IMPORTANT DO THIS CHECK WITH REAL MARKET DATA OR VERY MINOR SMOOTHED DATA (10 min smooth)

        if len(matching_extrema) > 0:

            '''for i in [0.8, 1, 1.2]:
                rsii = self.relative_strength_index(market_data, i)

                self.display_graph(interval_times, rsii, extrema=extrema, yhlines=[20, 50, 80])
            '''
            print('EXTREMA found')

            recent_extrema = matching_extrema[-1]

            rsi = self.relative_strength_index(market_data, 0.8)

            if self.chart_enforced and (self.chart_stuff and self.chart_stuff_switch):
                self.display_graph(interval_times, rsi, extrema=extrema, yhlines=[15, 50, 70])
                self.chart_stuff = False

            #order = self.check_sell_order(recent_extrema, rsi, self.DBConnector.ExchangeTrades())
            # return order
            '''if self.order_oszillator > 0:
                return self.check_sell_order(recent_extrema, rsi, self.DBConnector.ExchangeTrades())
            '''
            if not last_trade:
                order = self.check_buy_order(recent_extrema, rsi)
            else:
                if last_trade.src_currency == 'USD':
                    order = self.check_sell_order(recent_extrema, rsi, last_trade)

                elif last_trade.src_currency == 'BTC':
                    order = self.check_buy_order(recent_extrema, rsi, last_trade)
                else:
                    order = {'type': 'none',
                             'check': False}

            '''trading_pair = 'XXBTZEUR'
            fee_flag = 'fees' # in minutes

            fee_schedule = self.API.query_private('TradeVolume', {'fee-info': fee_flag,
                                                                'pair': trading_pair})

            if len(fee_schedule['error']) > 0:
                print('ERROR - Trade Manager: could not retrieve fee schedule')
                return None

            account_balance = self.API.query_private('Balance')

            if len(account_balance['error']) > 0:
                print('ERROR - Trade Manager: could not retrieve account balance')
                return None'''
        else:
            order = {'type': 'none',
                     'check': False}
        return order

    def check_buy_order(self, extremum, rsi, last_order=None):
        print('BUY ORDER PARAMETERS - extremum: ' + str(extremum[3]) + ' | rsi: ' + str(rsi[-1]))
        if extremum[3] > 0:
            if rsi[-1] < self.rsi_limit:
                #if
                return {'type': 'buy',
                        'check': True}

        return {'type': 'buy',
                'check': False}

    def check_sell_order(self, extremum, rsi, last_order):

        '''last_order.amount_src = 50
        last_order.rate = self.order_price
        last_order.min_sell_margin = 1650.84'''
        print('SELL ORDER PARAMETERS - extremum: ' + str(extremum[3]) + ' | rsi: ' + str(rsi[-1]) + ' | value: ' + str(extremum[-1]))

        if extremum[3] < 0:
            if rsi[-1] > 80:
                trading_pair = 'XXBTZEUR'
                fee_flag = 'fees'
                # account_balance = self.API.query_private('Balance')

                current_fee = self.get_current_fee(trading_pair)

                sell_price = self.calculate_min_sell_margin(last_order.rate, last_order.amount_src, current_fee)

                if extremum[4] > sell_price and extremum[4] > last_order.min_sell_margin:
                    return {'type': 'sell',
                            'check': True,
                            'min_price': sell_price}
                #account_balance['result']['XXBT']
        return {'type': 'sell',
                'check': False,
                'min_price': 0}

    def get_current_fee(self, trading_pair):
        fee_schedule = self.API.query_private('TradeVolume', {'fee-info': 'fees',
                                                              'pair': trading_pair})
        return decimal.Decimal(float(fee_schedule['result']['fees'][trading_pair]['fee']) / 100)

    def interpolate_nan(self, data, row):
        for i, d in enumerate(data):
            if float(d[row]) == 0:
                # Check for borders
                if i != 0 and i < len(data):
                    p = data[i - 1]
                    n = data[i + 1] # TODO: catch this IndexError -> observe why
                if i == 0:
                    p = data[i + 1]
                    n = data[i + 1]
                if i == len(data) - 1:
                    p = data[i - 1]
                    n = data[i - 1]

                # Check for 0 values
                if float(p[row]) == 0 or float(n[row]) == 0:
                    # Interpolate <open, close> and se
                    if i != 0 and i < len(data):
                        p[row] = str((float(data[i - 1][1]) + float(data[i - 1][4])) / 2)
                        n[row] = str((float(data[i + 1][1]) + float(data[i + 1][4])) / 2)
                    if i == 0:
                        p[row] = str((float(data[i + 1][1]) + float(data[i + 1][4])) / 2)
                        n[row] = str((float(data[i + 1][1]) + float(data[i + 1][4])) / 2)
                    if i == len(data) - 1:
                        p[row] = str((float(data[i - 1][1]) + float(data[i - 1][4])) / 2)
                        n[row] = str((float(data[i - 1][1]) + float(data[i - 1][4])) / 2)
                data[i][row] = str((float(p[row]) + float(n[row])) / 2)

        return data

    def smooth_data(self, x_dat, y_dat, interval, type):
        smoothed_data = None
        interval_s = int(interval * 60)

        if type == 'simple_moving_average':
            weights = np.repeat(1.0, interval_s) / interval_s
            smoothed_data = np.convolve(y_dat, weights, 'valid')

        if type == 'moving_average':
            # Adds border extension to avoid artifacts for convolution
            # Gets size of window for given timeframe
            # Convolves and trims padding elements
            x_ind = np.argmax(np.asarray([x - x_dat[0] for x in x_dat]) >= interval_s)
            window = np.ones(int(x_ind)) / float(x_ind)
            padding_start = [y_dat[0]] * x_ind  # To extend at the border to remove border error
            padding_end = [y_dat[-1]] * x_ind
            smoothed_data = np.convolve(padding_start + y_dat + padding_end, window, 'same')[x_ind:-x_ind]

        if type == 'exponential_moving_average':
            weights = np.exp(np.linspace(-1., 0., interval_s))
            weights /= weights.sum()
            smoothed_data = np.convolve(y_dat, weights, mode='full')[:len(y_dat)]
            smoothed_data[:interval_s] = smoothed_data[interval_s]

        return smoothed_data.tolist()

    def relative_strength_index(self, data, window):
        delta = np.diff(data)
        u = abs(delta * 0)
        d = u.copy()
        u[delta > 0] = abs(delta[delta > 0])
        d[delta < 0] = abs(delta[delta < 0])

        u_avg = self.smooth_data(None, u.tolist(), window, 'simple_moving_average')
        d_avg = self.smooth_data(None, d.tolist(), window, 'simple_moving_average')
        rs = np.divide(u_avg, d_avg)
        return [-1] * int(window * 60) + (100 - 100 / (1 + rs)).tolist()  # pad result for missing beginning with -1

    def centered_derivative(self, x_dat, t, type='centered'):
        d = []
        if type == 'forward':
            d_t = t[1] - t[0]
            x_dat = [x_dat[0], x_dat]
            d = (np.diff(x_dat) / d_t).tolist()

        if type == 'centered':
            # Maybe normalize with t
            d = np.gradient(x_dat).tolist()
        return d

    def find_zeros(self, x_dat):
        zeros = []
        for i in range(len(x_dat) - 1):
            if x_dat[i] > 0 and x_dat[i + 1] < 0:
                zeros.append([i, i + 1, -1])
            if x_dat[i] < 0 and x_dat[i + 1] > 0:
                zeros.append([i, i + 1, 1])
        return zeros
        # return np.where(np.array(list(map(abs, x_dat))) <= margin)[0]

    def clean_extrema(self, zeros, y_dat, diff=None, reverse=False):
        z = []
        # Calculate correct position of extrema
        for i, d in enumerate(zeros):
            if d[2] < 0:
                if y_dat[d[0]] < y_dat[d[1]]:
                    zeros[i].insert(0, d[1])
                else:
                    zeros[i].insert(0, d[0])
            else:
                if y_dat[d[0]] > y_dat[d[1]]:
                    zeros[i].insert(0, d[1])
                else:
                    zeros[i].insert(0, d[0])

        # Remove small intermediary extrema
        if diff:
            if reverse:
                zeros.reverse()
            for i, d in enumerate(zeros):
                if i > 0:
                    prev = (y_dat[z[-1][1]] + y_dat[z[-1][2]]) / 2
                    curr = (y_dat[d[1]] + y_dat[d[2]]) / 2
                    # check if next is alternating extrema
                    # if yes -> add
                    # if no -> check if new is better
                    if z[-1][3] == d[3]:
                        if d[3] > 0:  # minimum
                            if curr < prev:
                                z[-1] = d
                        else:  # maximum
                            if curr > prev:
                                z[-1] = d
                    else:
                        if abs(curr - prev) > diff:
                            z.append(d)
                    '''if abs(curr - prev) > diff:
                        # check if is alternating extrema
                        # if yes -> add
                        # if no -> check if new is better
                        if z[-1][2] == d[2]:
                            if d[2] > 0: # minimum
                                if curr < prev:
                                    z[-1] = d
                            else: # maximum
                                if curr > prev:
                                    z[-1] = d
                        else:
                            z.append(d)'''
                else:
                    z.append(d)
        else:
            z = zeros

        # Calculate extrema value
        for i, e in enumerate(z):
            z[i].append(y_dat[e[0]])

        if reverse:
           z.reverse()
        return z

    def extrema_in_interval(self, extrema, int_start, int_end):
        minimum = None
        maximum = None
        for extremum in extrema:
            if extremum[0] >= int_start and extremum[0] <= int_end:
                if extremum[3] > 0:
                    if minimum:
                        if minimum[4] > extremum[4]:
                            minimum = extremum
                    else:
                        minimum = extremum
                elif extremum[3] < 0:
                    if maximum:
                        if maximum[4] < extremum[4]:
                            maximum = extremum
                    else:
                        maximum = extremum

        if minimum[0] > maximum[0]:
            return [maximum, minimum]
        else:
            return [minimum, maximum]


    def find_extrema(self, x_dat, y_dat, diff=None):
        derivative = self.centered_derivative(y_dat, x_dat)
        extrema = self.clean_extrema(self.find_zeros(derivative), y_dat, diff)
        return extrema

    def calculate_profit(self, buy_rate, sell_rate, amount, buy_fee, sell_fee=None):
        try:
            if not sell_fee:
                sell_fee = buy_fee
            value = (amount * (1 - buy_fee)) / buy_rate
            return (value * (1 - sell_fee) * sell_rate) - amount
        except Exception:
            pass

    def calculate_min_sell_margin(self, buy_price, amount, fee=None):
        search_window_size = 100  # in USD
        margin = None
        low = buy_price

        if not fee:
            fee = self.get_current_fee('XXBTZEUR')

        if not buy_price:
            return

        if not search_window_size:
            return
        high = buy_price + search_window_size # Todo: fix and find TypeError (buy_price == Null)
        while not margin:
            tmp = (low + high) / 2
            tmp_margin = self.calculate_profit(buy_price, tmp, amount, fee)
            if abs(high - low) > 0.001:
                if tmp_margin < 0:
                    low = tmp
                else:
                    high = tmp
            else:
                return high  # return high to always make profit
        return None

    def calculate_adaptive_rsi_lim(self, data):
        p_max = max(data)
        p_min = min(data)

        even = len(data) % 2 == 0
        half = len(data) / 2
        second_start = 0

        if not even:
            second_start = 1

        first = data[0:int(half)]
        second = data[int(half + second_start):len(data)]

        t = (sum(second) - sum(first)) / sum(data) + 1

        t = (t) * (1 / 2)

        return (1 - t) * 15 + t * 25;

    def display_graph(self, x_dat, y_dat, extrema=None, yhlines=None):
        plt.figure()
        # plt.plot(times, [float(i) for i in vw_average], 'b--', label='original_data')
        # x_dat = [t - x_dat[0] for t in x_dat]
        plt.plot(x_dat, y_dat, 'k', label='smoothed_data')
        # plt.plot(times, derivative, 'r--', label='derivative')
        # plt.axhline(y=0)
        # plt.plot(times, dderivative, 'g--', label='2nd order derivative')
        '''for z in zeros:
            pass
            # plt.axvline(x=times[z[0]], color='r')'''
        if extrema:
            if len(extrema[0]) < 4:
                for z in extrema:
                    c = 'b'
                    if z[2] < 0:
                        c = 'g'
                    plt.axvline(x=x_dat[z[0]], color=c)
            else:
                for z in extrema:
                    c = 'b'
                    if z[3] < 0:
                        c = 'g'
                    plt.axvline(x=x_dat[z[0]], color=c)

        if yhlines:
            for l in yhlines:
                plt.axhline(y=l, color='r')


        #plt.axvline(x=1495379178, color='r')
        plt.axvline(x=time.time() - 60 * 10, color='r')
        '''for z in zeros:
            plt.axvline(x=times[z[1]])'''
        # plt.xticks([x_dat[i] for i in range(0, len(x_dat), 30)],
        #           [time.ctime(x_dat[i]) for i in range(0, len(x_dat), 30)])
        plt.show(block=False)
        # plt.show(block=True)
        print('done')

    def write_to_order_to_file(self, price, amount, type):
        f = open('stats.txt', 'a')
        if type == 'b':
            min_sell = self.calculate_min_sell_margin(price, amount, 0.0026)
            f.write('BUY ' + str(amount) + 'BTC at: ' + str(price) + ' | min sell: ' + str(min_sell) + '\n')
        if type == 's':
            f.write('SELL ' + str(amount) + 'BTC at: ' + str(price) + '\n')

        f.close()

    def write_extrema_to_file(self, extrema, window_pos):
        f = open('stats.txt', 'a')
        if extrema[3] > 0:
            f.write('MINIMUM at ' + str(extrema[0]) + ' with window start: ' + str(window_pos) + '\n')
        if extrema[3] < 0:
            f.write('MAXIMUM at ' + str(extrema[0]) + ' with window start: ' + str(window_pos) + '\n')

        f.close()

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
