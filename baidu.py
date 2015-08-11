# -*- coding: utf-8 -*-
__author__ = 'lufo'

import requests
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
        search_url = 'http://image.baidu.com/i?tn=baiduimagejson&ie=utf-8&width=&height=&word=%s&rn=60&pn=%s' % (
        keyword, str(i * 60)) # word为关键字，rn为显示的数量，pn为从第几张开始显示

        # print search_url
        try:
            resp = urllib2.urlopen(search_url)
            # print chardet.detect(resp.read())
            # print resp.read().decode('gb2312', errors='ignore')
            resp_js = json.loads(resp.read().decode('gb2312', errors='ignore'))
            if resp_js['data']:
                # print len(resp_js['data'])
                for x in resp_js['data'][:-1]:
                    try:
                        # print x['objURL']
                        url_list.append(x['objURL'])
                    except Exception, e:
                        print e
        except Exception, e:
            print e
    if not os.path.isdir(path):
        os.mkdir(path)
    with open(path + keyword + '.txt', 'w') as fw:
        for url in set(url_list):
            fw.write(url + '\n')


def save_all_img_url(begin=0):
    keyword_list = []
    with open('names.txt') as fr:
        for keyword in fr:
            keyword_list.append(keyword.strip())
    for keyword in keyword_list[begin:]:
        print keyword
        save_img_url(keyword)


def save_img(img_url_list, path):
    for i, img_url in enumerate(img_url_list):
        with open(path + str(i) + '.jpg', 'wb') as fw:
            try:
                fw.write(requests.get(img_url, timeout=5, allow_redirects=False).content)
            except Exception, e:
                print img_url
                print e


def save_all_img(begin=0):
    file_list = []
    with open('names.txt') as fr:
        for keyword in fr:
            file_list.append((keyword.strip() + '.txt'))
    for file in file_list[begin:]:
        img_url_list = []
        with open('./names/' + os.path.normcase(file)) as fr:
            for url in fr:
                img_url_list.append(url.strip())
        path = './names/' + file.split('.txt')[0] + '/'
        if not os.path.isdir(path):
            os.mkdir(path)
        save_img(img_url_list, path)


if __name__ == '__main__':
    save_all_img_url()
    # save_all_img()
