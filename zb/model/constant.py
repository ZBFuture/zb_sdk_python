from enum import Enum


class FuturesAccountType(Enum):
    BASE_USDT = 1  # U本位
    BASE_QC = 2  # QC本位
    BASE_COIN = 3  # 币本位


class PositionsMode(Enum):
    OneDirection = 1  # 单向
    BiDirection = 2  # 双向


class MarginMode(Enum):
    Isolated = 1  # 逐仓
    Cross = 2  # 全仓


class Action(Enum):
    # 1 限价, 2 市价, 3 IOC, 4 只做 maker, 5 FOK
    LIMIT = 1  # 限价
    OPPONENT = 11  # 对手价
    OPTIMAL_5 = 12  # 最优5档

    MARKET = 2  # 市价

    IOC = 3  # IOC
    OPPONENT_IOC = 31  # 对手价IOC
    OPTIMAL_5_IOC = 32  # 最优5档IOC

    ONLY_MAKER = 4  # 只做maker

    FOK = 5  # FOK
    OPPONENT_FOK = 51  # 对手价FOK
    OPTIMAL_5_FOK = 52  # 最优5档FOK", true);


class Interval(Enum):
    MIN_1 = "1M"
    MIN_5 = "5M"
    MIN_15 = "15M"
    MIN_30 = "30M"
    HOUR_1 = "1H"
    HOUR_6 = "6H"
    DAY_1 = "1D"
    DAY_5 = "5D"


class OrderSide(Enum):
    # 双向持仓
    # 1开多（买入），
    # 2开空（卖出），
    # 3平多（卖出），
    # 4平空（买入）
    SIDE_OPEN_LONG = 1
    SIDE_OPEN_SHORT = 2
    SIDE_CLOSE_LONG = 3
    SIDE_CLOSE_SHORT = 4

    # 单向持仓
    # 5 买入
    # 6 卖出
    # 0 仅平仓
    SIDE_ONE_WAY_BUY = 5
    SIDE_ONE_WAY_SELL = 6
    SIDE_ONE_WAY_ONLY_CLOSE = 0


class OrderState(Enum):
    """
    order status，include：
    partial-filled: portion deal,
    partial-canceled: portion deal withdrawal,
    filled: complete deal,
    canceled: cancel，
    created: created (in storage)
    """
    PARTIAL_FILLED = 'partial-filled'
    PARTIAL_CANCELED = 'partial-canceled'
    FILLED = 'filled'
    CANCELED = 'canceled'
    CREATED = 'created'
    INVALID = None


class TransferType(Enum):
    """
    master-transfer-in:sub account transfer to main account currency
    master-transfer-out :main account transfer to sub account
    """
    MASTER_TRANSFER_IN = "master-transfer-in"
    MASTER_TRANSFER_OUT = "master-transfer-out"


class Direct(Enum):
    PREV = 'prev'
    NEXT = 'next'


class DepositType(Enum):
    """
    blockchain:	Blockchain roll-in
    system: 	system deposit
    recharge:	fiat recharge
    transfer:	Merchants transfer money to each other
    """
    BLOCKCHAIN = 'blockchain'
    SYSTEM = 'system'
    RECHARGE = 'recharge'
    TRANSFER = 'transfer'


class WithdrawState(Enum):
    """
    reexamine:	    Under examination for withdraw validation
    canceled:	    Withdraw canceled by user
    pass:   	    Withdraw validation passed
    reject: 	    Withdraw validation rejected
    transferred:	On-chain transfer initiated
    confirmed:  	On-chain transfer completed with one confirmation
    """
    REEXAMINE = 'canceled'
    CANCELED = 'canceled'
    PASS = 'pass'
    REJECT = 'reject'
    TRANSFERRED = 'transferred'
    CONFIRMED = 'confirmed'


class ConnectionState(Enum):
    IDLE = 0
    CONNECTED = 1
    CLOSED_ON_ERROR = 2


class Channel(Enum):
    WHOLE_DEPTH = "DepthWhole"
    DEPTH = "Depth"
    KLINE = "KLine"
    TRADE = "Trade"
    TICKER = "Ticker"
    ORDER_CHANGE = "{}_RECORD_ADD_{}_{}"
