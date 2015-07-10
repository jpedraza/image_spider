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
import ConfigParser
import time

session = None
header = None
cookies = None


def create_session():
    """
    建立与星云网连接，模拟登录
    :return:
    """
    global session, header, cookies
    header = {
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36",
        'Host': "www.xingyun.cn",
        'Referer': "http://www.xingyun.cn/",
        'X-Requested-With': "XMLHttpRequest"
    }
    cf = ConfigParser.ConfigParser()
    cf.read("xingyun_config.ini")
    cookies = cf._sections['cookies']
    cookies = dict(cookies)
    mobile = cf.get("info", "mobile")
    pwd = cf.get("info", "pwd")
    login_data = {"mobile": mobile, "pwd": pwd}
    session = requests.session()
    session.post('http://www.xingyun.cn/login_mobileLogin.action', data=login_data, headers=header)


def get_top_user_url(**kwargs):
    """
    获取星云网top300用户的url，保存在xingyun_top300.txt中
    :param kwargs:
    :return:
    """
    global session, header, cookies
    if session == None:
        create_session()
    user_url_list = []
    url = 'http://www.xingyun.cn/yanlist/'
    header['Referer'] = url
    data = {
        'groupID': 0,
        'yanType': 1,
        'yanFilterType': 0,
        'totalCount': 300,
        'load_curPage': 1,
        'load_showLoadDiv': 1
    }
    r = session.post(url, data=data, headers=header)
    soup = BeautifulSoup(r.content, 'lxml')
    for item in soup.find_all('div', class_='userInfo'):
        user_url_list.append('http://www.xingyun.cn' + item.find('a')['href'])
    url = 'http://www.xingyun.cn/xingbangShow_getYanBangDataAjax.action'
    data = {'curPage': 1,
            'groupID': 1,
            'yanType': 1,
            'yanFilterType': 0}
    for i in xrange(2, 16):
        data['curPage'] = i
        r = session.post(url, data=data, headers=header)
        soup = BeautifulSoup(r.content, 'lxml')
        for item in soup.find_all('div', class_='userInfo'):
            user_url_list.append('http://www.xingyun.cn' + item.find('a')['href'])
    with open('xingyun_top300.txt', 'w') as fw:
        print len(user_url_list)
        for user_url in user_url_list:
            fw.write(session.get(user_url).url + '\n')


def follow(url, **kwargs):
    """
    模拟关注一个用户
    :param url: 用户url
    :param kwargs:
    :return:
    """
    global session, header, cookies
    if session == None:
        create_session()
    user_id = url.split('/')[-3]
    data = {'toUserId': user_id}
    header['Referer'] = url
    session.post('http://www.xingyun.cn/followUpdate_addFollow.action', data=data, headers=header)


def get_user_info(url, path='.', rank=-1, **kwargs):
    """
    获取一个用户的信息，存在一个文件夹中，文件夹包括用户的所有图片和一个文本文件，文本文件包括名次，分数，打分人数，人气，粉丝数，归属类别
    :param url: 用户主页的链接
    :param path: 写入的文件夹路径，不包括文件名
    :param rank: 用户排名
    :param kwargs:
    :return:
    """
    global session, header, cookies
    if session == None:
        create_session()
    follow(url)
    r = session.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    num_of_state = int(soup.find('a', id='nav_xingyu').find('em').get_text())  # 发表过的状态数
    yzscore = soup.find('div', class_='yzscore').find('span').get_text()
    job = soup.find('div', class_='text').get_text()
    info = soup.find('div', class_='follow')
    temp = info.find_all('a')
    impact = temp[0].get_text()
    fans = temp[1].get_text()
    num_of_rate = temp[2].get_text()
    with open(path + '/info.txt', 'w') as fw:
        fw.write('num_of_state:' + str(num_of_state) + '\n')
        fw.write('yzscore:' + yzscore.encode('utf8') + '\n')
        fw.write('job:' + job.encode('utf8') + '\n')
        fw.write('impact:' + impact.encode('utf8') + '\n')
        fw.write('fans:' + fans.encode('utf8') + '\n')
        fw.write('num_of_rate:' + num_of_rate.encode('utf8'))
    # 获取图片url
    img_url_list = []
    # 向xingyuShow_getXingyuContentAjax.action发送post请求获取最初5条动态
    user_id = url.split('/')[-3]
    header['Referer'] = url
    data = {'userid': user_id}
    r = session.post('http://www.xingyun.cn/xingyuShow_getXingyuContentAjax.action', headers=header, data=data)
    img_url_list.extend(get_img_url(r))
    for i in xrange(5):
        cur_page = i + 1
        if i != 0:
            # 发送翻页请求
            header['Referer'] = url
            data = {
                'xyimgsrcType': 'ajax',
                'showType': 0,
                'userid': user_id,
                'curPage': cur_page,
                'totalRecord': num_of_state
            }
            r = session.get('http://www.xingyun.cn/xingyuShow_showDynamicXyListAjax.action', headers=header, data=data)
            img_url_list.extend(get_img_url(r))
        for j in xrange(5):
            # 发送下滑更新的请求xingyuShow_getDynamicListByScrollLoad.action
            header['Referer'] = url
            data = {
                'curPage': cur_page,
                'dynamicLoadIndex': j + 1,
                'showType': 0,
                'userid': user_id
            }
            r = session.post('http://www.xingyun.cn/xingyuShow_getDynamicListByScrollLoad.action', headers=header,
                             data=data)
            img_url_list.extend(get_img_url(r))
    with open(path + '/img_url.txt', 'w') as fw:
        for img_url in img_url_list:
            fw.write(img_url + '\n')
    for i, img_url in enumerate(img_url_list):
        with open(path + '/' + str(i) + '.jpg', 'wb') as fw:
            fw.write(session.get(img_url).content)
            time.sleep(1)


def get_img_url(r, **kwargs):
    """
    从html中获取img的url
    :param r: html
    :param kwargs:
    :return: img的url
    """
    img_url_list = []
    soup = BeautifulSoup(r.content, 'lxml')
    for item in soup.find_all('div', class_='imgCont'):
        for img in item.find_all('input', showbig='true'):
            img_url_list.append(img['src'])
    return img_url_list


def save_all_image(**kwargs):
    """
    保存http://www.xingyun.cn/yanlist/中top300用户的信息
    :param kwargs:
    :return:
    """
    user_url_list = []
    with open('xingyun_top300.txt') as fr:
        for user_url in fr:
            user_url_list.append(user_url.strip())
    for i, user_url in enumerate(user_url_list):
        user_id = user_url.split('/')[-3]
        path = './xingyun/' + user_id
        if not os.path.exists(path):
            os.makedirs(path)
        get_user_info(user_url, path, i + 1)


def main():
    # get_top_user_url()
    # get_user_info('http://www.xingyun.cn/u/200200913177/saying/')
    save_all_image()


if __name__ == '__main__':
    main()
