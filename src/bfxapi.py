from src.api import API

class BFXAPI(API):
    def __init__(self):
        print('...setting up bitfinex api')

    # =========================
    # Unauthenticated endpoints
    # =========================

    def get_ticker(self):
        print('ticker')
        # Todo implement ticker

    def get_statistics(self):
        print('stats')
        # Todo implement stats

    def get_fundingbook(self):
        print('fundingbook')
        # Todo implement fundingbook

    def get_orderbook(self):
        print('orderbook')
        # Todo implement orderbook

    def get_trades(self):
        print('trades')
        # Todo implement trades

    def get_lends(self):
        print('lends')
        # Todo implement lends

    def get_symbols(self):
        print('symbols')
        # Todo implement symbols

    def get_symbol_detail(self):
        print('symbol detail')
        # Todo implement symbol detail

    # =======================
    # Authenticated Endpoints
    # =======================

    def get_acc_info(self):
        print('account info')
        # Todo implement symbol detail

    def get_summary(self):
        print('30d summary')
        # Todo implement symbol detail

    def get_deposit_address(self):
        print('deposit')
        # Todo implement symbol detail

    def get_api_key_perm(self):
        print('get api key permissions')
        # Todo implement symbol detail

    def get_margin_info(self):
        print('margin info')
        # Todo implement symbol detail

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

    def history_balance(self):
        print('balance history')
        # Todo implement symbol detail

    def history_deposit_withraw(self):
        print('deposit withdrawal history')
        # Todo implement symbol detail

    def history_past_trades(self):
        print('past trades history')
        # Todo implement symbol detail

    # ==============================
    # Authenticated - Margin Funding
    # ==============================

    def funding_new_offer(self):
        print('new offer funding')
        # Todo implement symbol detail

    def funding_cancel_offer(self):
        print('cancel offer funding')
        # Todo implement symbol detail

    def funding_offer_status(self):
        print('status offer funding')
        # Todo implement symbol detail

    def funding_active_credit(self):
        print('active_credit funding')
        # Todo implement symbol detail

    def funding_active_offer(self):
        print('active offer funding')
        # Todo implement symbol detail

    def funding_active_funding_used(self):
        print('active offer used funding')
        # Todo implement symbol detail

    def funding_active_funding_unused(self):
        print('active offer unused funding')
        # Todo implement symbol detail

    def funding_taken(self):
        print('taken funding')
        # Todo implement symbol detail

    def funding_close(self):
        print('close funding')
        # Todo implement symbol detail