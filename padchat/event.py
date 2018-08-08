#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# Author: Ben Chen
import qrcode
import qrcode_terminal
from xml.dom import minidom

from .constant import LoginType
from .user import User
from .logger import logger



class PadChatEventMixin:
    def event_msg_route(self, msg):
        EVENT_MAP = {
            'qrcode': self.event_qrcode, # 二维码
            'scan': self.event_scan, # 扫码
            'push': self.event_push, # 新消息
            'login': self.event_login, # 登录
            'logout': self.event_logout, # 注销登录
            'loaded': self.event_loaded, # 通讯录载入完毕
            'over': self.event_over, # 实例关闭
        }
        response_event = msg.get('event')
        event_callback = EVENT_MAP.get(response_event, None)
        if not event_callback:
            logger.error('unknow event: {response_event} body: {msg}'.format(
                response_event=response_event, msg=msg
            ))
        else:
            event_callback(msg.get('data'))

    # event 函数 ###############################################################

    def event_qrcode(self, data):
        '''
        二维码事件
        :param data: 
        :return: 
        '''
        url = data.get('url')
        self._qrcode(url, style='terminal')

    def _qrcode(self, data, style='img'):
        logger.debug(data)
        if style == 'img':
            image = qrcode.make(data)
            image.save('qrcode.png')
        elif style == 'terminal':
            qrcode_terminal.draw(data)

    def event_login(self, data):
        '''
        登录事件
        :param data: 
        :return: 
        '''
        logger.info('微信账号登陆成功！')
        self.get_login_token()

    def event_logout(self, data):
        '''
        注销事件
        :param data: 
        :return: 
        '''
        logger.info('已注销登录')

    def event_scan(self, data):
        '''
        扫码事件
        {
            "email":"",
            "external":"1",
            "long_link_server":"",
            "message":"Everything is ok",
            "nick_name":"这是昵称",
            "phone_number":"",
            "qq":1395472425,
            "short_link_server":"",
            "status":0,
            "uin":2751152411,
            "user_name":"wxid_xv6ks2q5miaq11"
        }
        :param data: 
        :return: 
        '''
        status = data.get('status')
        if status is 0:
            if not self._scan_tip:
                logger.info('等待扫码……')
                self._scan_tip = True
        elif status is 1:
            if not self._is_scan_tip:
                logger.info('{} 已扫码，请在手机端确认登录……'.format(
                    data.get('nick_name')))
                self._is_scan_tip = True
        elif status is 2:
            logger.debug(data)
            external = data.get('external')
            if external == 0:
                logger.info('扫码成功！登录成功！')
                user = User(**data)
                self.user = user
                self.save_user()
            elif external == 1:
                logger.info('扫码成功！登录失败！')
                self.login(LoginType.qrcode)
            else:
                logger.error('扫码成功！登录未知状态码！')
                self.login(LoginType.qrcode)
            self._scan_tip = False
            self._is_scan_tip = False
        elif status is 3:
            logger.info('二维码已过期')
            self._scan_tip = False
            self._is_scan_tip = False
            logger.info('将重新获取登录二维码')
            self.login(LoginType.qrcode)
        elif status is 4:
            logger.info('手机端已取消登录')
            self._scan_tip = False
            self._is_scan_tip = False
            self.login(LoginType.qrcode)

    def event_push(self, data: dict):
        '''
        消息推送
        :param data: 
        :return: 
        '''
        for push in data.get('list', []):
            sub_type = push.get('sub_type')
            if not sub_type or sub_type in (2048, 32768):
                # 无意义推送
                continue
            elif sub_type == 1:
                if push.get('from_user') == self.user.wx_id:
                    self.self_text_msg(push)
                else:
                    self.text_msg(push)
            elif sub_type == 2:
                logger.debug('好友信息推送，包含好友，群，公众号信息')
            elif sub_type == 3:
                logger.debug('图片消息')
            elif sub_type == 34:
                logger.debug('语音消息')
            elif sub_type == 37:
                self.friend_invite_msg(push)
            elif sub_type == 42:
                logger.debug('名片消息')
            elif sub_type == 43:
                logger.debug('视频消息')
            elif sub_type == 47:
                logger.debug('表情消息')
            elif sub_type == 48:
                logger.debug('定位消息')
            elif sub_type == 49:
                logger.debug('APP消息')
                content = push.get('content')
                if self._is_group_msg(push):
                    from_user, content = content.split(':\n', 1)
                xml = minidom.parseString(content)
                appmsg = xml.getElementsByTagName('appmsg')[0]
                type = appmsg.getElementsByTagName('type')[0].childNodes[0].data
                if type == '2000':
                    # 转账
                    if push.get('from_user') != self.user.wx_id:
                        # 转账给他人不触发事件，仅针对收到其他人转账
                        self.transfer_msg(push)
                elif type == '2001':
                    # 红包
                    self.red_packet_msg(push)
                elif type == '5':
                    # 收款通知
                    self.zhifu_msg(push)
                else:
                    self.app_msg(push)
            elif sub_type == 50:
                logger.debug('语音通话')
            elif sub_type == 62:
                logger.debug('小视频')
            elif sub_type == 2000:
                logger.debug('转账消息')
            elif sub_type == 2001:
                logger.debug('红包消息')
            elif sub_type == 3000:
                logger.debug('群邀请')
            elif sub_type == 9999:
                logger.debug('系统通知')
            elif sub_type == 10000:
                logger.debug('微信通知信息')
                if '為朋友，現在可以聊天了。' in push.get('content'):
                    self.add_friend_msg(push)
                elif '，现在可以开始聊天了。' in push.get('content'):
                    self.add_friend_msg(push)
            elif sub_type == 10002:
                logger.debug('撤回消息')
            else:
                logger.debug('其他信息: ', push)
            logger.debug(push)

    def event_loaded(self, data):
        logger.info('同步通讯录完成')

    def event_over(self, data):
        '''
        实例关闭
        :param data: 
        :return: 
        '''
        logger.warning('实例已关闭')
        logger.info('重新连接服务器')
        self._connect()

    def _is_group_msg(self, context):
        from_user = context.get('from_user')
        return from_user.endswith('@chatroom')
