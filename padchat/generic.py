#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# Author: Ben Chen
from tornado import ioloop

from .api import PadChatAPIMixin
from .constant import LoginType
from .base import BasePadchatClient
from .callback import PadChatCallbackMixin
from .event import PadChatEventMixin
from .push import PadchatPushMixin


class PadchatClient(PadChatEventMixin, PadChatAPIMixin,
                    PadChatCallbackMixin, PadchatPushMixin, BasePadchatClient):
    def login_callback(self, data, last_payload):
        super().login_callback(data, last_payload)
        self.login_init()

    def login_init(self):
        self._first_push_event = False

    def event_push(self, data: dict):
        if self._first_push_event:
            super().event_push(data)
        else:
            self._first_push_event = True

    def run(self):
        try:
            ioloop.IOLoop.instance().start()
        except KeyboardInterrupt:
            self.close()

    def event_login(self, data):
        super().event_login(data)
        # 避免重复拉取旧消息
        self.sync_msg()


class ReconnectPadchatClient(PadchatClient):
    def event_logout(self, data):
        super().event_logout(data)
        self.login(LoginType.qrcode)
