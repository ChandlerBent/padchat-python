#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# Author: Ben Chen
from padchat import PadchatClient


class TestClient(PadchatClient):
    def person_text_msg(self, context):
        content = context.get('content')
        from_user = context.get('from_user')
        if content == '个人资料':
            self.get_contact(from_user)
        elif content == '设置头像':
            with open('100.jpg', 'rb') as file:
                self.set_head_img(file)
        elif content == '同步通讯录':
            self.sync_contact()
        elif content == '同步通讯录1':
            # 慎用
            self.sync_contact(reset=True)
        elif content == '获取二维码':
            self.get_user_qrcode()
        elif content == '自己资料':
            self.get_my_info()
        elif content == '创建群':
            self.create_room([from_user, 'wxid_geokcg6ywrg921'])
        elif content.startswith('加群'):
            self.add_room_member(content.split(':')[1], from_user)
        elif content.startswith('邀请'):
            self.invite_room_member(content.split(':')[1], from_user)
        elif content == '发送app消息':
            self.send_app_msg(from_user, title='测试', des='描述测试', url='https://www.baidu.com', thumburl='https://ss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/img/logo_top_ca79a146.png')
        elif content == '发送图片':
            with open('100.jpg', 'rb') as file:
                self.send_image(from_user, file)
        elif content == '分享名片':
            self.share_card(from_user, '测试分享', from_user)

    def group_text_msg(self, context):
        from_user, content = context.get('content').split(':\n', 1)
        group_id = context.get('from_user')
        if content == '群成员列表':
            self.get_room_members(group_id)
        elif content == '退群':
            self.delete_room_member(group_id, from_user)
        elif content.startswith('公告'):
            self.set_room_announcement(group_id, content)
        elif content.startswith('群名'):
            self.set_room_name(group_id, content.split(':')[1])
        elif content == '二维码':
            self.get_room_qrcode(group_id)
        elif content == '解散':
            self.quit_room(group_id)
        elif content == '发送app消息':
            self.send_app_msg(group_id, title='测试', des='描述测试', url='https://www.baidu.com', thumburl='https://ss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/img/logo_top_ca79a146.png')
        elif content == '发送图片':
            with open('100.jpg', 'rb') as file:
                self.send_image(group_id, file)
        elif content == '分享名片':
            self.share_card(group_id, '测试分享', from_user)

    def get_contact_callback(self, data, last_payload):
        print('获取个人资料')
        print(data)

    def sync_contact_callback(self, data, last_payload):
        print('同步通讯录')
        print(data)

    def get_contact_qrcode_callback(self, data, last_payload):
        print('获取个人二维码')
        print(data)
        print(last_payload)

    def get_my_info_callback(self, data, last_payload):
        print('获取自己资料')
        print(data)



if __name__ == '__main__':
    user = TestClient.select_user()

    client = TestClient(**(user or {}))
    client.connect('ws://52.80.34.207:7777')
    client.run()