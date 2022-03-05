# coding=utf-8
import time

import requests
from lxml import html
import re
import config
from pybase import BaseObject

class K3ShopClawler(BaseObject):
    def __init__(self):
        BaseObject.__init__(self)
        self.db = config.get_mysql()
        self.cursor = self.db.cursor()


    def run(self):
        for page in range(1,31):
            sellers = self.process_one_page(page)
            if len(sellers) <= 0:
                continue

            self.log.info('页码:{}, 得到 [{}] 个卖家'.format(page, len(sellers)))
            inserts = []
            for s in sellers:
                inserts.append((s['name'], s['url'], s['phone'],
                        s['qq'], s['address']))
            sql = ('INSERT IGNORE INTO k3w_shop (name, url, phone, '
                    'qq, address) VALUES (%s, %s, %s, %s, %s)')
            self.cursor.executemany(sql, inserts)
            self.db.commit()
            time.sleep(0.5)

    def process_one_page(self, page=1):
        url = 'http://www.k3.cn/supplier/0,,0,0,{},1,.html'.format(page)
        cookie_str = 'UM_distinctid=17eddf2437f110-01b3bd3a28c42b-f791539-154ac4-17eddf2438065c; __51vcke__JH8oID4DYgzN67sY=b7465b70-d5fa-532b-8b69-9569dbcea25d; __51vuft__JH8oID4DYgzN67sY=1644401149573; _ati=2800730497315; k3cn=dXNlcl9pZD0zMjI3NzEwJnR5cGU9MCZ1c2VybmFtZT0xNzM3NjU0Mzk3MkBrMy5jbiZ0PTE2NDQ0MDEzNDcmaGFzaD01NDA0NTg2NmVjNzZlY2I1NTJkYjc5NzRhZjJiZDVhMw%3D%3D; acw_tc=2f624a2416453378873893004e7ef9ad7b218c48f7c4895b6653cb5b0ff3fc; CNZZDATA1278071117=910611069-1644399317-null%7C1645330073; __51uvsct__JH8oID4DYgzN67sY=3; __vtins__JH8oID4DYgzN67sY=%7B%22sid%22%3A%20%2288c2ca56-96cd-513d-ba9a-42ee702d46d8%22%2C%20%22vd%22%3A%208%2C%20%22stt%22%3A%20536189%2C%20%22dr%22%3A%205866%2C%20%22expires%22%3A%201645340224856%2C%20%22ct%22%3A%201645338424856%7D'

        cookies = {}
        for line in cookie_str.split(';'):
            name, value = line.strip().split('=', 1)
            cookies[name] = value

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
        return self.parse_shop_list(r.content)

    def parse_shop_list(self, content):
        try:
            doc = html.fromstring(content)
            doc.make_links_absolute('http://www.k3.cn')
            root = doc.getroottree()

            sellers = []
            for li in root.xpath('.//div[@class="seller_left"]/ul[@class="seller_list"]/li'):
                seller = {}
                _a = li.xpath('.//div[@class="list_con"]/div[@class="name"]/a')[0]
                seller['name'] = _a.text.strip()

                _url = li.xpath('.//div[@class="list_con"]/div[2]/a')[0]
                seller['url'] = _url.text.strip()

                _mobile = li.xpath('.//div[@class="list_con"]/div[4]/span["supplier_mobile_info"]/input')[0]
                seller['phone'] = _mobile.attrib['value']

                _qq = li.xpath('.//div[@class="list_con"]/div[4]/span')[1]
                seller['qq'] = _qq.text.strip().replace(u"QQ：", "")

                _address = li.xpath('.//div[@class="list_con"]/div[5]')[0]
                seller['address']  = _address.text.strip().replace('\r','').replace('\n','').replace('\t','').replace(u"拿货地址：", "")

                sellers.append(seller)
            return sellers
        except Exception as e:
            self.log.exception(e)
            return None

def main(args=None):
    k = K3ShopClawler()
    k.run()

if __name__ == '__main__':
    main()