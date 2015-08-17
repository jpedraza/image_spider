# -*- coding: utf-8 -*-
__author__ = 'lufo'

import requests
import json
import os
import subprocess
from multiprocessing.dummy import Pool as ThreadPool


def face_detection(img_path):
    """
    传入图片路径，判断图片中有没有人脸，使用YOLO
    :return: 有返回True，没有返回False
    """
    path = '/Users/lufo/Downloads/darknet/'
    os.chdir(path)
    a = subprocess.check_output('./darknet detection test ./yolo_test_1.cfg ./yolo_test_1_39000.weights ' + img_path,
                                shell=True)
    if 'aeroplane' in a:
        return True
    else:
        return False


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
                resp = requests.get(search_url, timeout=5, allow_redirects=False).content
                # print chardet.detect(resp.read())
                resp_js = json.loads(resp.decode('gb2312', errors='ignore'))
                if resp_js['data']:
                    # print len(resp_js['data'])
                    for x in resp_js['data'][:-1]:
                        try:
                            url_list.append(x['objURL'])
                        except Exception, e:
                            print e
            except Exception, e:
                print e
        if not os.path.isdir(path):
            os.mkdir(path)
        with open(path + keyword + '.txt', 'w') as fw:
            for url in uniqify(url_list):
                fw.write(url + '\n')


def save_img(img_url_list, path):
    for i, img_url in enumerate(img_url_list):
        img_path = path + str(i) + '.jpg'
        # print img_path
        with open(img_path, 'wb') as fw:
            try:
                fw.write(requests.get(img_url, timeout=5, allow_redirects=False).content)
            except Exception, e:
                print img_url
                print e


def save_all_img(begin=0, end=200000):
    file_list = []
    with open('names.txt') as fr:
        for keyword in fr:
            file_list.append((keyword.strip() + '.txt'))
    for file in file_list[begin:end]:
        img_url_list = []
        print './names/' + os.path.normcase(file)
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


def save_all_img_main(step=25, number_of_threads=4, begin=0):
    """
    并行保存所有图片
    :param step: 每个线程每次循环保存多少人的图片
    :param number_of_threads: 开启线程数
    :param begin: 从list的第几个元素开始抓取
    """
    keyword_list = []
    with open('names.txt') as fr:
        for keyword in fr:
            keyword_list.append(keyword.strip())
    end = len(keyword_list)
    pool = ThreadPool(number_of_threads)
    func = lambda x: save_all_img(x, x + step)
    for i in xrange(begin, end, step * number_of_threads):
        pool.map(func, xrange(i, i + step * number_of_threads, step))
    pool.close()
    pool.join()


def delete_img_without_face(begin=0, end=200000):
    """
    删除没有人脸的图片
    """
    file_list = []
    with open('names.txt') as fr:
        for keyword in fr:
            file_list.append((keyword.strip() + '.txt'))
    for file in file_list[begin:end]:
        path = '/Users/lufo/PycharmProjects/images/names/' + file.split('.txt')[0] + '/'
        # print path
        path_list = []
        for dir_info in os.walk(path):
            for filename in dir_info[2]:
                if '.jpg' in filename:
                    path_list.append(os.path.join(dir_info[0], filename))
        for img_path in path_list:
            print img_path
            if not face_detection(img_path):
                os.remove(img_path)


def delete_img_without_face_main(step=25, number_of_threads=8, begin=0):
    """
    并行删除没有人脸的图片
    """
    keyword_list = []
    with open('names.txt') as fr:
        for keyword in fr:
            keyword_list.append(keyword.strip())
    end = len(keyword_list)
    pool = ThreadPool(number_of_threads)
    func = lambda x: delete_img_without_face(x, x + step)
    for i in xrange(begin, end, step * number_of_threads):
        pool.map(func, xrange(i, i + step * number_of_threads, step))
    pool.close()
    pool.join()


if __name__ == '__main__':
    # save_all_img()
    delete_img_without_face_main()
    # save_img_url_main(number_of_threads=1, begin=0)
    # save_all_img()
