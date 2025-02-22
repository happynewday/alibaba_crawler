# coding=utf-8
import json
import time

import pymysql
import requests
from lxml import html
import re
from pybase import BaseObject
import config

class K3ShoesListClawler(BaseObject):
    def __init__(self):
        BaseObject.__init__(self)
        self.db = config.get_mysql()
        self.cursor = self.db.cursor(cursor=pymysql.cursors.DictCursor)

    def run(self):
        sql = "select * from k3w_shop"
        self.cursor.execute(sql)
        for shop in self.cursor.fetchall():
            products = self.process_one_page(shop['url'])
            if(len(products) <= 0):
                continue

            self.log.info('商家:{}, 得到 [{}] 个商品'.format(shop['name'], len(products)))
            inserts = []
            for p in products:
                inserts.append((p['url'], p['cover'], p['desc'],
                        p['price'], p['product_no']))
            sql = ('INSERT IGNORE INTO k3w_product (url, cover, description, '
                    'price, product_no) VALUES (%s, %s, %s, %s, %s)')
            self.cursor.executemany(sql, inserts)
            self.db.commit()

            time.sleep(0.2)

    def process_one_page(self, url):
        cookie_str = 'UM_distinctid=17eddf2437f110-01b3bd3a28c42b-f791539-154ac4-17eddf2438065c; __51vcke__JH8oID4DYgzN67sY=b7465b70-d5fa-532b-8b69-9569dbcea25d; __51vuft__JH8oID4DYgzN67sY=1644401149573; _ati=2800730497315; k3cn=dXNlcl9pZD0zMjI3NzEwJnR5cGU9MCZ1c2VybmFtZT0xNzM3NjU0Mzk3MkBrMy5jbiZ0PTE2NDQ0MDEzNDcmaGFzaD01NDA0NTg2NmVjNzZlY2I1NTJkYjc5NzRhZjJiZDVhMw%3D%3D; acw_tc=2f624a2416453378873893004e7ef9ad7b218c48f7c4895b6653cb5b0ff3fc; CNZZDATA1278071117=910611069-1644399317-null%7C1645330073; __51uvsct__JH8oID4DYgzN67sY=3; __vtins__JH8oID4DYgzN67sY=%7B%22sid%22%3A%20%2288c2ca56-96cd-513d-ba9a-42ee702d46d8%22%2C%20%22vd%22%3A%208%2C%20%22stt%22%3A%20536189%2C%20%22dr%22%3A%205866%2C%20%22expires%22%3A%201645340224856%2C%20%22ct%22%3A%201645338424856%7D'

        cookies = {}
        for line in cookie_str.split(';'):
            name, value = line.strip().split('=', 1)
            cookies[name] = value

        print json.dumps(cookies)
        send_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
            "Connection": "keep-alive",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Referer": "http://www.k3.cn/supplier/0,,0,0,1,1,.html"}

        r = requests.get(url, cookies=cookies, headers=send_headers)
        if r.status_code != 200:
            self.log.error('request failed')
            return None
        return self.parse_shoes_list(r.content)

    def parse_shoes_list(self, content):
        try:
            doc = html.fromstring(content)
            doc.make_links_absolute('http://www.k3.cn')
            root = doc.getroottree()

            products = []
            for li in root.xpath('.//div[@class="product_box"]/ul[@class="product_menu"]/li'):
                product = {}
                _a = li.xpath('.//a[@class="picture_box"]')[0]
                product['url'] = _a.attrib['href'].strip()

                _cover = _a.xpath('.//img')[0]
                product['cover'] = _cover.attrib['src'].strip()

                _desc = li.xpath('.//p[@class="title_text"]')[0]
                if _desc is not None and _desc.text is not None:
                    product['desc'] = _desc.text.strip()
                else:
                    product['desc'] = None

                _price = li.xpath('.//p[@class="unit_price"]')[0]
                if _price is not None and _price.text is not None:
                    product['price'] = _price.text.strip().replace(u"¥", "")
                else:
                    product['price'] = None

                _productNo = li.xpath('.//p[@class="business_text"]/a')[0]
                if _productNo is not None and _productNo.text is not None:
                    product['product_no'] = _productNo.text.strip().replace(u"货号：", "")
                else:
                    product['product_no'] = None

                products.append(product)
            return products
        except Exception as e:
            self.log.exception(e)
            return None

def main(args=None):
    k = K3ShoesListClawler()
    k.run()


if __name__ == '__main__':
    main()