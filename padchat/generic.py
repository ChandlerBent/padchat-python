#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# Author: Ben Chen
from tornado import ioloop
from tornado import gen
import time

from .api import PadChatAPIMixin
from .constant import LoginType
from .base import BasePadchatClient
from .event import PadChatEventMixin
from .push import PadchatPushMixin
from .logger import logger


class PadchatClient(PadChatEventMixin, PadChatAPIMixin, PadchatPushMixin,
                    BasePadchatClient):
    def _on_connection_success(self):
        super()._on_connection_success()
        self.init_padchat()

    def re_init_padchat(self):
        logger.info('将重新初始化实例')
        ioloop.IOLoop.instance().spawn_callback(self.init_padchat)

    @gen.coroutine
    def init_padchat(self):
        yield self.init()
        self._init = True
        logger.info('初始化成功')
        time.sleep(1)

        if self.user:
            yield self.login_padchat(LoginType.auto, token=self._token)
        else:
            yield self.login_padchat(LoginType.qrcode)

        self._first_push_event = False

    @gen.coroutine
    def wx_data_padchat(self):
        result = yield self.get_wx_data()
        if result.get('success') is True:
            wx_data = result['data'].get('wx_data')
            logger.info('获取实例设备数据成功')
            self._wx_data = wx_data
        else:
            logger.error('获取实例设备数据失败')

    @gen.coroutine
    def login_token_padchat(self):
        result = yield self.get_login_token()
        if result.get('success') is True:
            token = result['data'].get('token')
            logger.info('获取实例登录Token成功')
            self._token = token
        else:
            logger.error('获取实例登录Token失败')

    @gen.coroutine
    def login_padchat(self, login_type: str, **kwargs):

        result = yield self.login(type=login_type, **kwargs)

        if result.get('success') == True:
            logger.debug(result.get('msg'))
        else:
            if result.get('data', {}).get('status') == -2023:
                logger.error('尝试断线重连失败，尝试其他登录方式')
                result = yield self.login_padchat(LoginType.request, token=self._token)
            elif result.get('data', {}).get('status') in (-2017, -100):
                logger.error('尝试toten登录失败，尝试二维码方式登陆')
                result = yield self.login_padchat(LoginType.qrcode)
            else:
                logger.error('登录请求失败。将关闭实例后重新建立实例。')
                self.close()
                return
        return result

    @gen.coroutine
    def save_user_padchat(self):
        if not self._wx_data:
            yield self.wx_data_padchat()

        yield self.login_token_padchat()
        if self._wx_data and self._token:
            self._token = self._token
            if self.save_user():
                logger.info('保存用户登陆信息成功。')
            else:
                logger.error('保存用户登陆信息失败。')
        else:
            logger.error('保存用户登陆信息失败。')

    def event_push(self, data: dict):
        if self._first_push_event:
            super().event_push(data)
        else:
            self._first_push_event = True

    def event_login(self, data):
        super().event_login(data)
        self.save_user_padchat()

    def event_over(self, data):
        super().event_over(data)
        self.re_init_padchat()

    def run(self):
        try:
            ioloop.IOLoop.instance().start()
        except KeyboardInterrupt:
            self.close()
