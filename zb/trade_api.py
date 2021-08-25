import json
from typing import List

from zb.client import ApiClient, ArgumentsRequired, OrderNotCached
from zb.model.constant import *
from zb.model.trade import *


class TradeApi(ApiClient):
    def __init__(self, api_key, secret_key, api_host=None):
        describe = {
            'apis': {
                'private': {
                    'get': {
                        'undone_orders': '/Server/api/v2/trade/getUndoneOrders',
                        'all_orders': '/Server/api/v2/trade/getAllOrders',
                        'order': '/Server/api/v2/trade/getOrder',
                        'trade_list': '/Server/api/v2/trade/getTradeList',
                        'trade_history': '/Server/api/v2/trade/tradeHistory',
                        'order_algos': '/Server/api/v2/trade/getOrderAlgos',
                    },
                    'post': {
                        'create_order': '/Server/api/v2/trade/order',
                        'batch_order': '/Server/api/v2/trade/batchOrder',
                        'cancel_order': '/Server/api/v2/trade/cancelOrder',
                        'batch_cancel_order': '/Server/api/v2/trade/batchCancelOrder',
                        'cancel_all_orders': '/Server/api/v2/trade/cancelAllOrders',
                        'order_algo': '/Server/api/v2/trade/orderAlgo',
                        'cancel_algo': '/Server/api/v2/trade/cancelAlgo',

                    },
                },
            },
            'exceptions': {
                '2012': OrderNotCached,

            }
        }

        super().__init__(api_key, secret_key, api_host, describe)

    def order(self, symbol: str, side: OrderSide, amount: float, price: float, action=Action.LIMIT, entrust_type=1, client_order_id=None) -> str:
        """
        下单

        :param symbol:          交易对，如：BTC_USDT
        :param action:          订单价格类型:  1   限价<br/>11 对手价<br/>12 最优5档<br/>3   IOC<br/>31 对手价IOC<br/>32 最优5档IOC<br/>4   只做 maker<br/>5   FOK<br/>51 对手价FOK<br/>52 最优5档FOK<br/>默认是1
        :param side:            方向：<br/>1 开多（买入）<br/>2 开空（卖出）<br/>3 平多（卖出）
        :param price:           委托价格
        :param amount:          委托数量
        :param entrust_type:    委托类型：1 限价委托，2 强平委托，3 限价止盈，4 限价止损
        :param client_order_id: 用户自定义的订单号，不可以重复出现在挂单中。必须满足正则规则 `^[a-zA-Z0-9-_]{1,36}$`
        :return: orderId
        """

        if price is None or price <= 0:
            raise ArgumentsRequired("Order price must be greater than 0.")

        if amount is None or amount <= 0:
            raise ArgumentsRequired("Order amount must be greater than 0.")
        params = {
            'symbol': symbol,
            'action': action.value,
            'price': price,
            'amount': amount,
            'side': side.value,
            'entrustType': entrust_type,
        }
        if client_order_id:
            params['clientOrderId'] = client_order_id

        return self.private_post_create_order(params)

    def batch_order(self, orders: List[OrderRequest]) -> List[BatchOrderResult]:
        """
        Send a new sell order to ZBG for matching

        :param orders: Trading pair，example：btc_usdt, eth_usdt...(zb supported [symbols])
        :return: order id
        """

        params = json.dumps([item.__dict__ for item in orders])

        result = self.private_post_batch_order(params)

        return [BatchOrderResult(**item) for item in result]

    def cancel_order(self, symbol: str, order_id=None, client_order_id=None) -> str:
        """
        5.3 撤单， order_id和client_order_id二选一

        :param symbol:          交易对，如：BTC_USDT
        :param order_id:        订单ID
        :param client_order_id: 自定义订单ID
        :return: order ID
        """
        if order_id is None and client_order_id is None:
            raise ArgumentsRequired('order_id 与 client_order_id 选填1个')

        params = {
            'symbol': symbol,
        }
        if order_id:
            params['orderId'] = order_id
        if client_order_id:
            params['clientOrderId'] = client_order_id

        return self.private_post_cancel_order(params)

    def batch_cancel_orders(self, symbol: str, order_ids=None, client_order_ids=None) -> List[BatchCancelOrderResult]:
        """
        5.4 批量撤单, order_ids和client_order_ids二选一

        :param symbol:              交易对，如：BTC_USDT
        :param order_ids:           订单ID列表
        :param client_order_ids:    自定义订单ID列表
        :return: List[BatchCancelOrderResult]
        """
        if order_ids is None and client_order_ids is None:
            raise ArgumentsRequired('order_ids 与 client_order_ids 选填1个')

        params = {
            'symbol': symbol,
        }

        if order_ids:
            params['orderIds'] = order_ids
        if client_order_ids:
            params['clientOrderIds'] = client_order_ids

        result = self.private_post_batch_cancel_order(params)

        return [BatchCancelOrderResult(**item) for item in result]

    def cancel_all_orders(self, symbol: str) -> List[BatchCancelOrderResult]:
        """
        5.3 撤单， order_id和client_order_id二选一
        若data中有数据则表示有删除失败的订单，具体数据格式参考``批量撤单接口``

        :param symbol:          交易对，如：BTC_USDT
        :return: List[BatchCancelOrderResult]
        """
        params = {
            'symbol': symbol,
        }

        result = self.private_post_cancel_all_orders(params)

        return [BatchCancelOrderResult(**item) for item in result]

    def get_undone_orders(self, symbol: str, page=1, size=30) -> List[Order]:
        """
        5.6 查询当前全部挂单，没有撮合或未完全撮合挂单

        :param symbol: 交易对，如：BTC_USDT
        :param page:   页码
        :param size:   每页行数，默认30
        :return: List[Order]
        """

        params = {
            'symbol': symbol,
            'page': page,
            'size': size,
        }

        datas = self.private_get_undone_orders(params)

        return [Order(**order) for order in datas['list']]

    def get_all_orders(self, symbol: str, start_time=None, end_time=None, page=1, size=30) -> List[Order]:
        """
        5.7 查询所有订单(包括历史订单)

        请注意，如果订单满足如下条件，不会被查询到：

            - 订单的最终状态为 `已取消` , **并且**
            - 订单没有任何的成交记录, **并且**
            - 订单生成时间 + 7天 < 当前时间

        :param symbol:      交易对，如：BTC_USDT
        :param start_time:  起始时间
        :param end_time:    结束时间
        :param page:        页码
        :param size:        每页行数，默认30
        :return: List[Order]
        """

        params = {
            'symbol': symbol,
            'page': page,
            'size': size,
        }

        if start_time:
            params['startTime'] = start_time
        if end_time:
            params['endTime'] = end_time

        data = self.private_get_all_orders(params)

        return [Order(**order) for order in data['list']]

    def get_order(self, symbol: str, order_id=None, client_order_id=None) -> Order:
        """
        5.8 订单信息, order_ids和client_order_ids二选一

        :param symbol:             交易对，如：BTC_USDT
        :param order_id:           订单ID列表
        :param client_order_id:    自定义订单ID列表
        :return: Order
        """

        if order_id is None and client_order_id is None:
            raise ArgumentsRequired('order_id 与 client_order_id 选填1个')

        params = {
            'symbol': symbol,
        }
        if order_id:
            params['orderId'] = order_id
        if client_order_id:
            params['clientOrderId'] = client_order_id

        order = self.private_get_order(params)

        return Order(**order)

    def get_trade_list(self, symbol: str, order_id: int, page=1, size=30) -> List[Trade]:
        """
        5.9 订单成交明细

        :param symbol:      交易对，如：BTC_USDT
        :param order_id:    订单ID
        :param page:        页码
        :param size:        每页行数，默认30
        :return: List[Trade]
        """

        params = {
            'symbol': symbol,
            'orderId': order_id,
            'pageNum': page,
            'pageSize': size,
        }

        data = self.private_get_trade_list(params)

        return [Trade(**trade) for trade in data['list']]

    def order_algo(self, symbol: str, side: int, order_type: int, amount: float,
                   trigger_price=None, algo_price=None, price_type=None, biz_type=None) -> str:
        """
       5.11 委托策略下单

        :param symbol:          交易对，如：BTC_USDT
        :param side:           `1`:开多(计划委托)<br/>`2`:开空(计划委托)<br/>`3`:平多(止盈止损)<br/>`4`:平空(止盈止损)
        :param order_type:    ` 1`：计划委托<br/>`2`：止盈止损
        :param amount:          数量
        :param trigger_price:   触发价格，填写值0<X<=1000000
        :param algo_price:      委托价格，填写值0<X<=1000000
        :param price_type:      1:标记价格<br/> 2:最新价格
        :param biz_type:        1:止盈<br/> 2:止损
        :return: String algoId
        """

        params = {
            'symbol': symbol,
            'side': side,
            'amount': amount,
            'orderType': order_type,
        }
        if trigger_price:
            params['triggerPrice'] = trigger_price
        if algo_price:
            params['algoPrice'] = algo_price
        if price_type:
            params['priceType'] = price_type
        if biz_type:
            params['bizType'] = biz_type

        return self.private_post_order_algo(params)

    def cancel_algos(self, symbol: str, ids: list) -> List[BatchCancelOrderResult]:
        """
        5.12 委托策略撤单

        :param symbol:        交易对，如：BTC_USDT
        :param ids:           订单ID列表
        :return: List[BatchCancelOrderResult]
        """

        params = {
            'symbol': symbol,
            'ids': ids,
        }

        result = self.private_post_cancel_algos(params)

        return [BatchCancelOrderResult(**item) for item in result]

    def get_order_algos(self, symbol: str, side=None, order_type=None, biz_type=None,
                        status=None, start_time=None, end_time=None, page=1, size=30) -> List[Trade]:
        """
        5.13 委托策略查询
        :param symbol:     交易对，如：BTC_USDT
        :param side:       `1`:开多(计划委托)<br/>`2`:开空(计划委托)<br/>`3`:平多(止盈止损)<br/>`4`:平空(止盈止损)
        :param order_type: `1`：计划委托<br/>`2`：止盈止损
        :param biz_type:    针对止盈止损<br/>`1`:止盈<br/>`2`:止损
        :param status:      针对计划委托：
                                `1`:等待委托<br/>`2`:已取消<br/>`3`:已委托<br/>`4`:委托失败<br/>`5`已完成<br/>
                             针对止盈止损：
                                `1`:未触发<br/>`2`:已取消<br/>`3`:触发成功<br/>`4`:触发失败<br/>`5`已完成
        :param start_time:  开始时间戳
        :param end_time:    结束时间戳
        :param page:        页码
        :param size:        每页行数，默认30
        :return:
        """

        self.check_symbol(symbol)
        params = {
            'symbol': symbol,
            'pageNum': page,
            'pageSize': size,
        }
        if side:
            params['side'] = side
        if order_type:
            params['orderType'] = order_type
        if status:
            params['status'] = status
        if biz_type:
            params['bizType'] = biz_type
        if start_time:
            params['startTime'] = start_time
        if end_time:
            params['endTime'] = end_time
        data = self.private_get_order_algos(params)

        return [Trade(**trade) for trade in data]
