#!/usr/bin/python
# -*- coding:utf-8 -*-
import time

from com.lingh.model.db_model import subscribe_url
from com.lingh.util import HttpUtil
from com.lingh.util import db_util
from bs4 import BeautifulSoup
import json
import sys
import selenium_util

reload(sys)
sys.setdefaultencoding('utf-8')

def g_feed(url, header = None):
    return HttpUtil.g_html(url, header)


header = {
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.9'
}

data = []
subscribe_list = []

# http://news.sciencenet.cn/upload/news/images/2018/3/2018327153946110.jpg
def g_pic(url, header):
    try:
        sub_html = HttpUtil.g_html(url, header)
        # print sub_html
        domain = HttpUtil.g_host(url)
        bs = BeautifulSoup(sub_html, "html.parser")

        if bs.table and bs.table.find('img'):
            return "http://%s%s" % (domain, bs.table.find('img')['src'])
        return None
    except Exception as e:
        print e

def feed(url, uid):
    try:
        file = g_feed(url, header)
        bs = BeautifulSoup(file, "html.parser")
        p_title = bs.title
        p_description = bs.description
        items = bs.find_all('item')
        row = {}
        text = ""
        for item in items:
            bs1 = BeautifulSoup(str(item), "html.parser")
            row['title'] = bs1.title.text
            url = bs1.link.next_element.replace("\n", "")

            count = db_util.count_subscribe_by_url(url, uid)
            # 不需要重复处理
            if count and count > 0:
                continue

            pubdate = bs1.pubdate.text
            description = bs1.description.text
            print url
            # generate content
            img = g_pic(url, header)

            if not img:
                img = selenium_util.g_img_url(url)

            text = "%s ### %s | %s \n #### [%s](%s) \n ###### 发布时间：%s \n" % (text, p_title, p_description, row['title'], url, pubdate)
            if img:
                print img
                text = "%s ![](%s) \n " % (text, img)
            row['text'] = "%s > %s \n \n" % (text, description)

            subscribe_list.append(subscribe_url(url, uid, row['title'], p_title, pubdate, img))
        data.append(row)
    except Exception as e:
        print e

def send_msg():
    user = db_util.select_account_by_name('LinGH')
    uid = user[0]
    send_url = user[4]
    feed_list = db_util.list_rss(uid)

    for source in feed_list:
        feed(source, uid)

    for d in data:
        try:
            textmod = json.dumps({ "markdown": d, "msgtype": "markdown" })
            resp = HttpUtil.p_json(send_url, textmod, header)
            print json.loads(resp)['errcode']
            print json.loads(resp)['errmsg']
            time.sleep(2)
        except Exception as e:
            print e

    for subscribe in subscribe_list:
        db_util.insert_subscribe(subscribe)

send_msg()
# print selenium_util.g_img_url('http://www.ifanr.com/1002843?utm_source=rss&utm_medium=rss&utm_campaign=')
