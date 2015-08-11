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
from multiprocessing.dummy import Pool as ThreadPool


def uniqify(seq, idfun=None):
    # list 去重
    # order preserving
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        if seen.has_key(marker): continue
        seen[marker] = 1
        result.append(item)
    return result


def save_img_url(keyword_list, number_of_img=2000, path='./names/'):
    for keyword in keyword_list:
        print keyword
        pn = number_of_img / 60 + 1
        url_list = []
        for i in xrange(pn):
            search_url = 'http://image.baidu.com/i?tn=baiduimagejson&ie=utf-8&width=&height=&word=%s&rn=60&pn=%s' % (
                keyword, str(i * 60))  # word为关键字，rn为显示的数量，pn为从第几张开始显示

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


def save_img_url_main(step=100, number_of_threads=4, begin=800):
    keyword_list = []
    with open('names.txt') as fr:
        for keyword in fr:
            keyword_list.append(keyword.strip())
    end = len(keyword_list)
    pool = ThreadPool(number_of_threads)
    for i in xrange(begin, end, step * number_of_threads):
        pool.map(save_img_url, [keyword_list[i + j * step:i + (j + 1) * step] for j in xrange(number_of_threads)])
    pool.close()
    pool.join()


if __name__ == '__main__':
    save_img_url_main()
    # save_all_img()
