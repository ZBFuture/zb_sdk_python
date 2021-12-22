from unittest import TestCase
import zb
from zb.model.constant import TransferType, WithdrawState, Direct, PositionsMode, MarginMode


class TestAccountApi(TestCase):

    symbol = 'ETH_USDT'
    api = zb.AccountApi(api_key='9807581e-992e-41ca-8fa4-639fbf1c939f',
                        secret_key='a7a15b46-eb08-431e-81e4-096bd12e2a48',
                        api_host='https://fapi.zb.com')

    def test_get_account(self):

        print([m for m in dir(self.api) if m.startswith('private')])
        request = self.api.get_account()
        self.assertIsNotNone(request)
        print(request.account)
        print(request.assets)

    def test_get_positions(self):
        request = self.api.get_positions('eth_usdt')
        print(request)


    def test_get_margin_info(self):
        request = self.api.get_margin_info(position_id=6833656775477045248)
        print(request)

    def test_set_leverage(self):
        request = self.api.set_leverage(self.symbol, 11)
        print(request)

    def test_set_positions_mode(self):
        request = self.api.set_positions_mode(self.symbol, PositionsMode.OneDirection)
        print(request)

    def test_set_margin_mode(self):
        request = self.api.set_margin_mode(self.symbol, MarginMode.Isolated)
        print(request)

    def test_get_nominal_value(self):
        request = self.api.get_nominal_value(self.symbol, 1)
        print(request)

    def test_get_bill(self):
        request = self.api.get_bill(currency='eth', size=1)
        print(request)

    def test_get_bill_type_list(self):
        request = self.api.get_bill_type_list()
        print(request)

    def test_get_margin_history(self):
        request = self.api.get_margin_history(self.symbol)
        print(request)

    def test_get_setting(self):
        request = self.api.get_setting(self.symbol)
        print(request)

    def test_get_balance(self):
        request = self.api.get_balance("eth")
        print(request)

    def test_update_append_usd_value(self):
        request = self.api.update_append_usd_value(6833656775477045248, 1212.12)
        print(request)

    def test_set_margin_coins(self):
        request = self.api.set_margin_coins(self.symbol, 'eth,usdt')
        print(request)