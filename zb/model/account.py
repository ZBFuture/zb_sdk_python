"""
Account data
"""
from zb.model.common import ResultModel
from zb.utils import Utils


class Account(ResultModel):
    """
    合约账户信息，包括账号信息和资产列表

    :member
        account:    AccountInfo	    账户信息，包括可用余额、保证金余额、未实现盈亏
        assets:	    list	        资产信息列表，包括可用、冻结

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 账户信息，包括可用余额、保证金余额、未实现盈亏
        self.account = AccountInfo(**kwargs['account'])
        # 资产信息，包括可用、冻结
        self.assets = [Asset(**asset) for asset in kwargs['assets']]


class AccountInfo(ResultModel):
    """
    账户信息，包括可用余额、保证金余额、未实现盈亏

    :member
        accountBalance:	        float	    账户余额：可用+冻结+所以仓位未实现盈亏
        allMargin:	            float	    所有仓位保证金
        available:	            float	    可用资产量
        freeze:	                float	    冻结资产量
        allUnrealizedPnl:	    float	    所有对应仓位的累积未实现盈亏
        accountBalanceConvert:	float	    账户余额折合
        allMarginConvert:	    float	    所有仓位保证金折合
        availableConvert:	    float	    可用资产折合
        freezeConvert:	        float	    冻结资产折合
        allUnrealizedPnlConvert:float	    所有对应仓位的累积未实现盈亏折合
        convertUnit:	        string	    折合单位，页面显示上"≈"号后面的数字单位，如：cny，usd,btc
        unit:	                string	    固定返回，如果是u本位，返回usdt，如果是币本位返回btc，如果是qc合约返回qc，统计数据的单位
        percent:	            string	    未实现盈亏/所有仓位保证金*100%

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.accountBalance = Utils.safe_float(kwargs, "accountBalance")
        self.allMargin = Utils.safe_float(kwargs, "allMargin")
        self.available = Utils.safe_float(kwargs, "available")
        self.freeze = Utils.safe_float(kwargs, "freeze")
        self.allUnrealizedPnl = Utils.safe_float(kwargs, "allUnrealizedPnl")
        self.accountBalanceConvert = Utils.safe_float(kwargs, "accountBalanceConvert")
        self.allMarginConvert = Utils.safe_float(kwargs, "allMarginConvert")
        self.availableConvert = Utils.safe_float(kwargs, "availableConvert")
        self.freezeConvert = Utils.safe_float(kwargs, "freezeConvert")
        self.allUnrealizedPnlConvert = Utils.safe_float(kwargs, "allUnrealizedPnlConvert")
        self.convertUnit = Utils.safe_string(kwargs, "convertUnit")
        self.unit = Utils.safe_string(kwargs, "unit")
        self.percent = Utils.safe_string(kwargs, "percent")


class Asset(ResultModel):
    def __init__(self, **kwargs):
        """
        {
         "currencyId": 11,
         "amount": 12.2,
         "freezeAmount": 1,
         "id": 6740243890479048704,
         "accountBalance": 1212.12,
         "allUnrealizedPnl": -112.12,
         "allMargin": 1212.12,
         "createTime": 1606999371166,
         "modifyTime": 1607003956239,
         "extend": null
         }
        """
        self.extend = None
        self.currencyName = ''
        super().__init__(**kwargs)

        self.id = Utils.safe_integer(kwargs, "id")
        self.userId = Utils.safe_integer(kwargs, "userId")
        self.currencyId = Utils.safe_integer(kwargs, "currencyId")
        self.createTime = Utils.safe_integer(kwargs, "createTime")
        self.modifyTime = Utils.safe_integer(kwargs, "modifyTime")
        self.amount = Utils.safe_float(kwargs, "amount", 0)
        self.freezeAmount = Utils.safe_float(kwargs, "freezeAmount", 0)
        self.accountBalance = Utils.safe_float(kwargs, "accountBalance", 0)
        self.allUnrealizedPnl = Utils.safe_float(kwargs, "allUnrealizedPnl", 0)
        self.allMargin = Utils.safe_float(kwargs, "allMargin", 0)


class Positions(ResultModel):
    """
    合约持仓
    :member
        | 参数名           | 必选 | 类型       | 说明                                             |
        | :-------------   | :--- | :--------- | :---------------                                 |
        | userId           | 是   | Long       | 用户id                                           |
        | marketId         | 是   | Long       | 市场id                                           |
        | marketName       | 是   | String     | 市场名称                                         |
        | side             | 是   | Integer    | 开仓方向,开多：1 开空：0                         |
        | leverage         | 否   | Integer    | 杠杆倍数                                         |
        | amount           | 否   | BigDecimal | 持有仓位数量                                     |
        | freezeAmount     | 是   | BigDecimal | 下单冻结仓位数量                                 |
        | avgPrice         | 是   | BigDecimal | 开仓均价                                         |
        | liquidatePrice   | 是   | BigDecimal | 强平价格                                         |
        | margin           | 是   | BigDecimal | 保证金                                           |
        | marginMode       | 是   | Integer    | 保证金模式：1逐仓（默认），2全仓                 |
        | positionsMode    | 是   | Integer    | 1:单向持仓，2: 双向持仓                          |
        | status           | 是   | Integer    | 状态: 1 可用、2:锁定、3:冻结、4：不显示          |
        | unrealizedPnl    | 否   | BigDecimal | 未实现盈亏                                       |
        | marginBalance    | 是   | BigDecimal | 保证金余额                                       |
        | maintainMargin   | 是   | BigDecimal | 维持保证金                                       |
        | marginRate       | 是   | BigDecimal | 保证金率                                         |
        | nominalValue     | 是   | BigDecimal | 头寸的名义价值                                   |
        | liquidateLevel   | 是   | Integer    | 强平档位，即头寸对应的维持保证金档位             |
        | autoLightenRatio | 是   | BigDecimal | 自动减仓比例，范围0～1，数字越大自动减仓风险越高 |
        | returnRate       | 是   | BigDecimal | 回报率                                           |
        | id               | 是   | Long       | 仓位id                                           |
        | createTime       | 是   | Long       | 创建时间                                         |
        | modifyTime       | 是   | Long       | 修改时间                                         |
        | extend           | 否   | String       | 备用字段                                         |
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class MarginInfo(ResultModel):
    """
    保证金信息查询
    :member
        | 参数名         | 必选 | 类型       | 说明             |
        | :------------- | :--- | :--------- | :--------------- |
        | maxAdd         | 是   | BigDecimal | 最大可增加保证金 |
        | maxSub         | 是   | BigDecimal | 最大可减少保证金 |
        | liquidatePrice | 是   | BigDecimal | 预估强平价格     |
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.maxAdd = Utils.safe_float(kwargs, 'maxAdd')
        self.maxSub = Utils.safe_float(kwargs, 'maxSub')
        self.liquidatePrice = Utils.safe_float(kwargs, 'liquidatePrice')


class PositionsSettingResult(ResultModel):
    """
    保证金信息查询
    :member
        | 参数名           | 必选 | 类型       | 说明                                                    |
        | :--------------- | :--- | :--------- | :------------------------------------------------------ |
        | userId           | 是   | Long       | 用户id                                                  |
        | marketId         | 是   | Long       | 市场id                                                  |
        | leverage         | 是   | BigDecimal | 杠杠倍数                                                |
        | marginMode       | 是   | Integer    | 保证金模式：1逐仓（默认），2全仓                        |
        | positionsMode    | 否   | Integer    | 1:单向持仓，2: 双向持仓                                 |
        | id               | 否   | Long       | 仓位id                                                  |
        | maxAppendAmount  | 是   | BigDecimal | 最多追加保证金，可能被修改，如果为0会关闭自动增加保证金 |
        | enableAutoAppend | 是   | Integer    | 是否开启自动追加保证金 1:开启  0 ：不开启               |
        | marginCoins      | 是   | String     | 配置的按顺序冻结的保证金，如 eth,usdt,qc                |
        | createTime       | 否   | Long       | 创建时间                                                |
        | modifyTime       | 是   | Long       | 更新时间                                                |
        | extend           | 是   | String     | 备用字段                                                |
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class NominalValueResult(ResultModel):
    """
    :member
        | 参数名                     | 必选 | 类型       | 说明                                      |
        | :------------------------- | :--- | :--------- | :---------------------------------------- |
        | marketId                   | 是   | Long       | 市场id                                    |
        | side                       | 是   | Long       | 1:多仓 0：空仓                            |
        | nominalValue               | 否   | BigDecimal | 用户仓位头寸名义价值 （传side时返回）     |
        | openOrderNominalValue      | 否   | BigDecimal | 委托单头寸名义价值（传side时返回）        |
        | longNominalValue           | 否   | BigDecimal | 用户多仓位头寸名义价值 （传side时返回）   |
        | shortNominalValue          | 否   | BigDecimal | 用户空仓位头寸名义价值 （传side时返回）   |
        | openOrderLongNominalValue  | 否   | BigDecimal | 委托单多仓头寸名义价值 （不传side时返回） |
        | openOrderShortNominalValue | 否   | BigDecimal | 委托单空仓头寸名义价值 （不传side时返回） |
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class BillResult(ResultModel):
    """
    The currency deposit address in zb.

    :member
        | 参数名             | 必选 | 类型       | 说明               |
        | :----------------- | :--- | :--------- | :----------------- |
        | userId             | 是   | Long       | 用户id             |
        | freezeId           | 是   | String     | 冻结id             |
        | type               | 是   | Integer    | 账单类型           |
        | changeAmount       | 是   | BigDecimal | 变更资金量         |
        | feeRate            | 否   | BigDecimal | 费率               |
        | fee                | 否   | BigDecimal | 手续费             |
        | operatorId         | 否   | Long       | 操作者id           |
        | beforeAmount       | 是   | BigDecimal | 变更前账户资金     |
        | beforeFreezeAmount | 是   | BigDecimal | 变更前冻结资金     |
        | marketId           | 否   | Long       | 市场id             |
        | outsideId          | 否   | Long       | 外部幂等id         |
        | id                 | 否   | Long       | 账单id             |
        | isIn               | 否   | Integer    | 1：增加  0： 减少  |
        | available          | 否   | BigDecimal | 当前可用资产       |
        | unit               | 否   | String     | 币种名称，数量单位 |
        | createTime         | 否   | Long       | 创建时间戳         |
        | modifyTime         | 否   | Long       | 更新时间戳         |
        | extend             | 否   | String     | 备用字段           |
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class BillTypeResult(ResultModel):
    """

    :member
        | 参数名 | 必选 | 类型    | 说明             |
        | :----- | :--- | :------ | :--------------- |
        | code   | 是   | Integer | 账单类型         |
        | cnDesc | 是   | String  | 账单类型中文描述 |
        | enDesc | 是   | String  | 账单类型英文描述 |
    """

    def __init__(self, **kwargs):
        self.cnDesc = ''
        self.enDesc = ''

        super().__init__(**kwargs)

        self.code = Utils.safe_integer(kwargs, 'code')


class MarginHistoryResult(ResultModel):
    """

    :member
        | 参数名       | 必选 | 类型       | 说明                                                         |
        | :----------- | :--- | :--------- | :----------------------------------------------------------- |
        | symbol       | 是   | String     | 市场，如ETH_USDT                                             |
        | asset        | 是   | String     | 保证金币种，可能1个或者多个，如 USDT,ETH                     |
        | amount       | 是   | String     | 保证金数量，可能多个，如 USDT:121210.00001, ETH:0.0002       |
        | type         | 是   | Integer    | 调整方向 1: 增加逐仓保证金，0: 减少逐仓保证金                |
        | isAuto       | 否   | Integer    | 是否自动，默认否 0，1为是                                    |
        | contractType | 否   | Long       | 合约类型                                                     |
        | positionSide | 是   | String | 持仓方向:LONG SHORT BOTH   如果单向持仓就是LONG/SHORT   双向持仓：BOTH |
        | createTime   | 是   | Integer    | 创建时间                                                     |
    """

    def __init__(self, **kwargs):
        self.id = ''
        self.currency = ''
        self.address = ''
        self.remark = ''

        super().__init__(**kwargs)


class BalanceResult(ResultModel):
    """

    :member
        | 参数名           | 必选 | 类型       | 说明           |
        | :--------------- | :--- | :--------- | :------------- |
        | userId           | 是   | Long       | 用户id         |
        | currencyId       | 是   | Long       | 币种id         |
        | currencyName     | 是   | String     | 币种名字       |
        | amount           | 是   | BigDecimal | 可用资产量     |
        | freezeAmount     | 是   | BigDecimal | 冻结量         |
        | id               | 否   | Long       | 资金id         |
        | accountBalance   | 否   | BigDecimal | 账户余额       |
        | allUnrealizedPnl | 否   | BigDecimal | 账户未实现盈亏 |
        | allMargin        | 否   | BigDecimal | 账户保证金     |
        | createTime       | 否   | Long       | 创建时间       |
    """

    def __init__(self, **kwargs):
        self.currencyName = ''
        self.address = ''
        self.tx_hash = ''
        self.state = ''
        self.fee = ''
        self.created_at = 0
        self.audited_at = 0

        super().__init__(**kwargs)

        self.amount = Utils.safe_float(kwargs, 'amount')
