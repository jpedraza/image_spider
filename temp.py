# -*- coding: utf-8 -*-
__author__ = 'lufo'

import os
from itertools import combinations

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


def landmark_49_to_31(landmark49):
    """
    将49个关键点映射到31个
    :param landmark49: list，前49个元素为x坐标，后49个为y坐标
    :return: list，前31个元素为x坐标，后31个为y坐标
    """
    landmark31 = []
    index_list = [10, 13, 14, 16, 18] + range(19, 31) + range(31, 43) + [44, 47]
    for index in index_list:
        landmark31.append(landmark49[index])
    for index in index_list:
        landmark31.append(landmark49[index + 49])
    return landmark31


def landmark_68_to_31(landmark68):
    """
    将68个关键点映射到31个
    :param landmark68: list，前68个元素为x坐标，后68个为y坐标
    :return: list，前31个元素为x坐标，后31个为y坐标
    """
    landmark31 = []
    index_list = [27, 30, 31, 33, 35] + range(36, 48) + range(48, 60) + [63, 67]
    for index in index_list:
        landmark31.append(landmark68[index])
    for index in index_list:
        landmark31.append(landmark68[index + 68])
    return landmark31


def convent_landmark():
    """
    整理landmark_europe_49.txt的信息，
    """
    path = '/Users/lufo/Downloads/LFW(Xing)/'
    filename = 'landmark_europe_49.txt'
    with open(os.path.join(path, filename)) as fr:
        for line in fr:
            img_file_path, points = line.strip().split(' ')
            points_list = points.split(',')[:-1]
            if len(points_list) > 1:
                with open(os.path.join(path, 'img_path.txt'), 'a') as fw:
                    fw.write(img_file_path + '\n')
                points_list = landmark_49_to_31(points_list)
                with open(os.path.join(path, 'landmark_europe_31.txt'), 'a') as fw:
                    for point in points_list:
                        fw.write(point + ' ')
                    fw.write('\n')


def main():
    # get_dir_info('/Users/lufo/Downloads/renren')
    path = '/Users/lufo/Downloads/LFW(Xing)/'
    mean_point = landmark_68_to_31(get_lfw_mean())
    with open(os.path.join(path, 'lfw_mean_31.txt'), 'w') as fw:
        for point in mean_point:
            fw.write(str(point) + ' ')
            # convent_landmark()