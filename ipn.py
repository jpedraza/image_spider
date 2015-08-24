# -*- coding: utf-8 -*-
__author__ = 'lufo'

import os
import requests
from bs4 import BeautifulSoup

root_url = 'http://ipn.li/'


def get_podcast_list():
    """
    获取ipn.li下面所有节目的链接
    :return: 列表，每个元素为一个节目的链接
    """
    global root_url
    podcast_list = []
    try:
        soup = BeautifulSoup(requests.get(root_url).content)
    except Exception, e:
        print e
    for item in soup.find_all('a', class_='showList__item__head'):
        podcast_list.append(os.path.join(root_url, item['href']))
    return podcast_list


def get_download_url_list(url):
    """
    获取一个节目已经播出的播客下载地址
    :param url: 节目主页
    :return: list，每个元素保存一个下载地址
    """
    download_url_list = []
    try:
        soup = BeautifulSoup(requests.get(url).content)
    except Exception, e:
        print e
    for item in soup.find_all('a', class_='button fa fa-download'):
        download_url_list.append(os.path.join(url, item['href']))
    return download_url_list


def save_audio(url, path, filename):
    """
    保存音频文件
    :param url: 音频文件路径
    :param path: 保存路径
    :param filename: 文件名
    """
    if not os.path.isdir(path):
        os.makedirs(path)
    with open(os.path.join(path, filename), 'wb') as fw:
        try:
            fw.write(requests.get(url).content)
        except Exception, e:
            print e


def main():
    path = '/Users/lufo/Music/IPN/'
    podcast_list = get_podcast_list()
    for podcast_url in podcast_list:
        save_path = os.path.join(path, podcast_url.split('/')[-2])
        download_url_list = get_download_url_list(podcast_url)
        for i, url in enumerate(download_url_list):
            save_audio(url, save_path, str(i) + '.mp3')


if __name__ == '__main__':
    main()
