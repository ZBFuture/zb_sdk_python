from zb.model import *
from zb.model.common import ResultModel
from zb.utils import Utils

class Event(ResultModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.channel = Utils.safe_string(kwargs, 'channel')
        self.data = kwargs['data']

class DepthEvent(Event):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        data = kwargs['data']
        self.asks = [DepthEntry(item[0], item[1]) for item in data['asks']] if 'asks' in data else None
        self.bids = [DepthEntry(item[0], item[1]) for item in data['bids']] if 'bids' in data else None


class KlineEvent(Event):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.isWhole = 'type' in kwargs and kwargs['type'] == 'Whole'
        self.data = [Kline.json_parse(item) for item in kwargs['data']]

class TradeEvent(Event):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.channel = kwargs['channel']
        self.data = [Trade.json_parse(item) for item in kwargs['data']]


class TickerEvent(Event):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.channel = kwargs['channel']
        self.data = Ticker.json_parse(kwargs['data'])

class AllTickerEvent(Event):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.channel = kwargs['channel']
        self.data = {}
        for k, v in kwargs['data'].items():
            self.data[k] = Ticker.json_parse(v)
