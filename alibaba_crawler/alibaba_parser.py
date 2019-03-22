# coding: utf8
import re
import json
from lxml import html
from lxml import etree
from html.parser import HTMLParser
from pyobject import PyObject


_reo_space = re.compile(r'\s+', re.I|re.S)
_reo_bg = re.compile(r'background-image:url\((.+?)\);', re.I)
_reo_contact = re.compile(r'联系人：(.+)$')
_reo_phone = re.compile(r'(固话|手机号码)：(.+)$')
_reo_item = re.compile(r'detail\.1688\.com/offer/(\d+).html', re.I|re.S)


class AlibabaParser(PyObject):
    def __init__(self):
        PyObject.__init__(self)
        self.html_parser = HTMLParser()


    def parse_search_result(self, content):
        try:
            doc = html.fromstring(content)
            doc.make_links_absolute('https://www.1688.com')
            root = doc.getroottree()
            
            sellers = []
            for div in root.xpath('.//div[@class="list-item-left"]/div[@class="wrap"]'):
                seller = {}
                _a = div.xpath('.//a[@class="list-item-title-text"]')[0]
                seller['url'] = _a.attrib['href'].split('?')[0]
                seller['title'] = _a.text.strip()
                _spans = div.xpath('.//div[@class="detail-float-items"]/a/span')
                products = [(x.text or '').strip().strip(';') for x in _spans]
                seller['products'] = ','.join([x for x in products if x])
                _a = div.xpath('.//a[@class="sm-offerResult-areaaddress"]')[0]
                seller['address'] = _a.attrib['title'].strip()
                _b = div.xpath('./div[@class="list-item-detail"]/div[@class="detail-right"]/div[1]/b')[0]
                seller['businessType'] = (_b.text or '').strip()
                sellers.append(seller)
            _inputs = root.xpath('.//input[@id="jumpto"]')
            pages = int(_inputs[0].attrib['data-max']) if _inputs else 1
            return (sellers, pages)
        except Exception as e:
            self.log.exception(e)
            return None
    
    
    def parse_credit_detail(self, content):
        try:
            doc = html.fromstring(content)
            doc.make_links_absolute('https://www.1688.com')
            root = doc.getroottree()
            
            info = {}
            div = root.xpath('.//div[@id="site_header"]')[0]
            _div = div.xpath('.//div[@class="m-body"]/div[@class="m-content"]/div[1]')[0]
            m = _reo_bg.search(_div.attrib['style'])
            info['image'] = m.group(1) if m else ''

            _lst = root.xpath('.//span[@class="contact-info"]')
            if _lst:
                m = _reo_contact.match(_lst[0].text.strip())
                info['contact'] = m.group(1).strip()

            numbers = set()
            _lst = root.xpath('.//span[@class="tip-info phone-num"]')
            if _lst:
                m = _reo_phone.match(_lst[0].text)
                numbers.add(m.group(2).strip())
            _lst = root.xpath('.//input[@name="hiddenMobileNo"]')
            if _lst:
                n = _lst[0].attrib['value'].strip()
                if n:
                    numbers.add(n)
            numbers = list(numbers)
            if numbers:
                info['phoneNumber1'] = numbers[0]
            if len(numbers) > 1:
                info['phoneNumber2'] = numbers[1]

            div = root.xpath('.//div[@id="J_COMMON_CompanyRegisterInfoBox"]')[0]
            keys = []
            for td in div.xpath('.//td[@class="td-key"]'):
                keys.append(td.text_content().strip())
            values = []
            for td in div.xpath('.//td[@class="td-value"]'):
                values.append(td.text_content().strip())
            ps = zip(keys, values)
            for k,v in ps:
                if not v:
                    continue
                if k.find(r'统一社会') == 0:
                    info['creditCode'] = v
                if k.find(r'公司名称') == 0:
                    info['title'] = v

            return info
        except Exception as e:
            self.log.exception(e)
            return None


    def parse_offer_list(self, content):
        try:
            doc = html.fromstring(content)
            doc.make_links_absolute('https://www.1688.com')
            root = doc.getroottree()
            
            items = []
            for div in root.xpath('.//ul[@class="offer-list-row"]/li[@class="offer-list-row-offer"]'):
                item = {}
                _a = div.xpath('./div[@class="image"]/a')[0]
                href = _a.attrib['href'].split('?')[0]
                m = _reo_item.search(href)
                item['id'] = int(m.group(1))
                item['url'] = 'https://m.1688.com/offer/{}.html?'.format(
                        item['id'])
                item['title'] = _a.attrib['title'].strip()
                _img = div.xpath('./div[@class="image"]/a/img')[0]
                item['image'] = _img.attrib['data-lazy-load-src']
                if item['image'].find('//') == 0:
                    item['image'] = 'https:' + item['image']
                items.append(item)
            ems = root.xpath('.//em[@class="page-count"]')
            pages = int(ems[0].text.strip()) if ems else 1
            return (items, pages)
        except Exception as e:
            self.log.exception(e)
            return None


    def formats(self, s):
        s = self.html_parser.unescape(s)
        return s.strip()


    def parse_item_page(self, content):
        try:
            info = {}
            doc = html.fromstring(content)
            doc.make_links_absolute('https://www.1688.com')
            root = doc.getroottree()
            
            attribs = {}
            for e in root.xpath('.//span[@class="detail-attribute-item"]'):
                k = e.attrib['data-offer-attribute-name']
                v = e.attrib['data-offer-attribute-value']
                attribs[k] = self.formats(v)
            barcode = attribs.get('商品条形码', '')
            if barcode.isalnum():
                info['barcode'] = barcode
            uw = attribs.get('净重', attribs.get('净重（规格）', ''))
            if uw.isdigit():
                info['unitWeight'] = int(uw)
            info['global'] = 1 if attribs.get('是否进口', '') == '是' else 0
            info['origin'] = attribs.get('原产地', attribs.get('原产国/地区', ''))
            
            component_data = {}
            for s in re.findall(r'<script type="component-data/json" data-module-hidden-data-area="Y">(.+?)</script>', 
                    content, re.I|re.S):
                try:
                    component_data.update(json.loads(s))
                except Exception as e:
                    continue
            info['unit'] = component_data['unit']
            skus = []
            for k,m in component_data.get('skuMap', {}).items():
                sku = {'name': self.formats(k)}
                sku['saleCount'] = m.get('saleCount', 0)
                sku['canBookCount'] = m.get('canBookCount', 0)
                v = m.get('discountPrice', '')
                if v:
                    sku['price'] = float(v)
                v = m.get('retailPrice', '')
                if v:
                    sku['retailPrice'] = float(v)
                skus.append(sku)
            if skus:
                info['skus'] = json.dumps(skus, ensure_ascii=False)
                prices = [x['price'] for x in skus if 'price' in x 
                        and x['canBookCount']]
                if prices:
                    info['bottomPrice'] = min(prices)
                    info['ceilingPrice'] = max(prices)

            component = {}
            for s in re.findall(r'<script type="component/json" data-module-hidden-data-area="Y">(.+?)</script>', 
                    content, re.I|re.S):
                try:
                    component.update(json.loads(s))
                except Exception as e:
                    continue
            ranges = []
            prices = []
            for r in component['showPriceRanges']:
                try:
                    price = r['convertPrice']
                    prices.append(float(price))
                except Exception as e:
                    pass
                mobj = re.match(r'(\d+)-(\d+)$', r['range'])
                if mobj:
                    ranges.append((int(mobj.group(1)), price))
                    continue
                mobj = re.match(r'&ge;(\d+)$', r['range'])
                if mobj:
                    ranges.append((int(mobj.group(1)), price))
                    continue
                if r['range'].isdigit():
                    ranges.append((int(r['range']), price))
                    continue
                self.log.error('无法识别范围[{}]'.format(r['range']))
                return None
            if ranges:
                info['priceRange'] = json.dumps(ranges)
                info['beginAmount'] = ranges[0][0]
                if prices:
                    info['bottomPrice'] = min(prices)
                    info['ceilingPrice'] = max(prices)

            spans = root.xpath('.//span[@class="detail-logistics-text"]')
            info['freightLocation'] = spans[0].text_content().strip()
            info['freightCost'] = spans[1].text_content().strip()
            mobj = re.search(r'¥([\d.]+)', info['freightCost'], re.I)
            if mobj:
                info['freightCost'] = mobj.group(1)

            areas = {}
            for e in root.xpath('.//div[@class="detail-tradedata-data-areas"]/input'):
                for p in [('data-tradedata-1st-name', 'data-tradedata-1st-value'), 
                        ('data-tradedata-2nd-name', 'data-tradedata-2nd-value')]:
                    k = e.attrib.get(p[0], '')
                    v = e.attrib.get(p[1], '')
                    if k and v:
                        areas[k] = v
            info['saleAmount']  = int(areas.get('近30天成交', 0))
            info['buyerAmount'] = int(areas.get('近30天采购', 0))
            info['repeatBuyAmountRaito'] = float(
                    areas.get('复购率', '0').strip('%'))

            es = root.xpath('.//input[@name="postCategoryId"]')
            if es:
                info['categoryId'] = int(es[0].attrib['value'])

            promotions = []
            for e in root.xpath('.//div[@class="preference-view-item"]'):
                title = e.xpath('.//span[@class="view-title-text"]')[0].text.strip()
                for e2 in e.xpath('./div[contains(@class, "preference-view-content")]/div'):
                    cls = e2.attrib['class']
                    if cls.find('preference-card-item') != -1:
                        desc = e2.xpath('./div[@class="card-line-text line-text"]')[0].text.strip()
                        promotions.append({'type': title, 'desc': desc, 
                                'time': ''})
                    elif cls.find('preference-coupon-item') != -1:
                        _div = e2.xpath('./div[@class="prefence-coupon-info"]')[0]
                        coupon_type = _div.xpath('.//span[@class="coupon-type"]')[0].text.strip()
                        texts = _div.xpath('./div[@class="coupon-info-text"]')
                        promotions.append({'type': coupon_type, 
                                'desc': texts[0].text.strip(), 
                                'time': texts[1].text.strip()})
                    elif cls.find('preference-activity-item') != -1:
                        _div = e2.xpath('./div[@class="prefence-activity-info"]')[0]
                        _desc = _div.xpath('./div[1]')[0].text.strip()
                        _time = _div.xpath('./div[2]')[0].text.strip()
                        promotions.append({'type': title, 'desc': _desc, 
                                'time': _time})
            if promotions:
                info['promotions'] = json.dumps(promotions, ensure_ascii=False)

            if info.get('bottomPrice', ''):
                if info['bottomPrice'] == info['ceilingPrice']:
                    info['refPrice'] = '{}'.format(info['bottomPrice'])
                else:
                    info['refPrice'] = '{}-{}'.format(
                            info['bottomPrice'], info['ceilingPrice'])

            return info
        except Exception as e:
            self.log.exception(e)
            return None

