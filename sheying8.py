# -*- coding: utf-8 -*-
__author__ = 'lufo'

import os
import requests
import time
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as ThreadPool

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
        try:
            r = s.get('http://www.sheying8.com/photolist/human/' + str(i + 1) + '.html', timeout=1)
        except Exception, e:
            print e
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


def craw_image(url_list):
    """
    将sheying8中所有图片保存下来，每个文件夹保存一个人的图片
    :param url_list: 要抓取的url列表
    :return:
    """
    global session
    if session == None:
        session = requests.session()
    s = session
    for url in url_list:
        filename = url[len('http://www.sheying8.com/uploadfile/user/'):len(
            'http://www.sheying8.com/uploadfile/user/2013-11/174263') - 1]
        path = './sheying8/' + filename
        if not os.path.exists(path):
            os.makedirs(path)
        print filename
        try:
            r = s.get(url, timeout=1)
        except Exception, e:
            print e
        soup = BeautifulSoup(r.content, 'lxml')
        item = soup.find('div', class_='photos-content')
        if item:
            for i, img in enumerate(item.find_all('img', class_='img-thumbnail')):
                img_url = 'http://www.sheying8.com' + img['src']
                save_image(img_url, path + '/' + str(i) + '.jpg')
                time.sleep(0.01)


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
        try:
            fw.write(s.get(img_url, timeout=1).content)
        except Exception, e:
            print e


def craw_image_parallel(url_list, step, number_of_threads, begin=0):
    """
    并行抓取图片
    :param url_list: 要抓取的用户url list
    :param step: 每个线程每次抓取多少用户
    :param number_of_threads: 线程数
    :param begin: 从url_list第几个开始
    :return:
    """
    func = lambda x: craw_image(url_list[x:x + step])
    pool = ThreadPool(number_of_threads)
    for i in xrange(begin, len(url_list), step * number_of_threads):
        pool.map(func, xrange(i, i + step * number_of_threads, step))
    pool.close()
    pool.join()


def main():
    # get_sheying8_url()
    url_list = []
    filename = 'sheying8.txt'
    with open(filename) as fr:
        for url in fr:
            url_list.append(url.strip())
    craw_image_parallel(url_list, 100, 4)


if __name__ == '__main__':
    main()
