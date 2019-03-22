# -*- coding: utf-8 -*-
""" 分发卖家（抓取商品列表） 
"""
import json
from datetime import datetime
from pyutil import get_logger, SingletonScript
from pyrabbitmq import qsize, Publisher
import config


def main():
    log = get_logger()
    log.info('start')
    if qsize(config.MQ_URL, config.EXCHANGE, 
            config.QUEUE_ALIBABA_OFFER) > 100:
        log.warning('queue is busy!')
        return
    
    publisher = Publisher(config.MQ_URL, config.EXCHANGE, 
            config.QUEUE_ALIBABA_OFFER)
    mysql = config.get_mysql()
    
    columns = ['id', 'url']
    where = "WHERE status='OK'"
    for r in mysql.select('alibaba_seller', columns, where):
        message = dict(zip(columns, r))
        publisher.publish(json.dumps(message, ensure_ascii=False))
    log.info('finished')
   

if __name__ == '__main__':
    SingletonScript()
    main()

