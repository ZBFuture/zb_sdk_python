import gzip
import json
import logging
import ssl
import threading

import websocket

# Key: ws, Value: connection
from zb.errors import *
from zb.model.constant import ConnectionState
from zb.utils import Utils

websocket_connection_handler = dict()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def on_message(ws, message):
    websocket_connection = websocket_connection_handler[ws]
    websocket_connection.on_message(message)
    return


def on_error(ws, error):
    websocket_connection = websocket_connection_handler[ws]
    websocket_connection.on_failure(error)


def on_close(ws):
    websocket_connection = websocket_connection_handler[ws]
    websocket_connection.on_close()


def on_open(ws):
    websocket_connection = websocket_connection_handler[ws]
    websocket_connection.on_open(ws)


connection_id = 0


def websocket_func(*args):
    connection_instance = args[0]
    # `pip3 install websocket-client` 如果报错提示：module 'websocket' has no attribute 'WebSocketApp'
    connection_instance.ws = websocket.WebSocketApp(connection_instance.url,
                                                    on_message=on_message,
                                                    on_error=on_error,
                                                    on_close=on_close)
    global websocket_connection_handler
    websocket_connection_handler[connection_instance.ws] = connection_instance
    connection_instance.logger.info("[Sub][" + str(connection_instance.id) + "] Connecting...")
    connection_instance.delay_in_second = -1
    connection_instance.ws.on_open = on_open
    connection_instance.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    connection_instance.logger.info("[Sub][" + str(connection_instance.id) + "] Connection event loop down")
    if connection_instance.state == ConnectionState.CONNECTED:
        connection_instance.state = ConnectionState.IDLE


class WebsocketConnection:

    def __init__(self, api_key, secret_key, url, watch_dog, request):
        self.__thread = None
        self.__api_key = api_key
        self.__secret_key = secret_key
        self.__watch_dog = watch_dog
        self.request = request

        self.delay_in_second = -1
        self.ws = None
        self.last_receive_time = 0

        self.logger = logging.getLogger('zb-client')
        global connection_id
        connection_id += 1
        self.id = connection_id
        self.state = ConnectionState.IDLE
        self.url = url

    def in_delay_connection(self):
        return self.delay_in_second != -1

    def re_connect_in_delay(self, delay_in_second):
        if self.ws is not None:
            self.ws.close()
            self.ws = None
        self.delay_in_second = delay_in_second

    def connect(self):
        if self.state == ConnectionState.CONNECTED:
            self.logger.info("[Sub][" + str(self.id) + "] Already connected")
        else:
            self.__thread = threading.Thread(target=websocket_func, args=[self])
            self.__thread.start()

    def re_connect(self):
        if self.delay_in_second != 0:
            self.delay_in_second -= 1
            self.logger.warning("[Sub][" + str(self.id) + "] In delay connection: " + str(self.delay_in_second))
        else:
            self.connect()

    def send(self, data):
        self.logger.info("[Sub][" + str(self.id) + "] Send data to server: " + data)
        self.ws.send(data)

    def on_close(self):
        self.__watch_dog.on_connection_closed(self)
        del websocket_connection_handler[self.ws]
        self.ws.close()
        self.logger.error("[Sub][" + str(self.id) + "] Closing normally")

    def on_open(self, ws):
        self.logger.info("[Sub][" + str(self.id) + "] Connected to server")
        self.ws = ws
        self.last_receive_time = Utils.milliseconds()
        self.state = ConnectionState.CONNECTED
        if self.request.subscription_handler is not None:
            self.request.subscription_handler(self)

        self.__watch_dog.on_connection_created(self)
        return

    def on_error(self, error_message):
        if self.request.error_handler is not None:
            self.request.error_handler(error_message)
        self.logger.info("[Sub][" + str(self.id) + "] " + str(error_message))

    def on_failure(self, error):
        self.on_error("Unexpected error: " + str(error))
        self.close_on_error()

    def close_on_error(self):
        if self.ws is not None:
            # self.ws.close()
            self.state = ConnectionState.CLOSED_ON_ERROR
            self.logger.error("[Sub][" + str(self.id) + "] Connection is closing due to error")

    def close_on_hand(self):
        if self.ws is not None:
            if self.request.unsubscription_handler is not None:
                self.request.unsubscription_handler(self)

            self.on_close()

    def on_message(self, message):
        self.last_receive_time = Utils.milliseconds()

        if isinstance(message, str):
            # print("RX string : ", message)
            json_wrapper = json.loads(message)
        elif isinstance(message, bytes):
            # print("RX bytes: " + gzip.decompress(message).decode("utf-8"))
            json_wrapper = json.load(gzip.decompress(message).decode("utf-8"))
        else:
            self.logger.error("[Sub][" + str(self.id) + "] RX unknown type : ", type(message))
            return

        if 'action' in json_wrapper and 'pong' == json_wrapper['action']:
            return

        if 'errorCode' in json_wrapper:
            print(json_wrapper)
            self.on_error(json_wrapper)
            return

        res = None
        try:
            if self.request.json_parser is not None:
                res = self.request.json_parser(json_wrapper)
        except Exception as e:
            self.logger.error("[Sub][" + str(self.id) + "] Failed to parse server's response", e)
            self.on_error("Failed to parse server's response: " + str(e))

        try:
            if self.request.update_callback is not None:
                self.request.update_callback(res)
        except Exception as e:
            self.logger.error("[Sub][" + str(self.id) + "] Failed to call the callback method,message:" + res, e)
            self.on_error("Process error: " + str(e) + " You should capture the exception in your error handler")
