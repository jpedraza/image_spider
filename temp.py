# -*- coding: utf-8 -*-
__author__ = 'lufo'

import os
import requests
from bs4 import BeautifulSoup


def get_dir_info(path):
    """
    获取文件夹每个子文件夹中文件数
    :param path: 文件夹路径
    :return: list，每个元素为子文件夹文件数
    """
    file_num_list = []
    for i, dir_info in enumerate(os.walk(path)):
        if i > 0:
            print len(dir_info[2])
            file_num_list.append(len(dir_info[2]))
    return file_num_list


def get_lfw_mean():
    """
    返回lfw关键点的均值
    """
    file_path = '/Users/lufo/Downloads/LFW(Xing)/landmark68.txt'
    point_list = []
    with open(file_path) as fr:
        for line in fr:
            point_list.append(map(float, line.strip().split()))
    mean_point = map(lambda x: x / len(point_list),
                     reduce(lambda x, y: [x[i] + y[i] for i in xrange(len(x))], point_list))
    return mean_point


def main():
    # get_dir_info('/Users/lufo/Downloads/renren')
    print get_lfw_mean()


if __name__ == '__main__':
    main()
