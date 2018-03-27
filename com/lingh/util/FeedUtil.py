#!/usr/bin/python
# -*- coding:utf-8 -*-
import time

from com.lingh.util import HttpUtil
from bs4 import BeautifulSoup
import json
import sys
import re
from urlparse import urlparse

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

# http://news.sciencenet.cn/upload/news/images/2018/3/2018327153946110.jpg
def g_pic(url, header):
    print url
    try:
        sub_html = HttpUtil.g_html(url, header)
        # print sub_html
        domain = HttpUtil.g_host(url)
        bs = BeautifulSoup(sub_html, "html.parser")

        if bs.table and bs.table.find('img'):
            return "http://%s%s" % (domain, bs.table.find('img')['src'])
        return ""
    except Exception as e:
        print e

def feed(url):
    try:
        file = g_feed(url, header)
        bs = BeautifulSoup(file, "html.parser")
        items = bs.find_all('item')
        for item in items:
            row = {}
            bs1 = BeautifulSoup(str(item), "html.parser")
            row['title'] = bs1.title.text
            url = bs1.link.next_element.replace("\n", "")
            # print bs1.comments.text
            pubdate = bs1.pubdate.text
            # print bs1.category.text
            # print bs1.guid.text
            description = bs1.description.text

            # generate content
            img = g_pic(url, header)
            text = "#### %s \n  ###### 链接： %s \n ###### 发布时间：%s \n" % (row['title'], url, pubdate)
            if img:
                text = "%s ![](%s) \n " % (text, img)
            row['text'] = "%s > %s" % (text, description)

            data.append(row)
    except Exception as e:
        print e

feed('http://www.sciencenet.cn/xml/news-0.aspx?news=0')
# feed("http://www.adaymag.com/feed")
# feed("http://www.duxieren.com/duxieren.xml")
# feed("http://www.matrix67.com/blog/feed")

send_url = 'https://oapi.dingtalk.com/robot/send?access_token=3d1fa7c56de3c10b5e1257b8802526ec1e9021338c7914c76eede6e2193e6914'
for d in data:
    try:
        textmod = json.dumps({ "markdown": d, "msgtype": "markdown" })
        print HttpUtil.p_json(send_url, textmod, header)
        time.sleep(2)
    except Exception as e:
        print e

# print g_pic('http://news.sciencenet.cn/htmlnews/2018/3/407125.shtm',header)
