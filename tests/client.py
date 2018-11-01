#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# Author: Ben Chen
from tornado import gen

from padchat import PadchatClient


class TestClient(PadchatClient):
    @gen.coroutine
    def person_text_msg(self, context):
        content = context.get('content')
        from_user = context.get('from_user')
        if content == '个人资料':
            result = yield self.get_contact(from_user)
            print(result)
        elif content == '设置头像':
            with open('100.jpg', 'rb') as file:
                result = yield self.set_head_img(file)
        elif content == '同步通讯录':
            result = yield self.sync_contact()
        elif content == '同步通讯录1':
            # 慎用
            result = yield self.sync_contact(reset=True)
        elif content == '获取二维码':
            result = yield self.get_user_qrcode()
            print(result)
        elif content == '自己资料':
            result = yield self.get_my_info()
            print(result)
        elif content == '创建群':
            result = yield self.create_room([from_user, 'wxid_geokcg6ywrg921'])
        elif content.startswith('加群'):
            result = yield self.add_room_member(content.split(':')[1], from_user)
        elif content.startswith('邀请'):
            result = yield self.invite_room_member(content.split(':')[1], from_user)
        elif content == '发送app消息':
            result = yield self.send_app_msg(from_user, title='测试', des='描述测试', url='https://www.baidu.com', thumburl='https://ss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/img/logo_top_ca79a146.png')
        elif content == '发送图片':
            with open('100.jpg', 'rb') as file:
                result = yield self.send_image(from_user, file)
        elif content == '分享名片':
            result = yield self.share_card(from_user, '测试分享', from_user)

    @gen.coroutine
    def group_text_msg(self, context):
        from_user, content = context.get('content').split(':\n', 1)
        group_id = context.get('from_user')
        if content == '群成员列表':
            result = yield self.get_room_members(group_id)
        elif content == '退群':
            result = yield self.delete_room_member(group_id, from_user)
        elif content.startswith('公告'):
            result = yield self.set_room_announcement(group_id, content)
        elif content.startswith('群名'):
            result = yield self.set_room_name(group_id, content.split(':')[1])
        elif content == '二维码':
            result = yield self.get_room_qrcode(group_id)
        elif content == '解散':
            result = yield self.quit_room(group_id)
        elif content == '发送图片':
            with open('100.jpg', 'rb') as file:
                result = yield self.send_image(group_id, file)
        elif content == '分享名片':
            result = yield self.share_card(group_id, '测试分享', from_user)

    @gen.coroutine
    def red_packet_msg(self, context):
        result = yield self.receive_red_packet(context)
        key = result.get('data', {}).get('key')
        result = yield self.open_red_packet(context, key)
        if result.get('success') is True:
            print('领取红包成功')

    @gen.coroutine
    def image_msg(self, context):
        result = yield self.get_msg_image(context)


if __name__ == '__main__':
    user = TestClient.select_user()

    client = TestClient(**(user or {}))
    client.connect('ws://padchat-sdk.botorange.com:8988/')
    client.run()