#coding; utf8

#from pymysql import PyMySql
import pymysql
pymysql.install_as_MySQLdb()


MQ_URL = 'amqp://guest:guest@10.25.1.73:5672/%2F'
EXCHANGE = 'exchange_crawler'
QUEUE_ALIBABA_QUERY = 'alibaba_query'
QUEUE_ALIBABA_SELLER = 'alibaba_seller'
QUEUE_ALIBABA_OFFER = 'alibaba_offer'
QUEUE_ALIBABA_ITEM = 'alibaba_item'
BROWSER_AGENCY_HOST = 'http://101.37.223.149/_open'

RDS_HOST = 'hp-test.mysql.polardb.rds.aliyuncs.com'
RDS_PORT = 3306
RDS_USER = 'hp_test'
RDS_PSWD = 'F&pe09dRxorco1RY'

def get_mysql():
    return pymysql.connect(host=RDS_HOST, port=RDS_PORT,
            user=RDS_USER, password=RDS_PSWD, database='k3w_crawler')

