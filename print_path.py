# -*- coding: utf-8 -*-
__author__ = 'lufo'

import os


def get_path(root_path):
    """
    输出root_path下所有文件的绝对路径
    :param root_path: 根路径
    :return:
    """
    path_list = []
    for i, dir_info in enumerate(os.walk(root_path)):
        if i > 0:
            for filename in dir_info[2]:
                path_list.append(dir_info[0] + '/' + filename + ' ' + str(i))
    return path_list


def main():
    root_path = '/ssd_001/casia'
    path_list = get_path(root_path)
    with open('/ssd_001/train_val.txt', 'w') as fw:
        for path in path_list:
            fw.write(path)


if __name__ == '__main__':
    main()
