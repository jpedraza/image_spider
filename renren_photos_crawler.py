# -*- coding: utf-8 -*-
# 人人相册爬虫

import os
import re
import ConfigParser
import requests
from bs4 import BeautifulSoup
from lxml import html

session = None


def create_session():
    global session
    headers = get_headers(get_config())
    s = requests.session()
    login_data = {'email': 'lufo816@gmail.com', 'password': 'lxb816qq94'}
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
def get_url(config):
    person_dict = {}

    # 人人相册url前缀
    url_prefix = 'http://photo.renren.com/photo/'
    rid_list = config.options('person')
    for rid in rid_list:
        person_dict[rid] = url_prefix + rid.strip() + '/albumlist/v7'

    return person_dict


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
    parsed_body = html.fromstring(s.get(url).content)
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
        response = s.get(album_url)
        parsed_body = html.fromstring(response.text)
        js = parsed_body.xpath('//script/text()')
        text = js[3].encode('utf-8')
        image_list = re.findall(r'"url":"(.*?)"', text)
        img_dict[key] = image_list

    return img_dict


def download_img(img_dict, start_dir):
    for album_id, image_list in img_dict.iteritems():

        if not os.path.exists(start_dir):
            os.makedirs(start_dir)

        image_list = map(lambda x: x.replace('\\', ''), image_list)
        for url in image_list:
            response = requests.get(url)
            with open(start_dir + '/' + url.split('/')[-1], 'wb') as f:
                f.write(response.content)


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
        soup = BeautifulSoup(s.get(url).content)
        if page_num == 0:
            count = soup.find('span', class_='count').string
            total_pages = int(count) / friends_per_page
        friends = soup.find_all('p', class_='avatar')
        for friend in friends:
            uid_list.append(friend.find('a')['href'].split('id=')[-1].strip())
        page_num += 1
    with open('uid_list.txt', 'a') as fw:
        for uid in uid_list:
            fw.write(uid + '\n')
    return uid_list


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


def get_img():
    config = get_config()
    # 相册首地址
    url_dict = get_url(config)

    for rid, url in url_dict.iteritems():
        name = config.get('person', rid)
        print name
        # 为每个人创建一个单独的文件夹存储相册
        start_dir = os.path.join(config.get('dir', 'start_dir'), name)
        album_url_dict = get_albums(url)
        img_dict = get_imgs(album_url_dict)
        download_img(img_dict, start_dir)


def main():
    uid_list = get_uid_list_main(469144378, 3)
    print uid_list


if __name__ == '__main__':
    main()
