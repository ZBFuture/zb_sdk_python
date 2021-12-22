import json
from unittest import TestCase
import zb
from zb.model.constant import *
from zb.model.trade import OrderRequest


class TestTradeApi(TestCase):
    symbol = 'ETH_USDT'
    api = zb.TradeApi(api_key='8da1a454-2f07-48e7-b268-72582fb72794',
                        secret_key='d67355ca-3e20-41fc-8e14-bfdf506f72fc',
                        api_host='http://fapi.zb.com')

    def test_buy(self):
        param = [OrderRequest(self.symbol, 1, 1, 10, 1000, 1, None),]
        param_ = [a.__dict__ for a in param]
        json_str = json.dumps(param_)
        print(json_str)

    def test_order(self):
        request = self.api.order(self.symbol, Action.LIMIT, OrderSide.SIDE_OPEN_LONG, 1000, 1,1)
        print(request)

    def test_cancel_order(self):
        request = self.api.cancel_order(self.symbol, 6834450285260185600)
        print(request)

    def test_batch_cancel_orders(self):
        request = self.api.batch_cancel_orders(symbol=self.symbol, order_ids=[6834411668051599365,])
        print(request)

    def test_cancel_all_orders(self):
        request = self.api.cancel_all_orders(symbol=self.symbol)
        print(request)

    def test_get_undone_orders(self):
        request = self.api.get_undone_orders(self.symbol)
        print(request)

    def test_get_all_orders(self):
        request = self.api.get_all_orders(self.symbol)
        print(request)

    def test_get_order(self):
        request = self.api.get_order(self.symbol, 6834411668051599365)
        print(request)
        request = self.api.get_order(self.symbol, client_order_id=6834411668047407139)
        print(request)

    def test_get_trade_list(self):
        request = self.api.get_trade_list(symbol=self.symbol, order_id=6834411668051599365)
        print(request)
