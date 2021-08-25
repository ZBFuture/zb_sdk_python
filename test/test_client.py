import base64
import hashlib
import hmac
from datetime import datetime
from unittest import TestCase

import zb
from zb.utils import Utils


class TestClient(TestCase):
    client = zb.ApiClient()
    client.urls['api'] = 'https://www.zbgpro.net'

    api_key = "8da1a454-2f07-48e7-b268-72582fb72794"

    secret_key = "d67355ca-3e20-41fc-8e14-bfdf506f72fc"

    def test_request(self):
        request = self.client.request("/exchange/api/v1/common/symbols")
        self.assertIsNotNone(request)

    def test_hmac_sha256(self):
        key = self.secret_key.encode('utf-8')
        content = '123409'
        sign = base64.b64encode(hmac.new(key, content.encode('utf-8'), digestmod=hashlib.sha256).digest())
        print(sign)

    def test_get_server_time(self):
        param = {
            "a":None,
            "b":""
        }
        print(param['b'] == '')
        # server_time = self.client.get_server_time()
        server_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        print(server_time)
        # print(datetime.fromtimestamp(server_time / 1000))

    def test_get_symbols(self):
        symbols = self.client.get_markets()
        self.assertTrue(len(symbols) > 0)
        print(symbols)
        print(symbols[0].symbol, symbols[0].base_currency)

    def test_get_currencies(self):
        symbols = self.client.get_currencies()
        print(symbols)

    def test_index_by(self):
        symbols = self.client.load_markets()
        symbols_by_id = Utils.index_by(symbols, "id")
        self.assertTrue('336' in symbols_by_id)

    def test_load_symbols(self):
        symbols = self.client.load_markets()
        self.assertTrue(len(symbols) > 0)
        print(self.client.markets_by_name['zt_usdt'])
        print(self.client.markets_by_id['336'])
        self.assertTrue('btc_usdt' in self.client.markets_by_name)
        self.assertTrue('btc' in self.client.currencies_by_name)

    def test_get_assist_price(self):
        assist_price = self.client.get_assist_price("zt", "eos")
        print(assist_price)
        print(assist_price.to_btc_price('zt'))

