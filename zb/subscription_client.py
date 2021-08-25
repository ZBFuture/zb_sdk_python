import hashlib
import json
import time
from datetime import datetime
from typing import List

from zb.model.constant import Channel, FuturesAccountType, Action, OrderSide
from zb.model.subscribe_envet import *
from zb.model.trade import OrderRequest
from zb.websocket_connection import WebsocketConnection, ArgumentsRequired
from zb.websocket_watch_dog import WebSocketWatchDog


class WebsocketRequest(object):
    def __init__(self):
        self.subscription_handler = None
        self.unsubscription_handler = None
        self.auto_close = False
        self.error_handler = None
        self.json_parser = None
        self.update_callback = None


class SubscriptionClient(object):
    def __init__(self, **kwargs):
        """
        Create the subscription client to subscribe the update from server.

        :param kwargs: The option of subscription connection.
            uri: Set the URI for subscription.
            is_auto_connect: When the connection lost is happening on the subscription line, specify whether the client
                            reconnect to server automatically. The connection lost means:
                                Caused by network problem
                                The connection close triggered by server (happened every 24 hours)
                            No any message can be received from server within a specified time, see receive_limit_ms
            receive_limit_ms: Set the receive limit in millisecond. If no message is received within this limit time,
                            the connection will be disconnected.
            connection_delay_failure: If auto reconnect is enabled, specify the delay time before reconnect.
        """
        self._api_key = None
        self._secret_key = None
        if "api_key" in kwargs:
            self._api_key = kwargs["api_key"]
        if "secret_key" in kwargs:
            secret_key = kwargs["secret_key"]
            self._secret_key = hashlib.sha1(secret_key.encode('utf-8')).hexdigest()

        self.connections = list()

        self.url = 'wss://futures.zb.land/ws/public/v1'
        self.is_auto_connect = True
        self.receive_limit_ms = 60000
        self.connection_delay_failure = 15

        if 'url' in kwargs:
            self.url = kwargs["url"]
        if "is_auto_connect" in kwargs:
            self.is_auto_connect = kwargs["is_auto_connect"]
        if "receive_limit_ms" in kwargs:
            self.receive_limit_ms = kwargs["receive_limit_ms"]
        if "connection_delay_failure" in kwargs:
            self.connection_delay_failure = kwargs["connection_delay_failure"]
        self._watch_dog = WebSocketWatchDog(self.is_auto_connect, self.receive_limit_ms, self.connection_delay_failure)

    def _create_connection(self, channel, callback, json_parser, error_handler=None, **kwargs):
        def subscription_handler(conn):
            param = {
                'action': 'subscribe',
                'channel': channel
            }
            if kwargs:
                param.update(kwargs)
            message = json.dumps(param)
            print('subscribe message:', message)
            conn.send(message)

        request = WebsocketRequest()
        request.channel = channel
        request.subscription_handler = subscription_handler
        request.json_parser = json_parser
        request.update_callback = callback
        request.error_handler = error_handler

        connection = WebsocketConnection(self._api_key, self._secret_key, self.url, self._watch_dog, request)
        self.connections.append(connection)
        connection.connect()

        return connection

    def _disconnection(self, connection: WebsocketConnection):
        channel = connection.request.channel
        if channel == 'login':
            return
        param = {
            'action': 'unsubscribe',
            'channel': channel,
        }
        connection.send(param)
        connection.on_close()
        self.connections.remove(connection)


class MarketClient(SubscriptionClient):
    def __init__(self, **kwargs):
        """
        Create the subscription client to subscribe the update from server.

        :param kwargs: The option of subscription connection.
            uri: Set the URI for subscription.
            is_auto_connect: When the connection lost is happening on the subscription line, specify whether the client
                            reconnect to server automatically. The connection lost means:
                                Caused by network problem
                                The connection close triggered by server (happened every 24 hours)
                            No any message can be received from server within a specified time, see receive_limit_ms
            receive_limit_ms: Set the receive limit in millisecond. If no message is received within this limit time,
                            the connection will be disconnected.
            connection_delay_failure: If auto reconnect is enabled, specify the delay time before reconnect.
        """
        if 'uri' not in kwargs:
            kwargs['uri'] = 'wss://futures.zb.land/ws/public/v1'
        super().__init__(**kwargs)

    def _subscribe_event(self, channel, callback, json_parser, size, error_handler):

        conn = self._create_connection(channel=channel,
                                       callback=callback,
                                       json_parser=json_parser,
                                       error_handler=error_handler,
                                       size=size)
        return conn.id

    def subscribe_whole_depth_event(self, symbol: str, callback, scale=None, size=5, error_handler=None):
        """
        7.3 全量深度

        :param symbol:      The symbols, like "btc_usdt".
        :param scale:       盘口精度
        :param size:        记录条数,最大值为10，默认值为5
        :param callback:    The implementation is required. onReceive will be called if receive server's update.
            example: def callback(candlestick_event: CandlestickEvent):
                        pass
        :param error_handler: The error handler will be called if subscription failed or error happen between client and Huobi server
            example: def error_handler(exception: ZbgApiException)
                        pass
        :return: id
        """
        channel = symbol.upper() + '.' + Channel.WHOLE_DEPTH.value
        if scale:
            channel = channel + '@' + str(scale)

        def json_parse(json_wrapper):
            return DepthEvent(**json_wrapper)

        return self._subscribe_event(channel, callback, json_parse, size, error_handler)

    def subscribe_depth_event(self, symbol: str, callback, scale=None, size=5, error_handler=None):
        """
        7.3 全量深度

        :param symbol:      The symbols, like "btc_usdt".
        :param scale:       盘口精度
        :param size:        记录条数,最大值为10，默认值为5
        :param callback:    The implementation is required. onReceive will be called if receive server's update.
            example: def callback(candlestick_event: CandlestickEvent):
                        pass
        :param error_handler: The error handler will be called if subscription failed or error happen between client and Huobi server
            example: def error_handler(exception: ZbgApiException)
                        pass
        :return: id
        """
        channel = symbol.upper() + '.' + Channel.DEPTH.value
        if scale:
            channel = channel + '@' + str(scale)

        def json_parse(json_wrapper):
            return DepthEvent(**json_wrapper)

        return self._subscribe_event(channel, callback, json_parse, size, error_handler)

    def subscribe_kline_event(self, symbol: 'str', callback, interval: Interval, size=100, error_handler=None):
        """
        Subscribe candlestick/kline event. If the candlestick/kline is updated, server will send the data to client and onReceive in callback will
        be called.

        :param symbol:      The symbols, like "btc_usdt".
        :param interval:    The candlestick/kline interval, MIN1, MIN5, DAY1 etc.
        :param callback:    The implementation is required. onReceive will be called if receive server's update.
            example: def callback(candlestick_event: CandlestickEvent):
                        pass
        :param error_handler: The error handler will be called if subscription failed or error happen between client and Huobi server
            example: def error_handler(exception: ZbgApiException)
                        pass
        :param size: The number of data returned the first time.max : 1440
        :return: id
        """
        channel = symbol.upper() + '.' + Channel.KLINE.value + '_' + interval.value

        def json_parse(json_wrapper):
            return KlineEvent(**json_wrapper)

        return self._subscribe_event(channel, callback, json_parse, size, error_handler)

    def subscribe_trade_event(self, symbol: 'str', callback, size=50, error_handler=None):
        """
        Subscribe trade event. If the trade is generated, server will send the data to client and onReceive in callback will be called.

        :param symbol: The symbols, like "btc_usdt".
        :param callback: The implementation is required. onReceive will be called if receive server's update.
            example: def callback(candlestick_event: CandlestickEvent):
                        pass
        :param error_handler: The error handler will be called if subscription failed or error happen between client and Huobi server
            example: def error_handler(exception: ZbgApiException)
                        pass
        :param size: The number of data returned the first time.max:100
        :return: id
        """
        channel = symbol.upper() + '.' + Channel.TRADE.value

        def json_parse(json_wrapper):
            return TradeEvent(**json_wrapper)

        return self._subscribe_event(channel, callback, json_parse, size, error_handler)

    def subscribe_ticker_event(self, symbol: 'str', callback, error_handler=None):
        """
        Subscribe 24 hours trade statistics event. If the statistics is generated, server will send the data to client and onReceive in callback will be called.

        :param symbol: The symbol, like "btc_usdt" .
        :param callback: The implementation is required. onReceive will be called if receive server's update.
            example: def callback(candlestick_event: CandlestickEvent):
                        pass
        :param error_handler: The error handler will be called if subscription failed or error happen between client and Huobi server
            example: def error_handler(exception: ZbgApiException)
                        pass
        :return: id
        """

        channel = symbol.upper() + '.' + Channel.TICKER.value

        def json_parse(json_wrapper):
            return TickerEvent(**json_wrapper)

        return self._subscribe_event(channel, callback, json_parse, 1, error_handler)

    def subscribe_all_ticker_event(self, callback, error_handler=None):
        """
        Subscribe 24 hours trade statistics event. If the statistics is generated, server will send the data to client and onReceive in callback will be called.

        :param callback: The implementation is required. onReceive will be called if receive server's update.
            example: def callback(candlestick_event: CandlestickEvent):
                        pass
        :param error_handler: The error handler will be called if subscription failed or error happen between client and Huobi server
            example: def error_handler(exception: ZbgApiException)
                        pass
        :return: id
        """

        channel = 'All.' + Channel.TICKER.value

        def json_parse(json_wrapper):
            return AllTickerEvent(**json_wrapper)

        return self._subscribe_event(channel, callback, json_parse, 1, error_handler)

    def subscribe_mark_price_event(self, symbol: 'str', callback, error_handler=None):

        channel = symbol.upper() + '.mark'

        def json_parse(json_wrapper):
            return Event(**json_wrapper)

        return self._subscribe_event(channel, callback, json_parse, 1, error_handler)

    def subscribe_all_mark_price_event(self, callback, error_handler=None):

        channel = 'All.mark'

        def json_parse(json_wrapper):
            return Event(**json_wrapper)

        return self._subscribe_event(channel, callback, json_parse, 1, error_handler)

    def subscribe_index_price_event(self, symbol: 'str', callback, error_handler=None):

        channel = symbol.upper() + '.index'

        def json_parse(json_wrapper):
            return Event(**json_wrapper)

        return self._subscribe_event(channel, callback, json_parse, 1, error_handler)

    def subscribe_all_index_price_event(self, callback, error_handler=None):

        channel = 'All.index'

        def json_parse(json_wrapper):
            return Event(**json_wrapper)

        return self._subscribe_event(channel, callback, json_parse, 1, error_handler)

    def subscribe_mark_kline_event(self, symbol: 'str', callback, interval=Interval.MIN_15, size=10, error_handler=None):

        channel = symbol.upper() + '.mark_' + interval.value

        def json_parse(json_wrapper):
            return KlineEvent(**json_wrapper)

        return self._subscribe_event(channel, callback, json_parse, size, error_handler)

    def subscribe_index_kline_event(self, symbol: 'str', callback, interval=Interval.MIN_15, size=10, error_handler=None):

        channel = symbol.upper() + '.index_' + interval.value

        def json_parse(json_wrapper):
            return KlineEvent(**json_wrapper)

        return self._subscribe_event(channel, callback, json_parse, size, error_handler)

    def subscribe_fund_rate_event(self, symbol: 'str', callback, error_handler=None):

        channel = symbol.upper() + '.FundingRate'

        def json_parse(json_wrapper):
            return Event(**json_wrapper)

        return self._subscribe_event(channel, callback, json_parse, 1, error_handler)

    def subscribe_spot_price_event(self, symbol: 'str', callback, side='bids', error_handler=None):
        name = 'All' if symbol.upper() == 'ALL' else symbol.upper()
        channel = name + '.' + side.lower() + 'SpotPrice'

        def json_parse(json_wrapper):
            return Event(**json_wrapper)

        return self._subscribe_event(channel, callback, json_parse, 1, error_handler)

    def unsubscribe_event(self, conn_id=None, channel=None):
        if conn_id:
            for conn in self.connections[:]:
                if conn.id == conn_id:
                    self._disconnection(conn)

        if channel:
            for conn in self.connections[:]:
                if conn.request.channel == channel:
                    self._disconnection(conn)


class WsAccountClient(SubscriptionClient):
    LOGIN = "login"
    PONG = "pong"
    Subscribe = "subscribe"

    # fund channel
    CH_FundChange = "Fund.change"
    CH_FundBalance = "Fund.balance"
    CH_FundGetAccount = "Fund.getAccount"
    CH_FundGetBill = "Fund.getBill"
    CH_FundAssetChange = "Fund.assetChange"
    CH_FundAssetInfo = "Fund.assetInfo"

    # position channel
    CH_PositionsChange = "Positions.change"
    CH_getPositions = "Positions.getPositions"
    CH_marginInfo = "Positions.marginInfo"
    CH_updateMargin = "Positions.updateMargin"
    CH_getSetting = "Positions.getSetting"
    CH_setLeverage = "Positions.setLeverage"
    CH_setPositionsMode = "Positions.setPositionsMode"
    CH_setMarginMode = "Positions.setMarginMode"
    CH_getNominalValue = "Positions.getNominalValue"

    # trade channel
    CH_getOrder = "Trade.getOrder"
    CH_getUndoneOrders = "trade.getUndoneOrders"
    CH_getAllOrders = "trade.getAllOrders"
    CH_getTradeList = "trade.getTradeList"
    CH_tradeHistory = "trade.tradeHistory"
    CH_orderChange = "Trade.orderChange"
    CH_order = "Trade.order"
    CH_batchOrder = "Trade.batchOrder"
    CH_cancelOrder = "Trade.cancelOrder"
    CH_batchCancelOrder = "Trade.batchCancelOrder"
    CH_cancelAllOrders = "trade.cancelAllOrders"

    def __init__(self, api_key, secret_key, url, **kwargs):
        self.callback_map = dict()
        self.json_parser_map = dict()
        self.error_handler_map = dict()
        self.connection = None

        super().__init__(api_key=api_key, secret_key=secret_key, url=url, **kwargs)

    def login(self):
        def json_parser(json_wrapper):
            print('data message: >>>>>> ', json_wrapper)
            channel = Utils.safe_string(json_wrapper, 'channel')
            if channel in self.json_parser_map:
                return self.json_parser_map[channel](json_wrapper)
            else:
                print('no error handler for :', str(json_wrapper))

            return json_wrapper

        def callback(event):
            channel = Utils.safe_string(event, 'channel')
            if channel in self.callback_map:
                return self.callback_map[channel](event)
            else:
                print('no callback for :', str(event))

        def error_handler(message):
            if isinstance(message, dict):
                channel = Utils.safe_string(message, 'channel')
                if channel in self.error_handler_map:
                    return self.error_handler_map[channel](message)
            else:
                print('ws error message >>>>>', message)

        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        from zb import ApiClient
        sign = ApiClient.generate_sign(timestamp, "GET", self.LOGIN, None, self._secret_key)
        param = {
            'action': 'login',
            'ZB-APIKEY': self._api_key,
            'ZB-TIMESTAMP': timestamp,
            'ZB-SIGN': sign
        }
        self.connection = self._create_connection(channel='login',
                                                  callback=callback,
                                                  json_parser=json_parser,
                                                  error_handler=error_handler,
                                                  **param)
        time.sleep(2)

    def subscribe(self, channel, data, callback, json_parser, error_handler):
        param = {
            'action': self.Subscribe,
            'channel': channel,
        }

        if data:
            param.update(data)
        if self.connection is None:
            self.login()

        print("send subscribe message >>>>", json.dumps(param))
        self.connection.send(json.dumps(param))
        self.callback_map[channel] = callback
        if json_parser:
            self.json_parser_map[channel] = json_parser
        if error_handler:
            self.error_handler_map[channel] = error_handler


    def unsubscribe(self, channel, futures_account_type=FuturesAccountType.BASE_USDT,):
        if self.connection:
            param = {
                'action': 'unsubscribe',
                'channel': channel,
                'futuresAccountType': futures_account_type.value
            }
            message = json.dumps(param)
            print("send unsubscribe message >>>>", message)
            self.connection.send(message)

    def subscribe_fund_change(self, callback, currency=None, futures_account_type=FuturesAccountType.BASE_USDT, error_handler=None):
        param = {
            'futuresAccountType': futures_account_type.value,
        }

        if currency:
            param['currency'] = currency

        def json_parser(json_wrapper):
            return Event(**json_wrapper)

        self.subscribe(self.CH_FundChange, param, callback, json_parser, error_handler)

    def get_balance(self, callback, currency=None, futures_account_type=FuturesAccountType.BASE_USDT, error_handler=None):
        param = {
            'currency': currency if currency else '',
            'futuresAccountType': futures_account_type.value,
        }

        def json_parser(json_wrapper):
            return Event(**json_wrapper)

        self.subscribe(self.CH_FundBalance, param, callback, json_parser, error_handler)

    def get_account(self, callback, convert_unit='cny', futures_account_type=FuturesAccountType.BASE_USDT, error_handler=None):
        param = {
            'convertUnit': convert_unit,
            'futuresAccountType': futures_account_type.value,
        }

        def json_parser(json_wrapper):
            return Event(**json_wrapper)

        self.subscribe(self.CH_FundGetAccount, param, callback, json_parser, error_handler)

    def get_bill(self, callback, currency=None, bill_type=None, start_time=None, end_time=None, page=1, size=10, futures_account_type=FuturesAccountType.BASE_USDT, error_handler=None):
        param = {
            'futuresAccountType': futures_account_type.value,
            'pageNum': page,
            'pageSize': size,
        }
        if currency:
            param['currency'] = currency
        if bill_type:
            param['type'] = bill_type
        if start_time:
            param['startTime'] = start_time
        if end_time:
            param['endTime'] = end_time

        def json_parser(json_wrapper):
            return Event(**json_wrapper)

        self.subscribe(self.CH_FundGetBill, param, callback, json_parser, error_handler)

    def subscribe_asset_change(self, callback, convert_unit='cny', futures_account_type=FuturesAccountType.BASE_USDT, error_handler=None):
        param = {
            'futuresAccountType': futures_account_type.value,
            'convertUnit': convert_unit,
        }

        def json_parser(json_wrapper):
            return Event(**json_wrapper)

        self.subscribe(self.CH_FundAssetChange, param, callback, json_parser, error_handler)

    def get_asset_info(self, callback, convert_unit='cny', futures_account_type=FuturesAccountType.BASE_USDT, error_handler=None):
        param = {
            'futuresAccountType': futures_account_type.value,
        }
        if convert_unit:
            param['convertUnit'] = convert_unit

        def json_parser(json_wrapper):
            return Event(**json_wrapper)

        self.subscribe(self.CH_FundAssetInfo, param, callback, json_parser, error_handler)

    def subscribe_positions_change(self, callback, symbol=None, futures_account_type=FuturesAccountType.BASE_USDT, error_handler=None):
        param = {
            'futuresAccountType': futures_account_type.value,
        }
        if symbol:
            param['symbol'] = symbol

        def json_parser(json_wrapper):
            return Event(**json_wrapper)

        self.subscribe(self.CH_PositionsChange, param, callback, json_parser, error_handler)

    def get_positions(self, callback, symbol=None, futures_account_type=FuturesAccountType.BASE_USDT, error_handler=None):
        param = {
            'futuresAccountType': futures_account_type.value,
        }
        if symbol:
            param['symbol'] = symbol

        def json_parser(json_wrapper):
            return Event(**json_wrapper)

        self.subscribe(self.CH_getPositions, param, callback, json_parser, error_handler)

    def get_margin(self, callback, positions_id: int, futures_account_type=FuturesAccountType.BASE_USDT, error_handler=None):
        param = {
            'futuresAccountType': futures_account_type.value,
            'positionsId': positions_id,
        }

        def json_parser(json_wrapper):
            return Event(**json_wrapper)

        self.subscribe(self.CH_marginInfo, param, callback, json_parser, error_handler)

    def update_margin(self, callback, positions_id: int, amount: float, type: int, futures_account_type=FuturesAccountType.BASE_USDT, error_handler=None):
        """
        8.4.4、提取或增加保证金
        :param callback:        结果处理函数
        :param positions_id:    仓位id
        :param amount:          变动数量
        :param type:            1: 增加  0：减少
        :param futures_account_type:
        :param error_handler:
        :return:
        """
        param = {
            'futuresAccountType': futures_account_type.value,
            'positions_id': positions_id,
            'amount': amount,
            'type': type,
        }

        def json_parser(json_wrapper):
            return Event(**json_wrapper)

        self.subscribe(self.CH_updateMargin, param, callback, json_parser, error_handler)

    def get_setting(self, callback, symbol: str, futures_account_type=FuturesAccountType.BASE_USDT, error_handler=None):
        """
        8.4.5、仓位配置信息查询
        :param callback:            结果处理函数
        :param symbol:              合约，即市场交易对唯一标识符，如：BTC_USDT
        :param futures_account_type:
        :param error_handler:
        :return:
        """
        param = {
            'futuresAccountType': futures_account_type.value,
            'symbol': symbol,
        }

        def json_parser(json_wrapper):
            return Event(**json_wrapper)

        self.subscribe(self.CH_getSetting, param, callback, json_parser, error_handler)

    def set_leverage(self, callback, symbol: str, leverage: int, futures_account_type=FuturesAccountType.BASE_USDT, error_handler=None):
        """
        8.4.6、仓位杠杆设置
        :param callback:            结果处理函数
        :param symbol:              合约，即市场交易对唯一标识符，如：BTC_USDT
        :param leverage:            杠杆倍数
        :param futures_account_type:1:USDT永续合约  2：币本位合约
        :param error_handler:       错误处理函数
        :return:
        """
        param = {
            'symbol': symbol,
            'leverage': leverage,
            'futuresAccountType': futures_account_type.value,
        }

        def json_parser(json_wrapper):
            return Event(**json_wrapper)

        self.subscribe(self.CH_setLeverage, param, callback, json_parser, error_handler)

    def set_positions_mode(self, callback, symbol: str, positions_mode: int, futures_account_type=FuturesAccountType.BASE_USDT, error_handler=None):
        """
        8.4.7、仓位持仓模式设置
        :param callback:            结果处理函数
        :param symbol:              合约，即市场交易对唯一标识符，如：BTC_USDT
        :param positions_mode:      1:单向持仓，2: 双向持仓
        :param futures_account_type:1:USDT永续合约  2：币本位合约
        :param error_handler:       错误处理函数
        :return:
        """
        param = {
            'symbol': symbol,
            'positionsMode': positions_mode,
            'futuresAccountType': futures_account_type.value,
        }

        def json_parser(json_wrapper):
            return Event(**json_wrapper)

        self.subscribe(self.CH_setPositionsMode, param, callback, json_parser, error_handler)

    def set_margin_mode(self, callback, symbol: str, margin_mode: int, futures_account_type=FuturesAccountType.BASE_USDT, error_handler=None):
        """
        8.4.8、仓位保证金模式设置
        :param callback:            结果处理函数
        :param symbol:              合约，即市场交易对唯一标识符，如：BTC_USDT
        :param margin_mode:         1 逐仓（默认），2 全仓
        :param futures_account_type:1:USDT永续合约  2：币本位合约
        :param error_handler:       错误处理函数
        :return:
        """
        param = {
            'symbol': symbol,
            'marginMode': margin_mode,
            'futuresAccountType': futures_account_type.value,
        }

        def json_parser(json_wrapper):
            return Event(**json_wrapper)

        self.subscribe(self.CH_setMarginMode, param, callback, json_parser, error_handler)

    def get_nominal_value(self, callback, symbol: str, side: int, futures_account_type=FuturesAccountType.BASE_USDT, error_handler=None):
        """
        8.4.9、查看用户当前头寸
        :param callback:            结果处理函数
        :param symbol:              合约，即市场交易对唯一标识符，如：BTC_USDT
        :param side:                方向：1：开多   0 开空
        :param futures_account_type:1:USDT永续合约  2：币本位合约
        :param error_handler:       错误处理函数
        :return:
        """
        param = {
            'symbol': symbol,
            'side': side,
            'futuresAccountType': futures_account_type.value,
        }

        def json_parser(json_wrapper):
            return Event(**json_wrapper)

        self.subscribe(self.CH_getNominalValue, param, callback, json_parser, error_handler)

    ## 订单和交易相关

    def subscribe_order_change(self, callback, symbol=None, futures_account_type=FuturesAccountType.BASE_USDT, error_handler=None):
        """
        8.5.1、订单变动
        :param callback:            结果处理函数
        :param symbol:              合约，即市场交易对唯一标识符，如：BTC_USDT， 没有symbol，表示仓位的任何变动都会推送给客户。如果指定了symbol，则只会推送此market的仓位变动给客户
        :param futures_account_type:1:USDT永续合约  2：币本位合约
        :param error_handler:       错误处理函数
        :return:
        """
        param = {
            'futuresAccountType': futures_account_type.value,
        }
        if symbol:
            param['symbol'] = symbol

        def json_parser(json_wrapper):
            return Event(**json_wrapper)

        self.subscribe(self.CH_orderChange, param, callback, json_parser, error_handler)

    def order(self, callback, symbol: str, side: OrderSide, amount: float, price: float, action=Action.LIMIT, entrust_type=1, error_handler=None):
        """
        8.5.2、下单
        :param callback:            结果处理函数
        :param symbol:              合约，即市场交易对唯一标识符，如：BTC_USDT
        :param price:               价格
        :param amount:              数量
        :param action:              委托动作: 1 限价, 2 市价, 3 IOC, 4 只做 maker, 5 FOK
        :param entrust_type:        委托类型：1限价委托，2强平委托，3限价止盈，4限价止损
        :param side:                方向：1开多（买入），2开空（卖出），3平多（卖出），4平空（买入）
        :param error_handler:       错误处理函数
        :return:
        """
        param = {
            'symbol': symbol,
            'price': price,
            'amount': amount,
            'action': action.value,
            'entrust_type': entrust_type,
            'side': side.value,
        }

        def json_parser(json_wrapper):
            return Event(**json_wrapper)

        self.subscribe(self.CH_order, param, callback, json_parser, error_handler)

    def get_order(self, callback, symbol: str, order_id=None, client_order_id=None, error_handler=None):
        """
        8.5.3、查询订单明细 order_ids和client_order_ids二选一
        :param callback:            结果处理函数
        :param symbol:              合约，即市场交易对唯一标识符，如：BTC_USDT
        :param order_id:            订单ID    int
        :param client_order_id:     自定义id   str
        :param error_handler:       错误处理函数
        :return:
        """
        if order_id is None and client_order_id is None:
            raise ArgumentsRequired('order_id 与 client_order_id 选填1个')

        param = {
            'symbol': symbol,
        }
        if order_id:
            param['orderId'] = order_id
        if client_order_id:
            param['clientOrderId'] = client_order_id

        def json_parser(json_wrapper):
            return Event(**json_wrapper)

        self.subscribe(self.CH_getOrder, param, callback, json_parser, error_handler)

    def cancel_order(self, callback, symbol: str, order_id=None, client_order_id=None, error_handler=None):
        """
        8.5.4、取消订单
        :param callback:            结果处理函数
        :param symbol:              合约，即市场交易对唯一标识符，如：BTC_USDT
        :param order_id:            订单ID    int
        :param client_order_id:     自定义id   str
        :param error_handler:       错误处理函数
        :return:
        """

        if order_id is None and client_order_id is None:
            raise ArgumentsRequired('order_id 与 client_order_id 选填1个')

        param = {
            'symbol': symbol,
        }
        if order_id:
            param['orderId'] = order_id
        if client_order_id:
            param['clientOrderId'] = client_order_id

        def json_parser(json_wrapper):
            return Event(**json_wrapper)

        self.subscribe(self.CH_cancelOrder, param, callback, json_parser, error_handler)

    def batch_cancel_order(self, callback, symbol: str, order_ids=None, client_order_ids=None, error_handler=None):
        """
        8.5.5、批量取消委托
        :param callback:            结果处理函数
        :param symbol:              合约，即市场交易对唯一标识符，如：BTC_USDT
        :param order_ids:           订单ID列表
        :param client_order_ids:    自定义id 列表
        :param error_handler:       错误处理函数
        :return:
        """
        if order_ids is None and client_order_ids is None:
            raise ArgumentsRequired('order_ids 与 client_order_ids 选填1个')

        param = {
            'symbol': symbol,
        }

        if order_ids:
            param['orderIds'] = order_ids
        if client_order_ids:
            param['clientOrderIds'] = client_order_ids

        def json_parser(json_wrapper):
            return Event(**json_wrapper)

        self.subscribe(self.CH_batchCancelOrder, param, callback, json_parser, error_handler)

    def cancel_all_orders(self, callback, symbol: str, error_handler=None):
        """
        8.5.6、取消所有订单
        :param callback:            结果处理函数
        :param symbol:              合约，即市场交易对唯一标识符，如：BTC_USDT
        :param error_handler:       错误处理函数
        :return:
        """
        param = {
            'symbol': symbol,
        }

        def json_parser(json_wrapper):
            return Event(**json_wrapper)

        self.subscribe(self.CH_cancelAllOrders, param, callback, json_parser, error_handler)

    def get_undone_orders(self, callback, symbol: str, page=1, size=10, error_handler=None):
        """
        8.5.7、查询当前全部挂单(未完成的订单列表)
        :param callback:            结果处理函数
        :param symbol:              合约，即市场交易对唯一标识符，如：BTC_USDT
        :param page:                页码，从1开始
        :param size:                分页大小
        :param error_handler:       错误处理函数
        :return:
        """
        param = {
            'symbol': symbol,
            'pageNum': page,
            'sizeSize': size,
        }

        def json_parser(json_wrapper):
            return Event(**json_wrapper)

        self.subscribe(self.CH_getUndoneOrders, param, callback, json_parser, error_handler)

    def get_all_orders(self, callback, symbol: str, start_time=None, end_time=None, page=1, size=10, error_handler=None):
        """
        8..5.8、查询所有订单
        :param callback:            结果处理函数
        :param symbol:              合约，即市场交易对唯一标识符，如：BTC_USDT
        :param start_time:          开始时间戳
        :param end_time:            结束时间戳
        :param page:                页码，从1开始
        :param size:                分页大小
        :param error_handler:       错误处理函数
        :return:
        """
        param = {
            'symbol': symbol,
            'pageNum': page,
            'pageSize': size,
        }

        if start_time:
            param['startTime'] = start_time
        if end_time:
            param['endTime'] = end_time

        def json_parser(json_wrapper):
            return Event(**json_wrapper)

        self.subscribe(self.CH_getAllOrders, param, callback, json_parser, error_handler)

    def get_trade_list(self, callback, symbol: str, order_id: int, error_handler=None):
        """
        8.5.9、查询成交明细
        :param callback:            结果处理函数
        :param symbol:              合约，即市场交易对唯一标识符，如：BTC_USDT
        :param order_id:            订单id
        :param error_handler:       错误处理函数
        :return:
        """
        param = {
            'symbol': symbol,
            'orderId': order_id,
        }

        def json_parser(json_wrapper):
            return Event(**json_wrapper)

        self.subscribe(self.CH_getTradeList, param, callback, json_parser, error_handler)

    def get_trade_history(self, callback, symbol: str, start_time=None, end_time=None, page=1, size=10, error_handler=None):
        """
        8.5.10、查询历史成交记录
        :param callback:            结果处理函数
        :param symbol:              合约，即市场交易对唯一标识符，如：BTC_USDT
        :param start_time:          开始时间戳
        :param end_time:            结束时间戳
        :param page:                页码，从1开始
        :param size:                分页大小
        :param error_handler:       错误处理函数
        :return:
        """
        param = {
            'symbol': symbol,
            'pageNum': page,
            'pageSize': size,
        }

        if start_time:
            param['startTime'] = start_time
        if end_time:
            param['endTime'] = end_time

        def json_parser(json_wrapper):
            return Event(**json_wrapper)

        self.subscribe(self.CH_tradeHistory, param, callback, json_parser, error_handler)

    def batch_order(self, callback, orders: List[OrderRequest], error_handler=None):
        """
        8.5.10、查询历史成交记录
        :param callback:            结果处理函数
        :param orders:              订单列表
        :param error_handler:       错误处理函数
        :return:
        """
        param = {'orderDatas': json.dumps([item.__dict__ for item in orders])}

        def json_parser(json_wrapper):
            return Event(**json_wrapper)

        self.subscribe(self.CH_batchOrder, param, callback, json_parser, error_handler)

