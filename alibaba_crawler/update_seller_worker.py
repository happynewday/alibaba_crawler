# coding: utf8  
""" 更新卖家信息
"""
import json
import requests
from pyrabbitmq import Consumer
from baidu_map_api import BaiduMapApi
from alibaba_parser import AlibabaParser
import config


class UpdateSellerWorker(Consumer):
    def __init__(self, order):
        super(UpdateSellerWorker, self).__init__(config.MQ_URL, 
                config.EXCHANGE, config.QUEUE_ALIBABA_SELLER)
        self.parser = AlibabaParser()
        self.mysql = config.get_mysql()
        self.mapApi = BaiduMapApi()


    def update_credit_detail(self, params):
        self.log.info('update credit detail')
        url = '{}/page/creditdetail.htm?'.format(params['url'])
        r = requests.get(url)
        if r.status_code != 200:
            self.log.error('request failed')
            return None
        return self.parser.parse_credit_detail(r.content)


    def update_lng_lat(self, params):
        self.log.info('update longitude and latitude')
        r = self.mapApi.get_lng_lat(params['address'])
        if r is not None:
            return {'longitude': r['lng'], 'latitude': r['lat']}
        return None
        

    def consume(self, body):
        params = json.loads(body)
        _id = params['id']
        
        info = {}
        r = self.update_credit_detail(params)
        if r is None:
            self.log.error('parse credit detail failed')
            return
        
        info.update(r)
        r = self.update_lng_lat(params)
        if r:
            info.update(r)

        self.log.info('update seller info')
        sql = ('UPDATE alibaba_seller SET longitude=%s, latitude=%s, '
                'contact=%s, phoneNumber1=%s, phoneNumber2=%s, '
                'creditCode=%s, image=%s, status=%s WHERE id=%s')
        args = (info.get('longitude', 0), info.get('latitude', 0), 
                info.get('contact', ''), info.get('phoneNumber1', ''), 
                info.get('phoneNumber2', ''), info.get('creditCode', ''), 
                info.get('image', ''), 'OK', _id)
        self.mysql.execute(sql, args)

