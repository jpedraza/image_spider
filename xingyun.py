# -*- coding: utf-8 -*-
__author__ = 'lufo'

import os
import re
import time
import json
import platform
import requests
import html2text
from bs4 import BeautifulSoup
import sys
import datetime
import ConfigParser

session = None
header = None
cookies = None


def create_session():
    global session, header, cookies
    header = {
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36",
        'Host': "www.xingyun.cn",
        'Referer': "http://www.xingyun.cn/",
        'X-Requested-With': "XMLHttpRequest"
    }

    cf = ConfigParser.ConfigParser()
    cf.read("xingyun_config.ini")
    cookies = cf._sections['cookies']
    cookies = dict(cookies)
    mobile = cf.get("info", "mobile")
    pwd = cf.get("info", "pwd")
    login_data = {"mobile": mobile, "pwd": pwd}
    session = requests.session()
    r = session.post('http://www.xingyun.cn/login_mobileLogin.action', data=login_data, headers=header)


def test():
    global session, header, cookies
    if session == None:
        create_session()
    s = session
    data = {'toUserId': 200200901208}
    header['Referer'] = 'http://www.xingyun.cn/u/200200901208/saying/'
    r = s.post('http://www.xingyun.cn/followUpdate_addFollow.action', data=data, headers=header)
    print r


def main():
    # test()
    if session == None:
        create_session()
    s = session
    r = s.get('http://www.xingyun.cn/u/200200901208/saying/')
    print r.content


if __name__ == '__main__':
    main()
