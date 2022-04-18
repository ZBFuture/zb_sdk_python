# -*- coding: utf-8 -*-

"""zb client"""
import base64
import collections
import functools
import hashlib
import hmac
import json
import time
from datetime import datetime
from typing import List

import requests
from requests import Timeout

from zb.errors import *
from zb.model.common import Symbol, Currency, AssistPrice
from zb.utils import Utils


class ApiClient(object):
    enable_rate_limit = False
    last_rest_request_Timestamp = 0
    rate_limit = 2000  # milliseconds = seconds * 1000
    timeout = 10000  # milliseconds = seconds * 1000
    verbose = True
    lan = 'cn'  # cn, en, kr

    markets = None
    markets_by_id = None
    markets_by_name = None

    urls = {
        'logo': 'https://www.zb.com/src/images/logo.png',
        'api': 'https://fapi.zb.com',
        'doc': 'https://zbgapi.github.io/docs/spot/v1/cn/#185368440e',
    }
    apis = {
        'public': {
            'get': {
                'symbols': '/Server/api/v2/config/marketList',
            },
        },
    }
    exceptions = {
        10014: InvalidSign,
        10015: InvalidSign,
        10033: NotSupported,
    }

    def __init__(self, api_key=None, secret_key=None, api_host=None, config={}):

        for key in config:
            if hasattr(self, key) and isinstance(getattr(self, key), dict):
                setattr(self, key, self.deep_extend(getattr(self, key), config[key]))
            else:
                setattr(self, key, config[key])

        if api_key:
            self.__api_key = api_key
        if secret_key:
            self.__secret_key = hashlib.sha1(secret_key.encode('utf-8')).hexdigest()

        if api_host:
            self.urls['api'] = api_host

        self.define_rest_api(self.apis, 'request')

    def request(self, path, api='public', method="GET", params={}, headers=None):
        if self.enable_rate_limit:
            self.throttle()

        self.last_rest_request_Timestamp = Utils.milliseconds()

        from zb.model.constant import FuturesAccountType
        futures_account_type = Utils.safe_integer(params, "futuresAccountType")
        symbol = Utils.safe_string(params, "symbol")
        if futures_account_type == FuturesAccountType.BASE_QC.value:
            path = "/qc" + path
        elif symbol is not None and symbol.upper().endswith("QC"):
            path = "/qc" + path

        if api == 'private':
            headers = self.sign(path, method, params, headers)

        # 设置路径参数
        path = path.format(**params)
        url = self.urls['api'] + path

        response = None
        try:
            if self.verbose:
                print('method:', method, ', url :', url, ', header:', headers, ", request:", params)

            if method == "GET":
                response = requests.get(url, params=params, headers=headers)
            else:
                headers['Content-Type'] = 'application/json; charset=UTF-8'
                response = requests.post(url, data=json.dumps(params, separators=(',', ':')), headers=headers)

            if self.verbose:
                print('method:', method, ', url:', url, ", response:", response.text)
            else:
                self.handle_fail(response, method, url)

            return response.json()['data']

        except Timeout as e:
            self.raise_error(RequestTimeout, method, url, e)
        except ValueError as e:
            self.raise_error(BadResponse, method, url, e, response.text)
        except KeyError as e:
            self.raise_error(BadResponse, method, url, e, response.text)

    def throttle(self):
        now = float(Utils.milliseconds())
        elapsed = now - self.last_rest_request_Timestamp
        if elapsed < self.rate_limit:
            delay = self.rate_limit - elapsed
            time.sleep(delay / 1000.0)

    def sign(self, path, method='GET', params=None, headers=None):
        if self.__api_key == '' or self.__secret_key == '':
            raise AuthenticationError('Api key and secret key must not be empty.')

        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

        sign = self.generate_sign(timestamp, method, path, params, self.__secret_key)

        new_headers = {
            'ZB-APIKEY': self.__api_key,
            'ZB-TIMESTAMP': timestamp,
            'ZB-LAN': self.lan if self.lan else 'cn',
            'ZB-SIGN': sign
        }
        if headers:
            self.extend(new_headers, headers)

        return new_headers

    @staticmethod
    def __build_sort_param(params):
        if params is None:
            return ''

        keys = sorted(params)
        return '&'.join([k + '=' + str(params[k]) for k in keys if params[k] is not None and params[k] != ''])

    @staticmethod
    def generate_sign(timestamp, method, path, params, secret_key):
        param_str = ApiClient.__build_sort_param(params)
        content = timestamp + method + path + param_str
        print("sign string :", content)

        key = secret_key.encode('utf-8')
        sign = base64.b64encode(hmac.new(key, content.encode('utf-8'), digestmod=hashlib.sha256).digest())
        return str(sign, 'utf-8')

    def handle_fail(self, response, method=None, url=None):
        if 404 == response.status_code:
            raise NotSupported("not supported.")
        body = response.json()
        code = body['code']
        if 10000 != code:
            message = 'method: ' + method + ', url: ' + url + ', error code: ' + code + ", message: " + body['desc']

            if code in self.exceptions:
                exception_class = self.exceptions[code]
                raise exception_class(message)
            else:
                raise ZbApiException(message)

    SymbolList = List[Symbol]

    def load_markets(self, reload=False) -> SymbolList:
        if reload or not self.markets:
            self.markets = self.get_symbols()
            self.markets_by_id = Utils.index_by(self.markets, "id")
            self.markets_by_name = Utils.index_by(self.markets, "marketName")

        return self.markets

    def get_symbols(self) -> SymbolList:
        data_array = self.public_get_symbols()

        return [Symbol(**item) for item in data_array]

    def check_symbol(self, symbol: str):
        if symbol is None:
            raise ArgumentsRequired("[Input] symbol should not be null")

        self.load_markets()
        symbol = symbol.upper()
        if symbol not in self.markets_by_name:
            raise NotSupported("'" + symbol + "' is not yet supported by the zb.")

        return self.markets_by_name[symbol]

    def safe_get_symbol(self, symbol_id):
        if symbol_id is None:
            return None

        self.load_markets()
        if symbol_id not in self.markets_by_id:
            return None
        return self.markets_by_id[symbol_id]['marketName']

    @staticmethod
    def raise_error(exception_type, method=None, url=None, error=None, details=None):
        if error:
            error = str(error)
        output = ' '.join([var for var in (url, method, error, details) if var is not None])
        raise exception_type(output)

    @staticmethod
    def extend(*args):
        if args is not None:
            if type(args[0]) is collections.OrderedDict:
                result = collections.OrderedDict()
            else:
                result = {}
            for arg in args:
                result.update(arg)
            return result
        return {}

    @staticmethod
    def deep_extend(*args):
        result = None
        for arg in args:
            if isinstance(arg, dict):
                if not isinstance(result, dict):
                    result = {}
                for key in arg:
                    result[key] = ApiClient.deep_extend(result[key] if key in result else None, arg[key])
            else:
                result = arg
        return result

    @classmethod
    def define_rest_api(cls, api, method_name):
        entry = getattr(cls, method_name)  # returns a function (instead of a bound method)
        for api_type, methods in api.items():
            for http_method, urls in methods.items():
                for alias, url in urls.items():
                    url = url.strip()

                    uppercase_method = http_method.upper()
                    lowercase_method = http_method.lower()

                    underscore = api_type + '_' + lowercase_method + '_' + alias

                    def partialer():
                        outer_kwargs = {'path': url, 'api': api_type, 'method': uppercase_method}

                        @functools.wraps(entry)
                        def inner(_self, params=None):
                            inner_kwargs = dict(outer_kwargs)  # avoid mutation
                            if params is not None:
                                inner_kwargs['params'] = params
                            return entry(_self, **inner_kwargs)

                        return inner

                    to_bind = partialer()
                    setattr(cls, underscore, to_bind)
