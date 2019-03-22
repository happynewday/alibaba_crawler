# coding: utf8  
""" 扫描卖家商品
"""
import json
from datetime import datetime
import requests
from pyrabbitmq import Consumer
from alibaba_parser import AlibabaParser
import config


class ScanSellerWorker(Consumer):
    def __init__(self, order):
        super(ScanSellerWorker, self).__init__(config.MQ_URL, 
                config.EXCHANGE, config.QUEUE_ALIBABA_OFFER)
        self.parser = AlibabaParser()
        self.mysql = config.get_mysql()


    def process_one_page(self, params, page=1):
        _id = params['id']
        url = '{}/page/offerlist.htm?sortType=wangpu_score&pageNum={}#search-bar'.format(
                params['url'], page)
        r = requests.get(url)
        if r.status_code != 200:
            self.log.error('request failed')
            return None
        return self.parser.parse_offer_list(r.content)


    def consume(self, body):
        params = json.loads(body)
        sellerId = params['id']
     
        items = []
        self.log.info('处理第[1]页')
        t = self.process_one_page(params, 1)
        if t is None:
            self.log.error('process page [1] failed')
            return

        items += t[0]
        end = min(20, t[1]+1)
        for p in range(2, end):
            self.log.info('处理第[{}/{}]页'.format(p, end))
            _t = self.process_one_page(params, p)
            if _t is None:
                self.log.error('process page [{}] failed'.format(p))
                continue
            items += _t[0]
        
        self.log.info('得到 [{}] 个商品'.format(len(items)))
        inserts = []
        day = int(datetime.now().strftime('%Y%m%d'))
        for s in items:
            inserts.append((s['id'], sellerId, s['title'], s['url'], 
                    s['image'], day))
        sql = ('INSERT IGNORE INTO alibaba_item (itemId, sellerId, ' 
                'title, url, image, day) VALUES (%s, %s, %s, %s, %s, %s)')
        for i in range(0, len(inserts), 200):
            self.mysql.executemany(sql, inserts[i:i+200])
   
