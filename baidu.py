# -*- coding: utf-8 -*-
__author__ = 'lufo'

import md5
import base64
import urllib2
import urllib
import json
import random
import os
import sys
import chardet


def save_img_url(keyword, number_of_img=2000, path='./names/'):
    pn = 2000 / 60 + 1
    url_list = []
    for i in xrange(pn):
        search_url = 'http://image.baidu.com/i?tn=baiduimagejson&width=&height=&word=%s&rn=60&pn=%s' % (keyword, str(i))
        # print search_url
        resp = urllib2.urlopen(search_url)
        # print chardet.detect(resp.read())
        # print resp.read().decode('gb2312', errors='ignore')
        resp_js = json.loads(resp.read().decode('gb2312', errors='ignore'))
        if resp_js['data']:
            # print len(resp_js['data'])
            for x in resp_js['data'][:-1]:
                try:
                    url_list.append(x['objURL'])
                except Exception, e:
                    print e
    if not os.path.isdir(path):
        os.mkdir(path)
    with open(path + keyword + '.txt', 'w') as fw:
        for url in set(url_list):
            fw.write(url + '\n')


def save_all_img_url():
    keyword_list = []
    with open('names.txt') as fr:
        for keyword in fr:
            keyword_list.append(keyword.strip())
    for keyword in keyword_list:
        print keyword
        save_img_url(keyword)


if __name__ == '__main__':
    save_all_img_url()
