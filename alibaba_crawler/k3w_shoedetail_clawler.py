# coding=utf-8
import json
import logging
import time
import random

import pymysql
import requests
from lxml import html
import re
from pybase import BaseObject
import config

class K3ShoesDetailClawler(BaseObject):
    def __init__(self):
        BaseObject.__init__(self)
        self.db = config.get_mysql()
        self.cursor = self.db.cursor(cursor=pymysql.cursors.DictCursor)

    def run(self):
        start = 0
        number = 0
        while True:
            updates = []
            sql = 'select * from k3w_product where title is null and status=0 order by id limit 100'
            fetch_number = self.cursor.execute(sql)
            if fetch_number <= 0:
                break

            for product in self.cursor.fetchall():
                try:
                    start = product['id']
                    detail = self.process_one_product(product['url'])
                except Exception as e:
                    self.log.exception(e)
                    update_sql = 'UPDATE k3w_product set status=1 where id={}'.format(product['id'])
                    self.cursor.execute(update_sql)
                    self.db.commit()

                time.sleep(10)
                if detail is None or len(detail) <= 0:
                    continue

                updates.append((detail["title"].encode('utf-8'), detail['pictures'].encode('utf-8'), detail['category'].encode('utf-8'),
                               detail['sizes'], detail['skus'], detail['details'],
                                detail['first_upload'].encode('utf-8'), detail['updated'].encode('utf-8'), product['id']))
            try:
                update_sql = 'UPDATE k3w_product set title=(%s), pictures=(%s), category=(%s), sizes=(%s), skus=(%s), details=(%s), first_upload=(%s), updated=(%s) where id=(%s)'
                self.cursor.executemany(update_sql, updates)
                self.db.commit()
            except:
                logging.exception("update k3w_project failed")
                self.db.rollback()

    def process_one_product(self, url):
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
            raise Exception("request failed", r.status_code)
        return self.parse_shoes_detail(r.content)



    # def process_one_product_new(self, url):
    #     r = Render(url)
    #     result = r.frame.toHtml()
    #     formatted_result = str(result.toAscii())
    #     tree = html.fromstring(formatted_result)
    #     print tree


    def parse_shoes_detail(self, content):
        try:
            doc = html.fromstring(content)
            doc.make_links_absolute('http://www.k3.cn')
            root = doc.getroottree()

            detail = {}
            pictures = []
            for li in root.xpath('.//div[@class="picture_box"]/div[@class="picture"]/ul[@class="tb-thumb"]/li'):
                _img = li.xpath('.//img')[0]
                pictures.append(_img.attrib['big'].strip())

            detail["pictures"] = ";".join(pictures)

            _detail = root.xpath('.//div[@class="picture_box"]/div[@class="detailed_info"]')[0]
            _title = _detail.xpath('.//div[@class="title"]/div[@class="huohao"]')[0]
            if _title is not None and _title.text is not None:
                detail["title"] = _title.text.strip().replace(u"货号：", "")

            _category = _detail.xpath('.//div[@class="category"]/span[1]/span')[0]
            if _category is not None and _category.text is not None:
                detail["category"] = _category.text.strip()

            sizes = []
            for _size in _detail.xpath('.//div[@id="color-size-box"]/a[@class="sku-size"]'):
                if _size is not None and _size.text is not None:
                    sizes.append(_size.text.strip())
            detail["sizes"] = " ".join(sizes)

            skus = []
            for _sku in _detail.xpath('.//div[@id="color-size-box"]/div[@class="color_box"]/div[@class="color_item sku-color"]'):
                sku = {}
                _skuname = _sku.xpath('.//p[@class="title]')[0]
                if _skuname is not None and _skuname.text is not None:
                    sku["name"] = _skuname.text.strip()

                _skupic = _sku.xpath('.//img')[0]
                sku["picture"] = _skupic.attrib['src']
                skus.append(sku)
            detail["skus"] = json.dumps(skus)

            _starttime = _detail.xpath('.//div[@class="starting_time"]/span')
            if len(_starttime) == 4:
                detail["first_upload"] = _starttime[1].text.strip()
                detail["updated"] = _starttime[3].text.strip()
            else:
                detail["first_upload"] = ''
                detail["updated"] = ''

            details = {}
            for _detail in root.xpath('.//div[@class="picture_box"]/div[@class="info_list"]/div[@class="shoes_info"]/span'):
                content = _detail.attrib['title'].strip().replace(u"点击搜索：", "").split(":")
                details[content[0]] = content[1]

            detail["details"] = json.dumps(details)

            return detail
        except Exception as e:
            self.log.exception(e)
            raise e

def main(args=None):
    k = K3ShoesDetailClawler()
    k.run()


if __name__ == '__main__':
    main()