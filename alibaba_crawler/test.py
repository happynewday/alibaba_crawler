# coding: utf8 
import sys
import json
import time
import urllib
from datetime import datetime
import requests
from pyutil import get_logger
import config
from baidu_map_api import BaiduMapApi
from alibaba_parser import AlibabaParser

def foo():
    content = open('/data/share/x.html', 'rb').read()
    parser = AlibabaParser()
    info = parser.parse_wab_item(content.decode('utf8'))
    print(info)
    sys.exit()

#foo()

log = get_logger()
url = 'https://bjhyscy.1688.com/page/creditdetail.htm?'
url = 'https://detail.1688.com/offer/561657785411.html'
url = 'https://m.1688.com/offer/1198767727.html?'
url = 'https://m.1688.com/offer/564638707168.html?'
url = sys.argv[1]

actions = [
        ('waitForXPath', ('//*[@id="widget-wap-detail-common-attribute"]/div/div[1]', {'timeout': 10000, 'visible': 1})), 
        ('keyboard.press', ('ArrowDown', {'delay': 250})),
        ('keyboard.press', ('ArrowDown', {'delay': 250})),
        ('waitForXPath', ('//*[@id="widget-wap-detail-common-preferential"]/div/div[1]', {'timeout': 10000, 'visible': 1})), 
        ('click', ('#J_WapCommonPreferenceList', )), 
        ]
actions = json.dumps(actions, ensure_ascii=False)


r = requests.post('http://192.168.9.207:8005/_open', 
        data={'url': url, 'actions': actions})
d = json.loads(r.content)
log.info('foo end [{}:{}:{}]'.format(d['status'], d.get('error_code', ''), d.get('error_desc', '')))
if d['status'] == 'OK' or d.get('error_code', '') == 'ACTION_FAILED':
    log.info('write')
    open('/data/share/x.html', 'wb').write(d['html'].encode('utf8'))
    parser = AlibabaParser()
    info = parser.parse_wab_item(d['html'])
    print(info)

