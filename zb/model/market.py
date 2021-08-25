"""
Market Data
"""
from datetime import datetime

from zb.model.common import ResultModel
from zb.utils import Utils


class Market(ResultModel):
    """
    :member
        | 名称                 | 类型       | 示例 | 描述                                                         |
        | :------------------- | :--------- | :--- | :----------------------------------------------------------- |
        | id                   | Long       |      | 市场ID                                                       |
        | marketName           | String     |      | 市场名称                                                     |
        | symbol               | String     |      | 唯一标识                                                     |
        | buyerCurrencyId      | Long       |      | 买方币种ID                                                   |
        | buyerCurrencyName    | String     |      | 买方币种名称                                                 |
        | sellerCurrencyId     | Long       |      | 卖方币种ID                                                   |
        | sellerCurrencyName   | String     |      | 卖方币种名称                                                 |
        | marginCurrencyId     | Long       |      | 保证金币种ID                                                 |
        | marginCurrencyName   | String     |      | 保证金币种                                                   |
        | amountDecimal        | Integer    |      | 数量精度                                                     |
        | priceDecimal         | Integer    |      | 价格精度                                                     |
        | feeDecimal           | Integer    |      | 手续费精度                                                   |
        | marginDecimal        | Integer    |      | 保证金精度                                                   |
        | minAmount            | BigDecimal |      | 最小委托量                                                   |
        | maxAmount            | BigDecimal |      | 最大委托量                                                   |
        | minTradeMoney        | BigDecimal |      | 最小交易额                                                   |
        | maxTradeMoney        | BigDecimal |      | 最大交易额                                                   |
        | minFundingRate       | BigDecimal |      | 最小资金费率                                                 |
        | maxFundingRate       | BigDecimal |      | 最大资金费率                                                 |
        | maxLeverage          | Integer    |      | 最大杠杆倍数                                                 |
        | riskWarnRatio        | BigDecimal |      | 风险提醒比例                                                 |
        | defaultFeeRate       | BigDecimal |      | 默认费率                                                     |
        | contractType         | Integer    |      | 合约类型，1:usdt合约（默认），<br/>2:币本位合约              |
        | duration             | Integer    |      | 合约时长，<br/>1:永续合约（默认），<br/>2:交割合约-当周，<br/>3:交割合约-次周，<br/>4:交割合约-当季，<br/>5:交割合约-次季 |
        | status               | Integer    |      | 状态: 1:运行, 0:停止（默认）                                 |
        | createTime           | Long       |      | 创建时间                                                     |
        | enableTime           | Long       |      | 开盘时间                                                     |
        | defaultLeverage      | Integer    |      | 默认杠杆倍数                                                 |
        | defaultMarginMode    | Integer    |      | 默认保证金模式，<br/>1:逐仓（默认），<br/>2:全仓             |
        | defaultPositionsMode | Integer    |      | 默认仓位模式，<br/>1:单向持仓，<br/>2:双向持仓（默认）       |
        """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Depth(ResultModel):
    """
    The price depth information.

    :member
        timestamp: Second unix timestamp
        bids: The list of the bid depth. The content is DepthEntry class.
        asks: The list of the ask depth. The content is DepthEntry class.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.asks = [DepthEntry(item[0], item[1]) for item in kwargs['asks']]
        self.bids = [DepthEntry(item[0], item[1]) for item in kwargs['bids']]


class DepthEntry(ResultModel):
    """
    An depth entry consisting of price and amount.
    :member
        price: The price of the depth.
        amount: The amount of the depth.
    """

    def __init__(self, price, amount):
        super().__init__()

        self.price = float(price)
        self.amount = float(amount)


class Kline(ResultModel):
    """
    The candlestick/kline data.

    :member
        timestamp : keep the original timestamp, second
        high: The high price.
        low: The low price.
        open: The opening price.
        close: The closing price.
        volume: The trading volume in base currency.
    """

    def __init__(self, **kwargs):
        self.high = 0.0
        self.open = 0.0
        self.low = 0.0
        self.close = 0.0
        self.volume = 0.0
        self.timestamp = 0

        super().__init__(**kwargs)

    @staticmethod
    def json_parse(json_array):
        data_obj = Kline()
        data_obj.open = Utils.safe_float(json_array, 0)
        data_obj.high = Utils.safe_float(json_array, 1)
        data_obj.low = Utils.safe_float(json_array, 2)
        data_obj.close = Utils.safe_float(json_array, 3)
        if len(json_array) == 6:
            data_obj.volume = Utils.safe_float(json_array, 4)
            data_obj.timestamp = Utils.safe_integer(json_array, 5)
        else:
            data_obj.timestamp = Utils.safe_integer(json_array, 4)
        return data_obj

    def trade_time(self):
        """
        Format the trade timestamp as 'yyyy-MM-dd HH:mm:ss'
        :return: time string
        """
        if self.timestamp:
            return datetime.fromtimestamp(self.timestamp)


class Trade(ResultModel):
    """
    The trade information with price and amount etc.

    :member
        price: The trading price in quote currency.
        amount: The trading volume in base currency.
        timestamp: The UNIX formatted timestamp generated by server in UTC.
        side: The direction of the taker trade: 'buy' or 'sell'.
    """

    def __init__(self, **kwargs):
        self.price = 0.0
        self.amount = 0.0
        self.timestamp = 0
        self.side = None

        super().__init__(**kwargs)

    @staticmethod
    def json_parse(json_array):
        trade = Trade()
        trade.price = Utils.safe_float(json_array, 0)
        trade.amount = Utils.safe_float(json_array, 1)
        trade.side = 'buy' if Utils.safe_integer(json_array, 2) == 1 else 'sell'
        trade.timestamp = Utils.safe_integer(json_array, 3)
        return trade

    def trade_time(self):
        """
        Format the trade timestamp as 'yyyy-MM-dd HH:mm:ss'
        :return: time string
        """
        if self.timestamp:
            return datetime.fromtimestamp(self.timestamp)

class Ticker(ResultModel):
    """
    Latest Aggregated Ticker.

    :member
        open:       开盘价格
        high:       最高价
        low:        最低价
        close:      最新成交价
        volume:     成交量(最近的24小时)
        rate:       24H涨跌幅
        timestamp:  秒级别时间戳.
        closeCny:  以rmb为单位的最新成交价格.
    """

    def __init__(self, **kwargs):
        self.open = 0.0
        self.high = 0.0
        self.low = 0.0
        self.close = 0.0
        self.volume = 0.0
        self.rate = 0.0
        self.timestamp = 0
        self.closeCny = 0.0

        super().__init__(**kwargs)

    @staticmethod
    def json_parse(json_array):
        data_obj = Ticker()
        data_obj.open = Utils.safe_float(json_array, 0)
        data_obj.high = Utils.safe_float(json_array, 1)
        data_obj.low = Utils.safe_float(json_array, 2)
        data_obj.close = Utils.safe_float(json_array, 3)
        data_obj.volume = Utils.safe_float(json_array, 4)
        data_obj.rate = Utils.safe_float(json_array, 5)
        data_obj.timestamp = Utils.safe_integer(json_array, 6)
        if len(json_array) == 8:
            data_obj.closeCny = Utils.safe_float(json_array, 7)
        return data_obj

    def trade_time(self):
        """
        Format the trade timestamp as 'yyyy-MM-dd HH:mm:ss'
        :return: time string
        """
        if self.timestamp:
            return datetime.fromtimestamp(self.timestamp)

class HistoricalTrade(ResultModel):
    """
    The historical trade information .

    :member
        trade_id: The unique trade id.
        price: The trading price in quote currency.
        amount: The trading volume in base currency.
        total: The trading volume in quote currency.
        side: The direction of the taker trade: 'buy' or 'sell'.
        created_at: The UNIX formatted timestamp generated by server in UTC.
        date: The trade time. format: 'yyyy-MM-dd HH:mm:ss'.
    """

    def __init__(self, **kwargs):
        self.trade_id = ''
        self.price = 0.0
        self.amount = 0.0
        self.total = 0.0
        self.side = ''
        self.created_at = 0
        self.date = ''

        super().__init__(**kwargs)
