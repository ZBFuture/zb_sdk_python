import base64
import hashlib
import hmac
from datetime import datetime
from unittest import TestCase

import zb
from zb.model.constant import FuturesAccountType
from zb.utils import Utils


class TestClient(TestCase):
    client = zb.ApiClient()
    client.urls['api'] = 'https://fapi.zb.com'

    api_key = "8da1a454-2f07-48e7-b268-72582fb72794"

    secret_key = "d67355ca-3e20-41fc-8e14-bfdf506f72fc"

    def test_request(self):
        request = self.client.request("/Server/api/v2/config/marketList")
        self.assertIsNotNone(request)

    def test_hmac_sha256(self):
        key = self.secret_key.encode('utf-8')
        content = '123409'
        sign = base64.b64encode(hmac.new(key, content.encode('utf-8'), digestmod=hashlib.sha256).digest())
        print(sign)

    def test_get_server_time(self):
        param = {
            "a": None,
            "b": ""
        }
        print(param['b'] == '')
        print(param['a'] == FuturesAccountType.BASE_QC.value)
        # server_time = self.client.get_server_time()
        server_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        print(server_time)
        # print(datetime.fromtimestamp(server_time / 1000))

    def test_get_symbols(self):
        symbols = self.client.get_symbols()
        self.assertTrue(len(symbols) > 0)
        print(symbols)
        print(symbols[0].symbol, symbols[0].buyerCurrencyName)

    def test_index_by(self):
        symbols = self.client.load_markets()
        symbols_by_id = Utils.index_by(symbols, "id")
        self.assertTrue('100' in symbols_by_id)

    def test_load_symbols(self):
        symbols = self.client.load_markets()
        self.assertTrue(len(symbols) > 0)
        print(self.client.markets_by_name['btc_usdt'])
        print(self.client.markets_by_id['100'])
        self.assertTrue('BTC_USDT' in self.client.markets_by_name)

    def test_check_symbol(self):
        symbol = self.client.check_symbol("btc_usdt")
        self.assertTrue(symbol)

