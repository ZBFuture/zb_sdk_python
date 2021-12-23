from unittest import TestCase

import zb
from zb.model import Interval


class TestMarketApi(TestCase):
    symbol = 'eth_usdt'
    market_api = zb.MarketApi(api_host='https://fapi.zb.com')

    def test_get_market_list(self):
        request = self.market_api.get_market_list()
        print(request)
        print(len(request))

    def test_get_depth(self):
        request = self.market_api.get_depth(self.symbol)
        print(request)
        print(request.bids[0])
        print(request.asks[-1])

    def test_get_kline(self):
        request = self.market_api.get_kline(self.symbol, Interval.DAY_1, 10)
        print(request)
        self.assertIsNotNone(request[0].open)

    def test_trade(self):
        request = self.market_api.get_trade(self.symbol)
        print(request)

    def test_get_ticker(self):
        request = self.market_api.get_ticker(self.symbol)
        print(request)

    def test_get_mark_price(self):
        request = self.market_api.get_mark_price()
        print(request)

    def test_get_index_price(self):
        request = self.market_api.get_index_price(self.symbol)
        print(request)

    def test_get_spot_price(self):
        request = self.market_api.get_spot_price(is_buy=False)
        print(request)

    def test_get_mark_kline(self):
        request = self.market_api.get_mark_kline(self.symbol)
        print(request)



    def test_get_historical_trades(self):
        request = self.market_api.get_historical_trades('zt_usdt')
        print(request)

        request = self.market_api.get_historical_trades('zt_usdt', 'T6623032821957013504')
        print(request)
