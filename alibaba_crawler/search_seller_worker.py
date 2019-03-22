# coding: utf8  
""" 搜索卖家
"""
import json
import urllib
import requests
from pyrabbitmq import Consumer
from alibaba_parser import AlibabaParser
import config


class SearchSellerWorker(Consumer):
    def __init__(self, order):
        super(SearchSellerWorker, self).__init__(config.MQ_URL, 
                config.EXCHANGE, config.QUEUE_ALIBABA_QUERY)
        self.parser = AlibabaParser()
        self.mysql = config.get_mysql()


    def process_one_page(self, params, page=1):
        self.log.info('处理第[{}]页'.format(page))
        url = 'https://s.1688.com/company/company_search.htm?keywords={}&pageSize=30&offset=0&beginPage=1'.format(
                params['query'])
        r = requests.get(url)
        if r.status_code != 200:
            self.log.error('request failed')
            return None
        
        return self.parser.parse_search_result(r.content)


    def consume(self, body):
        params = json.loads(body)
        query = params['query']
        params['query'] = urllib.parse.quote(query.encode('gbk'))
        sellers = []
        t = self.process_one_page(params, 1)
        if t is None:
            self.log.error('process page [1] failed')
            return

        sellers += t[0]
        end = min(t[1]+1, 10)
        for p in range(2, end):
            _t = self.process_one_page(params, p)
            if _t is None:
                self.log.error('process page [{}] failed'.format(p))
                continue
            sellers += _t[0]
        
        self.log.info('得到 [{}] 个卖家'.format(len(sellers)))
        inserts = []
        for s in sellers:
            inserts.append((s['title'], s['address'], s['products'], 
                    s['businessType'], s['url']))
        sql = ('INSERT IGNORE INTO alibaba_seller (title, address, products, '
                'businessType, url) VALUES (%s, %s, %s, %s, %s)')
        for i in range(0, len(inserts), 200):
            self.mysql.executemany(sql, inserts[i:i+200])

