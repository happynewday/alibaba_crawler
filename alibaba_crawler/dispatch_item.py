# -*- coding: utf-8 -*-
""" 分发商品
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
            config.QUEUE_ALIBABA_ITEM) > 1000:
        log.warning('queue is busy!')
        return
    
    publisher = Publisher(config.MQ_URL, config.EXCHANGE, 
            config.QUEUE_ALIBABA_ITEM)
    mysql = config.get_mysql()
    
    columns = ['id', 'itemId', 'url']
    where = "WHERE status='NEW'"
    limit = "LIMIT 2000"
    order_by = "ORDER BY id DESC"
    for r in mysql.select('alibaba_item', columns, where, 
            order_by=order_by, limit=limit):
        message = dict(zip(columns, r))
        publisher.publish(json.dumps(message, ensure_ascii=False))
    log.info('finished')
   

if __name__ == '__main__':
    SingletonScript()
    main()

