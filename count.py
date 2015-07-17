# -*- coding: utf-8 -*-
__author__ = 'lufo'

import os


def get_file_num(path):
    file_num = []  # 第i个元素为第i个文件夹下面的文件个数
    for i, dir_info in enumerate(os.walk(path)):
        if len(dir_info[0].split('/')) > 3:  # dir_info第一个元素为根目录的信息
            file_num.append(len(dir_info[2]))
    return file_num


def main():
    path = './sheying8'
    file_num = get_file_num(path)
    total_file = len(file_num)
    for num in set(file_num):
        temp = 0.0
        for i in file_num:
            if i == num:
                temp += 1
        print num, temp / total_file


if __name__ == '__main__':
    main()
