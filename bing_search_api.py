# -*- coding: utf-8 -*-
__author__ = 'lufo'

import requests  # Get from https://github.com/kennethreitz/requests
import string
import os
import time
from multiprocessing.dummy import Pool as ThreadPool

KEY = "kGHwFzi2I1zI8dA8GiRRHtGsrW8qqUgLXLKUatCUpn8"

header = {
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36",
    'Host': "www.xingyun.cn",
    'Referer': "http://www.xingyun.cn/",
    'X-Requested-With': "XMLHttpRequest"
}


class BingSearchAPI():
    bing_api = "https://api.datamarket.azure.com/Data.ashx/Bing/Search/v1/Composite?"

    def __init__(self, key):
        self.key = key

    def replace_symbols(self, request):
        # Custom urlencoder.
        # They specifically want %27 as the quotation which is a single quote '
        # We're going to map both ' and " to %27 to make it more python-esque
        request = string.replace(request, "'", '%27')
        request = string.replace(request, '"', '%27')
        request = string.replace(request, '+', '%2b')
        request = string.replace(request, ' ', '%20')
        request = string.replace(request, ':', '%3a')
        return request

    def search(self, sources, query, params):
        ''' This function expects a dictionary of query parameters and values.
            Sources and Query are mandatory fields.
            Sources is required to be the first parameter.
            Both Sources and Query requires single quotes surrounding it.
            All parameters are case sensitive. Go figure.

            For the Bing Search API schema, go to http://www.bing.com/developers/
            Click on Bing Search API. Then download the Bing API Schema Guide
            (which is oddly a word document file...pretty lame for a web api doc)
        '''
        request = 'Sources="' + sources + '"'
        request += '&Query="' + str(query) + '"'
        for key, value in params.iteritems():
            request += '&' + key + '=' + str(value)
        request = self.bing_api + self.replace_symbols(request)
        return requests.get(request, auth=(self.key, self.key)).json()


def save_img_url(query, filename, key=KEY):
    """
    保存对应查询的所有图片的url，每个查询的图片保存在一个文件，一行一个url
    :param query: 查询关键字
    :param filename: 保存的文件名，包括路径
    :param key: api key
    """
    image_url_list = []
    bing = BingSearchAPI(key)
    params = {'ImageFilters': '"Face:Face"',
              '$format': 'json',
              '$top': 50,
              '$skip': 0}
    try:
        results = bing.search('image', query, params)  # requests 1.0+
        for image_url in results['d']['results'][0]['Image']:
            image_url_list.append(image_url['MediaUrl'])
    except Exception, e:
        print e
    with open(filename, 'w') as fw:
        for image_url in image_url_list:
            fw.write(image_url.encode('utf8') + '\n')


def save_all_img_url(query_list):
    """
    保存query_list中所有的查询的img url
    :param query_list: 列表，每个元素为一个查询
    """
    path = './europe_orig_sorted/'
    if not os.path.isdir(path):
        os.mkdir(path)
    for query in query_list:
        filename = path + query + '.txt'
        save_img_url(query, filename)


def save_img(img_url_list, path):
    """
    输入图片url_list，储存在对应路径
    :param img_url: 图片url list
    :param path: 保存的路径
    """
    global header
    for i, img_url in enumerate(img_url_list):
        with open(path + str(i) + '.jpg', 'wb') as fw:
            try:
                fw.write(requests.get(img_url, timeout=5, headers=header, allow_redirects=False).content)
            except Exception, e:
                print img_url
                print e
            time.sleep(0.1)


def save_all_img(file_list):
    """
    file_list每个元素为一个文件的文件名(包括路径)，文件中每行保存一个图片url，保存所有url
    :param file_list: file_list每个元素为一个文件的文件名，文件中每行保存一个图片url
    """
    for filename in file_list:
        img_url_list = []
        with open(filename) as fr:
            for img_url in fr.readlines():
                img_url_list.append(img_url.strip())
        path = filename.split('.txt')[0] + '/'
        if not os.path.isdir(path):
            os.mkdir(path)
        save_img(img_url_list, path)


def save_img_url_main():
    query_list_file = './europe_orig_sorted.txt'  # 查询文件名，每行的第一个字符串为查询内容
    query_list = []
    with open(query_list_file) as fr:
        for query in fr.readlines():
            query_list.append(query.strip().split()[0].replace('_', ' '))
    save_all_img_url(query_list[9900:])


def save_img_main(step=25, number_of_threads=4, begin=0):
    """
    并行保存所有图片
    :param step: 每个线程每次循环保存多少人的图片
    :param number_of_threads: 开启线程数
    :param begin: 从list的第几个元素开始抓取
    """
    query_list_file = './europe_orig_sorted.txt'  # 查询文件名，每行的第一个字符串为查询内容
    query_list = []
    with open(query_list_file) as fr:
        for query in fr.readlines():
            query_list.append(query.strip().split()[0].replace('_', ' '))
    file_list = []
    for query in query_list:
        file_list.append('./europe_orig_sorted/' + query + '.txt')
    end = len(file_list)
    pool = ThreadPool(number_of_threads)
    for i in xrange(begin, end, step * number_of_threads):
        pool.map(save_all_img, [file_list[i + j * step:i + (j + 1) * step] for j in xrange(number_of_threads)])
    pool.close()
    pool.join()


def get_file_num(path='./europe_orig_sorted/'):
    """
    获得path下文件个数
    :param path: 路径
    """
    for i, dir_info in enumerate(os.walk(path)):
        print len(dir_info[2]) - 1


if __name__ == "__main__":
    # save_img_url_main()
    save_img_main(number_of_threads=4)
    # get_file_num()
