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

session = None


def get_sheying8_url(**kwargs):
    """
    获取http://www.sheying8.com/photolist/human下的所有写真的url，存在sheying8.txt中
    :param kwargs:
    :return:
    """
    global session
    if session == None:
        session = requests.session()
    s = session
    url_list = []
    for i in xrange(2060):
        print i
        r = s.get('http://www.sheying8.com/photolist/human/' + str(i + 1) + '.html')
        soup = BeautifulSoup(r.content, 'lxml')
        for item in soup.find_all('div', class_='padder-v'):
            try:
                url = 'http://www.sheying8.com' + item.find('a', class_='text-ellipsis')['href'] + '\n'
                url_list.append(url)
            except:
                print 'url is None'
    filename = 'sheying8.txt'
    with open(filename, 'w') as fw:
        for url in url_list:
            fw.write(url)


def craw_image(**kwargs):
    """
    将sheying8中所有图片保存下来，每个文件夹保存一个人的图片
    :param kwargs:
    :return:
    """
    global session
    if session == None:
        session = requests.session()
    s = session
    url_list = []
    filename = 'sheying8.txt'
    with open(filename) as fr:
        for url in fr:
            url_list.append(url.strip())
    for url in url_list:
        filename = url[len('http://www.sheying8.com/uploadfile/user/'):len(
            'http://www.sheying8.com/uploadfile/user/2013-11/174263') - 1]
        path = './sheying8/' + filename
        if not os.path.exists(path):
            os.makedirs(path)
        print filename
        r = s.get(url)
        soup = BeautifulSoup(r.content, 'lxml')
        item = soup.find('div', class_='photos-content')
        if item:
            for i, img in enumerate(item.find_all('img', class_='img-thumbnail')):
                img_url = 'http://www.sheying8.com' + img['src']
                save_image(img_url, path + '/' + str(i) + '.jpg')


def save_image(img_url, path, **kwargs):
    """
    输入图片url，储存在对应路径
    :param img_url: 图片url
    :param kwargs: 路径，包括文件名
    :return:
    """
    global session
    if session == None:
        session = requests.session()
    s = session
    with open(path, 'wb') as fw:
        fw.write(s.get(img_url).content)


def main():
    # get_sheying8_url()
    craw_image()


if __name__ == '__main__':
    main()
