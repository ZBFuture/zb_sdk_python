from zb.model.common import ResultModel
from zb.model.constant import Action
from zb.utils import Utils
from json import dumps


class OrderRequest(dict):
    def __init__(self, **kwargs):
        self.clientOrderId = ''
        super().__init__(**kwargs)
        self.symbol = Utils.safe_string(kwargs, 'symbol')
        self.action = Utils.safe_integer(kwargs, 'action', Action.LIMIT.value)
        self.side = Utils.safe_integer(kwargs, 'side')
        self.price = Utils.safe_float(kwargs, 'price', None)
        self.amount = Utils.safe_float(kwargs, 'amount')
        self.entrustType = Utils.safe_integer(kwargs, 'entrustType', 1)



class BatchOrderResult(ResultModel):
    """
    | 名称          | 类型   | 是否必须 | 描述                                 |
    | :------------ | :----- | :------- | :----------------------------------- |
    | sCode         | Int    | 是       | 结果的code，1代表成功                |
    | sMsg          | String | 是       | 结果描述                             |
    | orderId       | String | 否       | 订单ID                               |
    | clientOrderId | String | 否       | 自定义订单ID，如空缺系统会自动赋值。 |
    """

    def __init__(self, **kwargs):
        self.sMsg = ''
        self.orderId = ''
        self.clientOrderId = ''
        super().__init__(**kwargs)
        self.sCode = Utils.safe_integer(kwargs, "sCode")

    def is_success(self):
        return self.sCode == 1


class BatchCancelOrderResult(ResultModel):
    """
    | 名称          | 类型   | 是否必须 | 描述                                 |
    | :------------ | :----- | :------- | :----------------------------------- |
    | sCode         | Int    | 是       | 结果的code，1代表成功                |
    | sMsg          | String | 是       | 结果描述                             |
    | orderId       | String | 否       | 订单ID                               |
    | clientOrderId | String | 否       | 自定义订单ID，如空缺系统会自动赋值。 |
    """

    def __init__(self, **kwargs):
        self.cnDesc = ''
        self.desc = ''
        self.code = ''
        super().__init__(**kwargs)
        self.orderId = Utils.safe_integer(kwargs, "data")

    def is_success(self):
        return self.sCode == 1


class Order(ResultModel):
    """
    Order data

    :member
        | 参数名          | 必选 | 类型       | 说明                                                         |
        | :-------------- | :--- | :--------- | :----------------------------------------------------------- |
        | id              | 是   | long     | 订单id                                                       |
        | orderCode       | 是   | String     | 自定义订单ID                                                 |
        | marketId        | 是   | Long       | 市场id                                                       |
        | price           | 是   | Decimal    | 委托价格                                                     |
        | amount          | 是   | Decimal    | 委托数量                                                     |
        | value           | 否   | Decimal    | 委托价值，即委托价格 * 委托数量                              |
        | availableAmount | 否   | Decimal    | 可用委托数量                                                 |
        | availableValue  | 是   | Decimal    | 可用委托价值                                                 |
        | tradeAmount     | 是   | Decimal    | 成交完成量, 每次成交都会增加                                 |
        | tradeValue      | 是   | Decimal    | 成交完成价值, 每次成交都会增加                               |
        | type            | 是   | Integer    | 委托类型: -1 卖, 1 买                                        |
        | action          | 是   | Integer    | 订单价格类型:   1   限价 11 对手价 12 最优5档 3   IOC 31 对手价IOC 32 最优5档IOC 4   只做 maker 5   FOK 51 对手价FOK 52 最优5档FOK |
        | showStatus      | 是   | Integer    | 状态: 1:未成交、2:部分成交（订单还在挂单中）、3:已完成、4：取消中、5:完全取消、6：取消失败、7：部分取消（订单已完成，部分成交） |
        | entrustType     | 是   | Integer    | 委托类型：1限价委托，2强制减仓，3强制平仓，4计划委托，5止盈，6止损 |
        | side            | 是   | Integer    | 方向：1开多（买入），2开空（卖出），3平多（卖出），4平空（买入） |
        | sourceType      | 是   | Integer    | 来源： 1:WEB 2:Android 3:iOS 4:Rest API 5:WebSocket API 6:System 7:Plan Entrust(计划委托) 8:Take Profit(止盈止损) 9:Take Profit(止损) |
        | leverage        | 是   | Integer    | 杠杠倍数                                                     |
        | avgPrice        | 是   | BigDecimal | 成交均价                                                     |
        | canCancel       | 是   | Boolean    | 能否取消                                                     |
        | createTime      | 是   | Long       | 下单时间，时间戳                                             |
        | margin          | 是   | Decimal    | 保证金                                                       |
    """

    def __init__(self, **kwargs):
        self.canCancel = True

        super().__init__(**kwargs)
        self.id = Utils.safe_string(kwargs, "id")
        self.clientOrderId = Utils.safe_string(kwargs, "orderCode")
        self.marketId = Utils.safe_integer(kwargs, "marketId")
        self.price = Utils.safe_float(kwargs, 'price')
        self.amount = Utils.safe_float(kwargs, 'amount')
        self.value = Utils.safe_float(kwargs, 'value', 0)
        self.availableAmount = Utils.safe_float(kwargs, 'availableAmount', 0)
        self.availableValue = Utils.safe_float(kwargs, 'availableValue', 0)
        self.tradeAmount = Utils.safe_float(kwargs, 'tradeAmount', 0)
        self.tradeValue = Utils.safe_float(kwargs, 'tradeValue', 0)
        self.type = Utils.safe_integer(kwargs, 'type')
        self.action = Utils.safe_integer(kwargs, 'action')
        self.showStatus = Utils.safe_integer(kwargs, 'showStatus')
        self.entrustType = Utils.safe_integer(kwargs, 'entrustType')
        self.side = Utils.safe_integer(kwargs, 'side')
        self.sourceType = Utils.safe_integer(kwargs, 'sourceType')
        self.leverage = Utils.safe_integer(kwargs, 'leverage')
        self.avgPrice = Utils.safe_float(kwargs, 'avgPrice')
        self.margin = Utils.safe_float(kwargs, 'margin')
        self.createTime = Utils.safe_integer(kwargs, 'createTime')

class Trade(ResultModel):
    """
    Trade data

    :member
        | 参数名      | 必选 | 类型    | 说明                                                         |
        | :---------- | :--- | :------ | :----------------------------------------------------------- |
        | orderId     | 是   | Long    | 订单id                                                       |
        | price       | 是   | Decimal | 成交价格                                                     |
        | amount      | 是   | Decimal | 成交数量                                                     |
        | feeAmount   | 是   | Decimal | 手续费                                                       |
        | feeCurrency | 是   | String  | 手续费币种                                                   |
        | relizedPnl  | 是   | Decimal | 已实现盈亏                                                   |
        | side        | 是   | Integer | 向：1开多（买入），2开空（卖出），3平多（卖出），4平空（买入） |
        | maker       | 是   | Boolean | 是否maker,否则为taker                                        |
        | createTime  | 是   | Long    | 成交时间戳                                                   |
    """

    def __init__(self, **kwargs):
        self.feeCurrency = ''
        self.maker = False

        super().__init__(**kwargs)

        self.price = Utils.safe_float(kwargs, 'price')
        self.amount = Utils.safe_float(kwargs, 'amount', 0)
        self.feeAmount = Utils.safe_float(kwargs, 'feeAmount', 0)
        self.relizedPnl = Utils.safe_float(kwargs, 'relizedPnl', 0)
        self.side = Utils.safe_integer(kwargs, 'side')
        self.createTime = Utils.safe_integer(kwargs, 'createTime')

class OrderAlgos(ResultModel):
    """
    Trade data

    :member
        | 参数名       | 必选 | 类型    | 说明                                                         |
        | :----------- | :--- | :------ | :----------------------------------------------------------- |
        | id           | 是   | Long    | 订单id                                                       |
        | marketId     | 是   | Long    | 市场id                                                       |
        | triggerPrice | 是   | Decimal | 触发价格                                                     |
        | algoPrice    | 是   | Decimal | 委托价格                                                     |
        | amount       | 是   | Decimal | 委托数量                                                     |
        | side         | 是   | Integer | `1`:开多(计划委托) `2`:开空(计划委托) `3`:平多(止盈止损) `4`:平空(止盈止损) |
        | orderType    | 是   | Integer | `1`：计划委托 `2`：止盈止损                              |
        | priceType    | 是   | Integer | `1`:标记价格 `2`:最新价格                                |
        | algoPrice    | 是   | Decimal | 委托价格，填写值0\<X\<=1000000                               |
        | bizType      | 是   | Integer | `1`:止盈 `2`:止损                                        |
        | leverage     | 是   | Integer | 杠杠倍数                                                     |
        | sourceType   | 是   | Integer | 来源： 1:WEB 2:Android 3:iOS 4:Rest API 5:WebSocket API 6:System 7:Plan Entrust(计划委托) 8:Take Profit(止盈止损) 9:Take Profit(止损) |
        | canCancel    | 是   | Boolean | 能否取消                                                     |
        | triggerTime  | 否   | Long    | 触发时间，时间戳                                             |
        | tradedAmount | 否   | Decimal | 已成交数量                                                   |
        | errorDesc    | 否   | String  | 触发后下单时出现的错误信息                                   |
        | createTime   | 是   | Long    | 创建时间，时间戳                                             |
        | status       | 是   | Integer | **针对计划委托** `1`:等待委托 `2`:已取消 `3`:已委托 `4`:委托失败 `5`已完成 **针对止盈止损** `1`:未触发 `2`:已取消 `3`:触发成功 `4`:触发失败 `5`已完成 |
    """

    def __init__(self, **kwargs):
        self.feeCurrency = ''
        self.maker = False
        self.createTime = 0

        super().__init__(**kwargs)

        self.price = Utils.safe_float(kwargs, 'price')
        self.amount = Utils.safe_float(kwargs, 'amount', 0)
        self.feeAmount = Utils.safe_float(kwargs, 'feeAmount', 0)
        self.relizedPnl = Utils.safe_float(kwargs, 'relizedPnl', 0)
        self.side = Utils.safe_integer(kwargs, 'side', 0)