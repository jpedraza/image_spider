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


def main():
    get_dir_info('/Users/lufo/Downloads/renren')


if __name__ == '__main__':
    main()
