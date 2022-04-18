from typing import List

from zb.client import ApiClient
from zb.model.account import *
from zb.model.constant import *


class AccountApi(ApiClient):
    def __init__(self, api_key, secret_key, api_host=None):
        describe = {
            'apis': {
                'private': {
                    'get': {
                        'account': '/Server/api/v2/Fund/getAccount',
                        'positions': '/Server/api/v2/Positions/getPositions',
                        'margin_info': '/Server/api/v2/Positions/marginInfo',
                        'nominal_value': '/Server/api/v2/Positions/getNominalValue',
                        'bill': '/Server/api/v2/Fund/getBill',
                        'bill_type_list': '/Server/api/v2/Fund/getBillTypeList',
                        'margin_history': '/Server/api/v2/Fund/marginHistory',
                        'setting': ' /Server/api/v2/setting/get',
                        'balance': '/Server/api/v2/Fund/balance',
                    },
                    'post': {
                        'update_margin': '/Server/api/v2/Positions/updateMargin',
                        'set_leverage': '/Server/api/v2/setting/setLeverage',
                        'set_positions_mode': ' /Server/api/v2/setting/setPositionsMode',
                        'set_margin_mode': ' /Server/api/v2/setting/setMarginMode',
                        'update_append_usd_value': ' /Server/api/v2/Positions/updateAppendUSDValue',
                        'set_margin_coins': ' /Server/api/v2/Positions/setMarginCoins',

                    },
                },
            }
        }

        super().__init__(api_key, secret_key, api_host, describe)

    def get_account(self, convert_unit='usd', futures_account_type=FuturesAccountType.BASE_USDT) -> Account:
        """
        合约账户信息
        :param convert_unit: 折合单位，页面显示上"≈"号后面的数字单位，可选：cny，usd,usdt,btc
        :param futures_account_type: 合约类型，1:USDT合约，2:QC本位合约，3:币本位合约
        :return: The current user information
        """
        params = {
            'convertUnit': convert_unit,
            'futuresAccountType': futures_account_type.value
        }
        account = self.private_get_account(params)
        print(account)
        return Account(**account)

    PositionsList = List[Positions]

    def get_positions(self, symbol: str, side=None, futures_account_type=FuturesAccountType.BASE_USDT) -> PositionsList:
        """
        所有合约仓位/单个合约仓位(marketId+side过滤)
        :param symbol:              市场名 如 BTC_USDT
        :param side:                1 多仓  0 空仓
        :param futures_account_type:1:USDT永续合约，2:QC本位合约，3:币本位合约，默认1
        :return:
        """
        params = {
            'symbol': symbol,
            'futuresAccountType': futures_account_type.value
        }
        if side:
            params['side'] = side

        positions = self.private_get_positions(params)

        return [Positions(**position) for position in positions]

    def get_margin_info(self, position_id: int, futures_account_type=FuturesAccountType.BASE_USDT) -> MarginInfo:
        """
        4.3 保证金信息查询（最大保证金增加数量，最大保证金提取数量，预计强平价格）
        如果没有记录不会创建一条空记录
        :param futures_account_type:1:USDT永续合约 2:QC本位合约，3:币本位合约
        :param position_id:         仓位Id
        :return: MarginInfo
        """
        params = {
            'positionsId': position_id,
            'futuresAccountType': futures_account_type.value
        }

        result = self.private_get_margin_info(params)
        return MarginInfo(**result)

    def set_leverage(self, symbol: str, leverage: int, futures_account_type=FuturesAccountType.BASE_USDT) -> PositionsSettingResult:
        """
        4.5 仓位杠杆设置
        :param symbol:              市场名称，如 BTC_USDT
        :param leverage:            杠杆倍数
        :param futures_account_type:1:USDT永续合约  2:QC本位合约，3:币本位合约
        :return: PositionsSettingResult
        """
        params = {
            'symbol': symbol,
            'leverage': leverage,
            'futuresAccountType': futures_account_type.value
        }

        result = self.private_post_set_leverage(params)

        return PositionsSettingResult(**result)

    def set_positions_mode(self, symbol: str, positions_mode: PositionsMode, futures_account_type=FuturesAccountType.BASE_USDT) -> PositionsSettingResult:
        """
        4.6 仓位持仓模式设置

        :param symbol:              市场名称，如 BTC_USDT
        :param positions_mode:      1:单向持仓，2: 双向持仓
        :param futures_account_type:1:USDT永续合约  2：币本位合约
        :return: PositionsSettingResult
        """
        params = {
            'symbol': symbol,
            'positionsMode': positions_mode.value,
            'futuresAccountType': futures_account_type.value
        }

        result = self.private_post_set_positions_mode(params)

        return PositionsSettingResult(**result)

    def set_margin_mode(self, symbol: str, margin_mode: MarginMode, futures_account_type=FuturesAccountType.BASE_USDT) -> PositionsSettingResult:
        """
        4.7 仓位保证金模式设置

        :param symbol:              市场名称，如 BTC_USDT
        :param margin_mode:         杠杆倍数
        :param futures_account_type:1:USDT永续合约  2:QC本位合约，3:币本位合约
        :return: SetLeverageResult
        """
        params = {
            'symbol': symbol,
            'marginMode': margin_mode.value,
            'futuresAccountType': futures_account_type.value
        }

        result = self.private_post_set_margin_mode(params)

        return PositionsSettingResult(**result)

    def get_nominal_value(self, symbol: str, side: int, futures_account_type=FuturesAccountType.BASE_USDT) -> NominalValueResult:
        """
        4.8 查看用户当前头寸.

        :param symbol:              市场名称，如 BTC_USDT
        :param side:                方向：1：开多   0 开空
        :param futures_account_type:1:USDT永续合约  2:QC本位合约，3:币本位合约
        :return: NominalValueResult
        """

        params = {
            'symbol': symbol,
            'side': side,
            'futuresAccountType': futures_account_type.value,
        }

        result = self.private_get_nominal_value(params)

        return NominalValueResult(**result)

    BillResultList = List[BillResult]

    def get_bill(self, currency=None, bill_type=None, start_time=None, end_time=None,
                 futures_account_type=FuturesAccountType.BASE_USDT, page=1, size=10) -> BillResultList:
        """
        4.9 查询用户bill账单

        :param currency:            币种名，如：btc
        :param bill_type:           账单类型 int
        :param start_time:          开始时间戳
        :param end_time:            结束时间戳
        :param futures_account_type:1:USDT永续合约  2:QC本位合约，3:币本位合约
        :param page:                页码
        :param size:                每页行数，默认10
        :return: BillResultList
        """

        params = {
            'pageNum': page,
            'pageSize': size,
            'futuresAccountType': futures_account_type.value,
        }
        if currency:
            params['currencyName'] = currency
        if bill_type:
            params['type'] = bill_type
        if start_time:
            params['startTime'] = start_time
        if end_time:
            params['endTime'] = end_time

        data = self.private_get_bill(params)

        return [BillResult(**item) for item in data['list']]

    def get_bill_type_list(self) -> List[BillTypeResult]:
        """
        4.10 查询账单类型信息list

        :return:  List[BillTypeResult]
        """

        result = self.private_get_bill_type_list()

        return [BillTypeResult(**item) for item in result]

    def get_margin_history(self, symbol: str, type=None, start_time=None, end_time=None, page=1, size=10) -> List[MarginHistoryResult]:
        """
        4.11 逐仓保证金变动历史

        :param symbol:      市场,如 ETH_USDT
        :param type:        调整方向 1: 增加逐仓保证金，0: 减少逐仓保证金
        :param start_time:  毫秒时间戳
        :param end_time:    毫秒时间戳
        :param page:        页码
        :param size:        每页行数，默认10
        :return: List[MarginHistoryResult]
        """

        params = {
            'symbol': symbol,
            'pageNum': page,
            'pageSize': size,
        }
        if type:
            params['type'] = type
        if start_time:
            params['startTime'] = start_time
        if end_time:
            params['endTime'] = end_time

        data = self.private_get_margin_history(params)

        return [MarginHistoryResult(**item) for item in data['list']]

    def get_setting(self, symbol: str, futures_account_type=FuturesAccountType.BASE_USDT) -> PositionsSettingResult:
        """
        4.12 仓位配置信息查询

        :param symbol:               市场id
        :param futures_account_type:1:USDT永续合约  2:QC本位合约，3:币本位合约
        :return: PositionsSettingResult
        """

        params = {
            'symbol': symbol,
            'futuresAccountType': futures_account_type.value,
        }

        result = self.private_get_setting(params)

        return PositionsSettingResult(**result)

    def get_balance(self, currency_name=None, futures_account_type=FuturesAccountType.BASE_USDT) -> List[BalanceResult]:
        """
        4.13 通过userid，currencyId查询资金

        :param currency_name:        币种名，如：BTC
        :param futures_account_type: 1:USDT永续合约  2:QC本位合约，3:币本位合约
        :return: List[BalanceResult]
        """

        params = {
            'currencyName': currency_name,
            'futuresAccountType': futures_account_type.value,
        }

        result = self.private_get_balance(params)

        return [BalanceResult(**item) for item in result]

    def update_append_usd_value(self, position_id: int, max_additional_usd_value: float, futures_account_type=FuturesAccountType.BASE_USDT) -> str:
        """
        4.14 设置自动追加保证金

        :param position_id:                 仓位ID int
        :param max_additional_usd_value:    设置增加的保证金数量，如果为0会关闭自动增加保证金
        :param futures_account_type:        1:USDT永续合约  2:QC本位合约，3:币本位合约
        :return: str 本次操作的clientId，由秒时间戳+仓位ID 组成
        """

        params = {
            'maxAdditionalUSDValue': max_additional_usd_value,
            'futuresAccountType': futures_account_type.value,
        }

        if position_id:
            params['positionsId'] = position_id

        return self.private_post_update_append_usd_value(params)

    def set_margin_coins(self, symbol: str, margin_coins: str, futures_account_type=FuturesAccountType.BASE_USDT) -> PositionsSettingResult:
        """
        4.15 设置保证金使用顺序
        使用位置：下单冻结顺序、开仓冻结顺序、手续费扣除顺序、已实现亏损扣除顺序、平仓解冻顺序、增加减少保证金顺序

        :param symbol:              市场名，如：btc_usdt
        :param margin_coins:        设置保证金顺序, 如：eth,usdt,qc
        :param futures_account_type:1:USDT永续合约  2:QC本位合约，3:币本位合约
        :return: str 本次操作的clientId，由秒时间戳+仓位ID 组成
        """

        params = {
            'symbol': symbol,
            'marginCoins': margin_coins,
            'futuresAccountType': futures_account_type.value,
        }

        result = self.private_post_set_margin_coins(params)

        return PositionsSettingResult(**result)
