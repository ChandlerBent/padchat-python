#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# Author: Ben Chen
from tornado import gen
from tornado import httpclient
from tornado import httputil
from tornado import ioloop
from tornado import websocket

import json

from .user import UserProfile
from .logger import logger



APPLICATION_JSON = 'application/json'

DEFAULT_CONNECT_TIMEOUT = 60
DEFAULT_REQUEST_TIMEOUT = 60


class PadchatSocketProtocol13(websocket.WebSocketProtocol13):
    pass


class PadchatSocketClientConnection(websocket.WebSocketClientConnection):
    def get_websocket_protocol(self):
        return PadchatSocketProtocol13(self, mask_outgoing=True,
                                   compression_options=self.compression_options)


class WebSocketClient:
    """Base for web socket clients.
    """

    def __init__(self, *, connect_timeout=DEFAULT_CONNECT_TIMEOUT,
                 request_timeout=DEFAULT_REQUEST_TIMEOUT, ping_interval=30):

        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        self.ping_interval = ping_interval

        self._url = None

        def periodic_ping(_self):
            super(PadchatSocketProtocol13, _self).periodic_ping()
            self.ping()
        PadchatSocketProtocol13.periodic_ping = periodic_ping

    def run(self):
        ioloop.IOLoop.instance().start()

    def connect(self, url):
        """Connect to the server.
        :param str url: server URL.
        """
        self._url = url
        self._connect()

    def _connect(self):

        headers = httputil.HTTPHeaders({'Content-Type': APPLICATION_JSON})
        request = httpclient.HTTPRequest(url=self._url,
                                         connect_timeout=self.connect_timeout,
                                         request_timeout=self.request_timeout,
                                         headers=headers)
        ws_conn = PadchatSocketClientConnection(request,
                                                ping_interval=self.ping_interval)
        self._ws_connection = ws_conn
        ws_conn.connect_future.add_done_callback(self._connect_callback)

    def ping(self):
        pass

    def send(self, data):
        """Send message to the server
        :param str data: message.
        """
        if not self._ws_connection:
            raise RuntimeError('Web socket connection is closed.')

        self._ws_connection.write_message(data)

    def close(self):
        """Close connection.
        """

        if not self._ws_connection:
            raise RuntimeError('Web socket connection is already closed.')

        self._ws_connection.close()

    def _connect_callback(self, future):
        if future.exception() is None:
            self._ws_connection = future.result()
            self._on_connection_success()
            self._read_messages()
        else:
            self._on_connection_error(future.exception())

    @gen.coroutine
    def _read_messages(self):
        while True:
            msg = yield self._ws_connection.read_message(
                callback=self.__on_message)
            if msg is None:
                self._on_connection_close()
                break

            # self._on_message(msg)

    def __on_message(self, future):
        msg = future.result()
        if msg is not None:
            self._on_message(msg)

    def _on_message(self, msg):
        """This is called when new message is available from the server.
        :param str msg: server message.
        """
        pass

    def _on_connection_success(self):
        """This is called on successful connection ot the server.
        """
        pass

    def _on_connection_close(self):
        """This is called when server closed the connection.
        """
        pass

    def _on_connection_error(self, exception):
        """This is called in case if connection to the server could
        not established.
        """
        print('Connection error: %s', exception)


class BasePadchatClient(WebSocketClient):
    def __init__(self, user=None, wx_data=None, token=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 微信实例变量
        self._cmd_id = 0

        self._wx_data = wx_data
        self._token = token

        # user info
        self.user = user

        # 消息回调队列
        self._msg_queue = {}

        # 状态变量
        self._init = False
        self._scan_tip = False
        self._is_scan_tip = False

    @property
    def cmd_id(self):
        # 自增长命令ID，用于标记每一条指令发送的唯一ID，在回调中根据命令ID返回对应事件
        self._cmd_id += 1
        return str(self._cmd_id)

    def _on_connection_success(self):
        logger.info('连接Padchat服务器成功……')
        self.init()

    def _on_message(self, raw_msg):
        msg = json.loads(raw_msg)
        logger.info(msg)
        msg_type = msg.get('type')
        if msg_type == 'cmdRet':
            self.cmd_msg_callback_route(msg)
        elif msg_type == 'userEvent':
            self.event_msg_route(msg)
        else:
            logger.warn('unknow msg type: {} text: {}'.format(
                msg_type, msg))

    def _on_connection_close(self):
        logger.info('与Padchat服务器连接已中断')
        logger.info('重新连接Padchat服务器……')
        self._connect()

    def _on_connection_error(self, exception):
        logger.error('异常出错', exc_info=True)
        logger.info('重新连接Padchat服务器……')
        self._connect()

    def cmd_msg_callback_route(self, msg):
        '''
        请求回应回调路由
        '''
        raise NotImplementedError

    def event_msg_route(self, msg):
        raise NotImplementedError

    def send(self, cmd, cmd_id, type='user', authkey=None, callback=None,
             data=None):
        '''
        发送指令
        '''
        payload = {
            'cmd': cmd,
            'type': type,
        }
        if cmd_id:
            payload['cmdId'] = cmd_id
        if data:
            payload['data'] = data

        content = json.dumps(payload, ensure_ascii=False)

        logger.debug(content)
        self.store_msg_queue(cmd_id, callback, data)
        super().send(content)

    def pop_msg_queue(self, cmd_id):
        '''
        返回对应cmd id的回调函数
        '''
        return self._msg_queue.pop(cmd_id)

    def store_msg_queue(self, cmd_id, callback, payload=None):
        '''
        存储cmd id对应的回调数据
        '''
        self._msg_queue[cmd_id] = {'callback': callback, 'payload': payload}

    def save_user(self):
        if self.user:
            if not self._wx_data:
                self.get_wx_data()
                return
            if not self._token:
                self.get_login_token()
                return
            user_profile = UserProfile()
            user_profile.save(self.user, self._wx_data, self._token)

    @staticmethod
    def load_users():
        user_profile = UserProfile()
        return user_profile.profile_file_data

    @staticmethod
    def select_user():
        user_profile = UserProfile()
        user_profile_map = list(enumerate(user_profile['nick_name']))
        logger.info('请输入要登录哪个用户的序号\n' + \
                    ('\n'.join(['{i}: {n}'.format(i=i+1, n=n)
                                for i, n in user_profile_map])
                     or '暂没微信账号登录记录') + \
                    '\n')
        index = input('不输入或0则为新用户登录: ')
        logger.debug(index)
        profile = None
        if index and index != '0':
            nickname = dict(user_profile_map).get(int(index)-1, None)
            if nickname is None:
                raise IndexError('用户序号不存在')
            profile = user_profile['nick_name'][nickname]
        return profile
