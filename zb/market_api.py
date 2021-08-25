"""
Market Data Api
"""
from typing import List

from zb import ApiClient
from zb.model.market import *
from zb.model.constant import *


class MarketApi(ApiClient):
    def __init__(self, api_host=None):
        describe = {
            'apis': {
                'public': {
                    'get': {
                        'market_list': ' /Server/api/v2/config/marketList',
                        'kline': '/api/public/v1/kline',
                        'ticker': '/api/public/v1/ticker',
                        'depth': '/api/public/v1/depth',
                        'trade': '/api/public/v1/trade',
                        'mark_price': '/api/public/v1/markPrice',
                        'index_price': '/api/public/v1/indexPrice',
                        'spot_price': '/api/public/v1/spotPrice',
                        'mark_kline': '/api/public/v1/markKline',
                        'index_kline': '/api/public/v1/indexKline',
                    },
                },
            }
        }

        super().__init__(api_host=api_host, config=describe)

    def get_market_list(self, futures_account_type=FuturesAccountType.BASE_USDT) -> List[Market]:
        """
        6.1 交易对

        :param futures_account_type: 合约类型，1:USDT合约（默认），2:币本位合约
        :return: List[Market]
        """
        params = {
            'futuresAccountType': futures_account_type.value,
        }
        data_array = self.public_get_market_list(params)

        return [Market(**item) for item in data_array]

    def get_depth(self, symbol: str, scale=None, size=5) -> Depth:
        """
        6.2 全量深度

        :param symbol:  交易对，如：BTC_USDT
        :param scale:   精度
        :param size:    条数，最大值为200，默认值为5
        :return:
        """
        params = {
            'symbol': symbol.upper(),
            'size': size
        }
        if scale:
            params["scale"] = scale

        result = self.public_get_depth(params)

        return Depth(**result)

    def get_kline(self, symbol: str, interval=Interval.MIN_15, size=10) -> List[Kline]:
        """
        6.3  k 线

        :param symbol:      交易对，如：BTC_USDT
        :param interval:    不种时间的kline。可选范围:1M,5M,15M, 30M, 1H, 6H, 1D, 5D。M代表分钟，H代表小时，D代表天。
        :param size:        最大值为1440
        :return:
        """
        params = {
            'symbol': symbol.upper(),
            'period': interval.value,
            'size': size,

        }
        data_array = self.public_get_kline(params)

        return [Kline.json_parse(e) for e in data_array]

    def get_trade(self, symbol: str, size=50) -> List[Trade]:
        """
        6.4 成交记录

        :param symbol:  交易对，如：BTC_USDT
        :param size:    最大值为100，默认值为50
        :return:  List[Trade]
        """
        params = {
            'symbol': symbol.upper(),
            'size': size
        }

        data_array = self.public_get_trade(params)

        return [Trade.json_parse(data_object) for data_object in data_array]

    def get_ticker(self, symbol=None):
        params = {
        }

        if symbol:
            params['symbol'] = symbol.upper()

        result = self.public_get_ticker(params)

        ticker = {}
        for k, v in result.items():
            ticker[k] = Ticker.json_parse(v)

        return ticker

    def get_mark_price(self, symbol=None):
        """
        6.6  最新标记价格
        :param symbol:  交易对，如：BTC_USDT
        :return: dict
        """
        params = {
        }

        if symbol:
            params['symbol'] = symbol.upper()

        return self.public_get_mark_price(params)

    def get_index_price(self, symbol=None):
        """
        6.7  最新指数价格
        :param symbol:  交易对，如：BTC_USDT
        :return: dict
        """
        params = {
        }

        if symbol:
            params['symbol'] = symbol.upper()

        return self.public_get_index_price(params)

    def get_spot_price(self, symbol=None, is_buy=True):
        """
        6.10 zb现货兑换价格
        :param is_buy:
        :param symbol:  交易对，如：BTC_USDT
        :return: dict
        """
        params = {
            'side': 'bids' if is_buy else 'asks',
        }

        if symbol:
            params['symbol'] = symbol.upper()

        return self.public_get_spot_price(params)

    def get_mark_kline(self, symbol: str, interval=Interval.MIN_15, size=10) -> List[Kline]:
        """
        6.8  标记价格k 线
        :param symbol:      交易对，如：BTC_USDT
        :param interval:    不种时间的kline。可选范围:1M,5M,15M, 30M, 1H, 6H, 1D, 5D。M代表分钟，H代表小时，D代表天。
        :param size:        最大值为1440
        :return:
        """
        params = {
            'symbol': symbol.upper(),
            'period': interval.value,
            'size': size,

        }
        data_array = self.public_get_mark_kline(params)

        return [Kline.json_parse(e) for e in data_array]

    def get_index_kline(self, symbol: str, interval=Interval.MIN_15, size=10) -> List[Kline]:
        """
        6.9  指数价格k 线
        :param symbol:      交易对，如：BTC_USDT
        :param interval:    不种时间的kline。可选范围:1M,5M,15M, 30M, 1H, 6H, 1D, 5D。M代表分钟，H代表小时，D代表天。
        :param size:        最大值为1440
        :return: dict
        """
        params = {
            'symbol': symbol.upper(),
            'period': interval.value,
            'size': size,

        }
        data_array = self.public_get_index_kline(params)

        return [Kline.json_parse(e) for e in data_array]
