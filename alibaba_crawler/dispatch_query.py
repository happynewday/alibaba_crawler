# coding: utf-8
""" 分发查询词 
"""
import json
import codecs
from pyutil import get_logger, SingletonScript
from pyrabbitmq import qsize, Publisher
import config


def main():
    log = get_logger()
    log.info('start')
    if qsize(config.MQ_URL, config.EXCHANGE, 
            config.QUEUE_ALIBABA_QUERY) > 100:
        log.warning('queue is busy!')
        return
    
    publisher = Publisher(config.MQ_URL, config.EXCHANGE, 
            config.QUEUE_ALIBABA_QUERY)
    for ln in codecs.open('queries', 'rb', 'utf8').readlines():
        q = ln.strip()
        if q:
            publisher.publish(json.dumps({'query': q}, ensure_ascii=False))
    log.info('finished')
   

if __name__ == '__main__':
    SingletonScript()
    main()

