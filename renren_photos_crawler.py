# -*- coding: utf-8 -*-
# 人人相册爬虫

import os
import re
import ConfigParser
import requests
from bs4 import BeautifulSoup
from lxml import html
from multiprocessing.dummy import Pool as ThreadPool

session = None
start_dir = '/Users/lufo/PycharmProjects/images/renren'
login_data_list = [{'email': 'lufo816@gmail.com', 'password': 'lxb816qq94'},
                   {'email': '2693107435@qq.com', 'password': 'fy123456'},
                   {'email': 'swulixi@sina.com', 'password': '12345678'},
                   {'email': '250520506@qq.com ', 'password': 'cigityz'},
                   {'email': '15736028958 ', 'password': 'l19898624'},
                   {'email': 'long61@qq.com ', 'password': 'qwe!@#123'},
                   {'email': 'mmx110@yeah.net', 'password': '19900528'},
                   {'email': '1953097503@qq.com', 'password': '123456'},
                   {'email': '1127308854@qq.com', 'password': 'cigitmedia'},
                   {'email': '1127308854@qq.com', 'password': 'cigitmedia'},
                   {'email': 'agnfff@sina.com', 'password': 'cg12345678'}]


def create_session():
    global session, login_data_list
    headers = get_headers(get_config())
    s = requests.session()
    login_data = login_data_list[2]
    try:
        s.post('http://www.renren.com/PLogin.do', data=login_data, headers=headers)
    except Exception, e:
        print e
    session = s


# 获取配置
def get_config():
    config = ConfigParser.RawConfigParser()
    config.read('renren_config.ini')

    return config


# 获取每个人得相册首地址
def get_rid(config):
    person_list = []
    rid_list = config.options('person')
    for rid in rid_list:
        person_list.append(rid.strip())
    return person_list


# 组装HTTP请求头
def get_headers(config):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2,ru;q=0.2,fr;q=0.2,ja;q=0.2',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.renren.com',
        'RA-Sid': 'DAF1BC22-20140915-034057-065a39-2cb2b1',

        'RA-Ver': '2.10.4',
        'Referer': 'http://www.renren.com/SysHome.do',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36',
    }

    # 从配置文件中取得用户cookie
    headers['Cookie'] = config.get('cookie', 'cookie')

    return headers


# 获得相册列表
def get_albums(url):
    global session
    if session == None:
        create_session()
    s = session
    try:
        parsed_body = html.fromstring(s.get(url, timeout=5).content)
    except Exception, e:
        print e
        return {}
    js = parsed_body.xpath('//script/text()')
    js = map(lambda x: x.encode('utf-8'), js)

    # 相册代码所在的js段
    album_js = js[3]
    album_raw = re.findall(r"'albumList':\s*(\[.*?\]),", album_js)[0]
    album_list = eval(album_raw)

    album_url_dict = {}
    for album in album_list:
        if album['sourceControl'] == 99:  # 有权访问该相册（只能爬取有权访问的相册）
            album_url = 'http://photo.renren.com/photo/'
            album_url = album_url + str(album['ownerId']) + '/'
            album_url = album_url + 'album-' + album['albumId'] + '/v7'

            album_url_dict[album['albumId']] = {}
            album_url_dict[album['albumId']]['album_url'] = album_url
            album_url_dict[album['albumId']]['photo_count'] = album['photoCount']
            album_url_dict[album['albumId']]['album_name'] = album['albumName']

    return album_url_dict


# 获取每个相册中的图片列表
def get_imgs(album_url_dict):
    global session
    if session == None:
        create_session()
    s = session
    img_dict = {}

    for key, val in album_url_dict.iteritems():
        album_url = val['album_url']
        try:
            response = s.get(album_url, timeout=5)
            parsed_body = html.fromstring(response.content)
            js = parsed_body.xpath('//script/text()')
            text = js[3].encode('utf-8')
            image_list = re.findall(r'"url":"(.*?)"', text)
            img_dict[key] = image_list
        except Exception, e:
            print e
    return img_dict


def download_img(img_dict, start_dir):
    global session
    if session == None:
        create_session()
    s = session
    for album_id, image_list in img_dict.iteritems():

        if not os.path.exists(start_dir):
            os.makedirs(start_dir)

        image_list = map(lambda x: x.replace('\\', ''), image_list)
        for url in image_list:
            try:
                response = s.get(url, timeout=5)
                with open(start_dir + '/' + url.split('/')[-1], 'wb') as f:
                    f.write(response.content)
            except Exception, e:
                print e


def get_uid_list(uid):
    print uid
    global session
    if session == None:
        create_session()
    s = session
    uid_list = []
    total_pages = 0
    page_num = 0
    friends_per_page = 20
    while page_num <= total_pages:
        url = "http://friend.renren.com/GetFriendList.do?curpage=" + str(page_num) + "&id=" + str(uid)
        try:
            soup = BeautifulSoup(s.get(url).content)
            if page_num == 0:
                count = soup.find('span', class_='count').string
                total_pages = int(count) / friends_per_page
            friends = soup.find_all('p', class_='avatar')
            for friend in friends:
                uid_list.append(friend.find('a')['href'].split('id=')[-1].strip())
            page_num += 1
        except Exception, e:
            print e
    with open('uid_list.txt', 'a') as fw:
        for uid in uid_list:
            fw.write(uid + '\n')
    return uid_list


def uniqify():
    """
    去除uid_list.txt中重复的并保存为'uid=uid'的形式
    """
    uid_set = set([])
    with open('uid_list.txt', 'r') as fr:
        for item in fr:
            uid_set.add(item.strip())
    with open('uid_list.txt', 'w') as fw:
        for item in uid_set:
            fw.write(item + '=' + item + '\n')


def get_uid_list_main(uid, layers=5):
    """
    获取用户n度好友
    :param uid: 初始用户id
    :param layers: 度数
    :return: List，保存所有好友uid，不重复
    """
    uid_list = [uid]
    for i in xrange(layers):
        temp = uid_list[:]
        for uid in uid_list:
            temp.extend(get_uid_list(uid))
        uid_list = list(set(temp))
    return uid_list


def get_renren_img(rid_list):
    global start_dir
    for rid in rid_list:
        name = rid
        print name
        url = 'http://photo.renren.com/photo/' + rid + '/albumlist/v7'
        # 为每个人创建一个单独的文件夹存储相册
        dir = os.path.join(start_dir, name)
        # print dir
        album_url_dict = get_albums(url)
        img_dict = get_imgs(album_url_dict)
        download_img(img_dict, dir)


def get_img_parallel(step, number_of_threads, begin, end):
    """
    并行抓取图片
    """
    config = get_config()
    # 相册首地址
    rid_list = get_rid(config)
    # get_renren_img(rid_list[2740:])
    pool = ThreadPool(number_of_threads)
    for i in xrange(begin, end, step * number_of_threads):
        pool.map(get_renren_img, [rid_list[i + j * step: i + (j + 1) * step] for j in xrange(number_of_threads)])
    pool.close()
    pool.join()


def main():
    # uid_list = get_uid_list_main(469144378, 3)
    # uniqify()
    # get_img()
    global start_dir
    num_of_dir = -1
    for dir in os.walk(start_dir):
        num_of_dir += 1
    print num_of_dir
    get_img_parallel(step=25, number_of_threads=4, begin=0 + num_of_dir, end=50000)


if __name__ == '__main__':
    main()
