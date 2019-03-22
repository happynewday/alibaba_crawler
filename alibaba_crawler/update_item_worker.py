# coding: utf8  
""" 更新卖家信息
"""
import json
import requests
from pyrabbitmq import Consumer
from alibaba_parser import AlibabaParser
import config


class UpdateItemWorker(Consumer):
    def __init__(self, order):
        super(UpdateItemWorker, self).__init__(config.MQ_URL, 
                config.EXCHANGE, config.QUEUE_ALIBABA_ITEM)
        self.parser = AlibabaParser()
        self.mysql = config.get_mysql()

    
    def update_status(self, _id, status):
        sql = 'UPDATE alibaba_item SET status=%s WHERE id=%s'
        self.mysql.execute(sql, (status, _id))


    def consume(self, body):
        params = json.loads(body)
        _id = params['id']
        itemId = params['itemId']
        url = 'https://m.1688.com/offer/{}.html?'.format(itemId)
        
        self.log.info('模拟浏览器打开页面[{}]'.format(url))
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
        code, idx = d.get('error_code', ''), int(d.get('index', 0))
        html = d.get('html', '')
        self.log.info('response [{}:{}:{}]'.format(d['status'], code, idx))
        
        if d['status'] != 'OK' or idx <= 2:
            self.log.error('无法打开网页')
            return
        
        info = self.parser.parse_item_page(d['html'])
        if info is None:
            self.log.error('解析失败')
            return self.update_status(_id, 'PARSE_FAILED')

        self.log.info('更新商品信息')
        info['status'] = 'OK'
        keys = []
        values = []
        for k,v in info.items():
            keys.append(k)
            values.append(v)

        fields = ', '.join(['{}=%s'.format(k) for k in keys])
        sql = 'UPDATE alibaba_item SET {} WHERE id=%s'.format(fields)
        args = tuple(values + [_id])
        self.mysql.execute(sql, args)

