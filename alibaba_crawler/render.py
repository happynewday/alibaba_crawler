# coding: utf8

import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import *
from PyQt4.QtNetwork import *

class Render(QWebPage):
    def __init__(self, url):
        self.app = QApplication(sys.argv)
        QWebPage.__init__(self)
        self.loadFinished.connect(self._loadFinished)
        self.mainFrame().load(QUrl(url))
        self.app.exec_()

    def _loadFinished(self, result):
        self.frame = self.mainFrame()
        self.app.quit()

class Browser(QWebView):
    def __init__(self, my_cookie_dict):
        super(Browser, self).__init__()
        # 将字典转化成QNetworkCookieJar的格式
        self.cookie_jar = QNetworkCookieJar()
        cookies = []
        for key, values in my_cookie_dict.items():
            my_cookie = QNetworkCookie(QByteArray(key), QByteArray(values))
            my_cookie.setDomain('.k3.cn')
            cookies.append(my_cookie)
        self.cookie_jar.setAllCookies(cookies)
        # 如果没有在前面设置domain,那么可以在这里指定一个url作为domain
        # self.cookie_jar.setCookiesFromUrl(cookies, QUrl('https://www.baidu.com/'))

        # 最后cookiejar替换完成
        self.page().networkAccessManager().setCookieJar(self.cookie_jar)

def customuseragent(url):
    print 'called for %s' % url
    return 'custom ua'

if __name__ == '__main__':
    app = QApplication(sys.argv)

    cookie_str = 'UM_distinctid=17eddf2437f110-01b3bd3a28c42b-f791539-154ac4-17eddf2438065c; __51vcke__JH8oID4DYgzN67sY=b7465b70-d5fa-532b-8b69-9569dbcea25d; __51vuft__JH8oID4DYgzN67sY=1644401149573; _ati=2800730497315; login_captcha_word=02d34849bb1148a1deb070b3aa297ee9; login_captcha_time=1645446180779; login_captcha_image=%3Cimg+id%3D%22captcha%22+src%3D%22%2Fimages%2Fcaptcha%2F1645446180779.png%22+width%3D%2280%22+height%3D%2230%22+style%3D%22border%3A0%3B%22+%2F%3E; login_captcha_hash=cec5cc32aadb5348483371e3b0d8e492; daily_login=1; user_user_id=3227710; user_login_time=2022-02-21+20%3A23%3A20; user_login_ip=94.177.118.48; user_username=17376543972%40k3.cn; user_type=0; user_is_user_login=1; user_login_type=passport; user_hash=fed31865cae4ed10104c5e74f3cc83e3; k3cn=dXNlcl9pZD0zMjI3NzEwJnR5cGU9MCZ1c2VybmFtZT0xNzM3NjU0Mzk3MkBrMy5jbiZ0PTE2NDU0NDYyMDAmaGFzaD1kMmNjYTRkMDYzYzljMzU1ODMwMDIxMmQ2NTQ0YmYyMg%3D%3D; acw_tc=2f624a1316454511920738834e44b221dc30846d3705ebcf92ff54e89ef643; CNZZDATA1278071117=910611069-1644399317-null%7C1645441068; __51uvsct__JH8oID4DYgzN67sY=10; __vtins__JH8oID4DYgzN67sY=%7B%22sid%22%3A%20%223b51c889-2d13-51c5-bf44-b6d0eb4f8d54%22%2C%20%22vd%22%3A%203%2C%20%22stt%22%3A%20399174%2C%20%22dr%22%3A%20214781%2C%20%22expires%22%3A%201645453394497%2C%20%22ct%22%3A%201645451594497%7D'
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"

    cookies = {}
    for line in cookie_str.split(';'):
        name, value = line.strip().split('=', 1)
        cookies[name] = value

    url = 'http://www.k3.cn/p/ooeebbdmbop.html'
    request = QNetworkRequest()
    request.setUrl(QUrl(url))
    request.setRawHeader("User-Agent", USER_AGENT)

    browser = Browser(cookies)
    browser.page().userAgentForUrl = customuseragent

    browser.load(QUrl('http://www.k3.cn/p/ooeebbdmbop.html'))
    browser.show()
    app.exec_()
