# coding: utf8 
""" 从物美的商品列表中生成查询词集合
"""
import codecs
from collections import defaultdict
from datetime import datetime, timedelta
from pyutil import get_logger
import config


log = get_logger()
mysql = config.get_mysql()
queries = defaultdict(int)
day = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
day = 20190314
log.info('read dmall item names on [{}]'.format(day))

def mk_query(name):
    t = name.split()
    if len(t[0]) >= 2:
        return t[0]
    return ''

for r in mysql.select('dmall_item', ['wareId', 'wareName'], 
        "WHERE _day={}".format(day)):
    _id, name = r
    q = mk_query(name)
    if q:
        queries[q] += 1

log.info('get [{}] queries'.format(len(queries)))
codecs.open('queries', 'wb', 'utf8').writelines(
        [k+'\n' for k in queries.keys()])
log.info('done')

