#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# Author: Ben Chen
def send_app_msg_xml_template(context):
    template = '''
<appmsg appid="{appid}" sdkver="{sdkver}">
<title>{title}</title>
<des>{des}</des>
<action>view</action>
<type>5</type>
<showtype>0</showtype>
<content></content>
<url>{url}</url>
<thumburl>{thumburl}</thumburl>
</appmsg>
'''.format(**context)
    return template