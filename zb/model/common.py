"""
Basic Data, include symbol, currency, server time, assist price
"""
from zb.utils import Utils


class ResultModel(dict):
    """
    The base class of the response data.
    """

    def __init__(self, **kw):
        super().__init__()
        for k, v in kw.items():
            self.__setattr__(k, v)

    def __setattr__(self, name, value):
        self[str.replace(name, '-', '_')] = value

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'%s' object has no attribute '%s'" % (self.__class__.__name__, key))


class Symbol(ResultModel):
    """
    The ZBG supported symbols.

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


class Currency(ResultModel):
    """
    The ZBG supported currencies.

    :member
        id: The currency id in ZBG.
        name: Name of the currency.
        draw_flag: Whether can withdraw.
        draw_fee: Withdraw Commission.
        once_draw_limit: Maximum withdrawal limit.
        daily_draw_limit: Maximum daily withdrawal limit.
        min_draw_limit: Minimum withdrawal limit.
        """

    def __init__(self, **kwargs):
        self.id = ""
        self.name = ""
        self.draw_flag = ""
        self.once_draw_limit = 0
        self.daily_draw_limit = 0

        super().__init__(**kwargs)
        self.draw_fee = Utils.safe_float(kwargs, "draw-fee")
        self.min_draw_limit = Utils.safe_float(kwargs, "min-draw-limit")


class AssistPrice(ResultModel):
    """
    The discount price of the specified currency in usd, cny and btc.

    :member
        btc : dict, The discount price of the currencies in btc.
        cny : dict, The discount price of the currencies in cny.
        usd : dict, The discount price of the currencies in usd.
    """

    def __init__(self, **kwargs):
        self.btc = {}
        self.cny = {}
        self.usd = {}

        super().__init__(**kwargs)

    def to_btc_price(self, coin):
        try:
            return float(self.btc[coin])
        except KeyError:
            raise AttributeError(r"There is no currency [%s] price converted into BTC" % coin)

    def to_cny_price(self, coin):
        try:
            return float(self.cny[coin])
        except KeyError:
            raise AttributeError(r"There is no currency [%s] price converted into CNY" % coin)

    def to_usd_price(self, coin):
        try:
            return float(self.usd[coin])
        except KeyError:
            raise AttributeError(r"There is no currency [%s] price converted into USD" % coin)


