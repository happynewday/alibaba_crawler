#coding; utf8 
from pymysql import PyMySql


MQ_URL = 'amqp://guest:guest@10.25.1.73:5672/%2F'
EXCHANGE = 'exchange_crawler'
QUEUE_ALIBABA_QUERY = 'alibaba_query'
QUEUE_ALIBABA_SELLER = 'alibaba_seller'
QUEUE_ALIBABA_OFFER = 'alibaba_offer'
QUEUE_ALIBABA_ITEM = 'alibaba_item'
BROWSER_AGENCY_HOST = 'http://101.37.223.149/_open'

RDS_HOST = 'rm-bp16w04r2zu0w499ao.mysql.rds.aliyuncs.com'
RDS_PORT = 3306
RDS_USER = 'bdtt'
RDS_PSWD = 'Chengzi123'

def get_mysql():
    return PyMySql(host=RDS_HOST, port=RDS_PORT, 
            user=RDS_USER, pswd=RDS_PSWD, db='crawler3')

