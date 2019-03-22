# coding: utf8 
import json
import urllib
import hashlib
import requests
from pyobject import PyObject


class BaiduMapApi(PyObject):
    def __init__(self):
        super(BaiduMapApi, self).__init__()
        self.ak = 'mW7E7wLyiRNIZo0iQiDoA3Hib6C1s5T1'
        self.sk = '9kOcBMXEBknyZkxDNakBMpa3hpQUULcY'


    def decode(self, latitude, longitude):
        try:
            queryStr = '/geocoder/v2/?location={},{}&output=json&ak={}'.format(
                    latitude, longitude, self.ak)
            encodedStr = urllib.parse.quote(queryStr, safe="/:=&?#+!$,;'@()*[]")
            rawStr = encodedStr + self.sk
            sn = hashlib.md5(urllib.quote_plus(rawStr).encode(
                    'utf8')).hexdigest()
            url = 'http://api.map.baidu.com{}&sn={}'.format(queryStr, sn) 
            r = requests.get(url)
            c = r.json()['result']['addressComponent']
            return c
        except Exception as e:
            self.log.exception(e)
            return None


    def get_lng_lat(self, address):
        try:
            queryStr = '/geocoder/v2/?address={}&output=json&ak={}'.format(
                    address, self.ak)
            encodedStr = urllib.parse.quote(queryStr, safe="/:=&?#+!$,;'@()*[]")
            rawStr = encodedStr + self.sk
            sn = hashlib.md5(urllib.parse.quote_plus(rawStr).encode(
                    'utf8')).hexdigest()
            url = 'http://api.map.baidu.com{}&sn={}'.format(queryStr, sn) 
            r = requests.get(url)
            return r.json()['result']['location']
        except Exception as e:
            self.log.exception(e)
        return None

