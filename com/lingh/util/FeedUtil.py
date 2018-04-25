#!/usr/bin/python
# -*- coding:utf-8 -*-
import time
from bs4 import BeautifulSoup
import json
import sys
import selenium_util
import argparse

sys.path.append('/home/linguohua/github/publish_news/');

from com.lingh.model.db_model import subscribe_url
from com.lingh.util import HttpUtil
from com.lingh.util import db_util
from com.lingh.model import mode, code

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

def g_pic(url, header):
    try:
        sub_html = HttpUtil.g_html(url, header)
        # print sub_html
        bs = BeautifulSoup(sub_html, "html.parser")

        for tag in ['figure', "xd-b-left", "article", "main", "section", "table", "content"]:
            f_list = bs.find_all(tag)

            if not f_list:
                f_list = bs.find_all("div", _class = tag)
        
            if not f_list:
                f_list = bs.find_all(id=tag)

            if not f_list or len(f_list) == 0:
                continue
            for figure in f_list:
                f_bs = BeautifulSoup(str(figure), "html.parser")
                for img in f_bs.find_all("img"):
                    if img:
                        try:
                            height = img['height']
                            if str(height) == "auto" or int(height) >= 300:
                                return img['src']
                        except Exception as e:
                            print e

                        try:
                            width = img['width']
                            if str(width) == "auto" or int(width) >= 400:
                                return img['src']
                        except Exception as e:
                            print e

        return None
    except Exception as e:
        print e

def is_ignore(title, description, ignore):
    if (title and str(title).__contains__(ignore)) or (description and str(description).__contains__(ignore)):
        return True
    else:
        return False

def ignore(bs, description, p_title, p_description, title, url):
    categorys = bs.find_all("category")
    if categorys:
        for category in categorys:
            category = category.text
            ignores = db_util.list_ignore_key(uid, category)
            for ignore in ignores:
                if is_ignore(title, description, ignore):
                    print "[WARN]Ignore key word %s with subscribe by category %s msg %s | %s | %s | %s." % (
                    ignore, category, p_title, p_description, title, url)
                    return code.ignore
    else:
        ignores = db_util.list_ignore_key(uid, code.all)
        for ignore in ignores:
            if is_ignore(title, description, ignore):
                print "[WARN]Ignore key word %s with subscribe msg %s | %s | %s | %s." % (ignore, p_title, p_description, title, url)
                return code.ignore
    return code.subscribe

def feed(url, uid):
    try:
        file = g_feed(url, header)
        bs = BeautifulSoup(file, "html.parser")
        print "[INFO]Start to subscribe for user %d with url : %s" % (uid, url)
        p_title = bs.title

        if p_title:
            p_title = p_title.text.strip()

        p_description = bs.description

        items = bs.find_all('item')
        for item in items:
            bs1 = BeautifulSoup(str(item), "html.parser")
            title = bs1.title.text
            
            if title:
                title = title.strip()

            description = bs1.description.text

            if code.ignore == ignore(bs, description, p_title, p_description, title, url):
                continue

            url = bs1.link.next_element.replace("\n", "")

            count = db_util.count_subscribe_by_url(url, uid)
            # 不需要重复处理
            if count and count > 0:
                continue

            pubdate = bs1.pubdate.text

            # generate content
            img = bs1.image
            if img:
                img = img.text
            else:
                img = g_pic(url, header)

            #if not img:
            #    img = selenium_util.g_img_url(url)

            print "[INFO]Subcribe %s | %s | %s | %s success." % (p_title, p_description, title, url)
            db_util.insert_subscribe(subscribe_url(url, uid, title, description, p_title, p_description, pubdate, img))
    except Exception as e:
        print e

def g_uid(name):
    user = db_util.select_account_by_name('LinGH')
    if user:
        return user[0],user[4]
    return 0, ""

def generate_msg(uid, items):
    text = ""
    p_title = ""

    for item in items:
        if not p_title:
            p_title = item[5]

        text = "%s ### %s | %s \n #### [%s](%s) \n ###### 发布时间：%s \n" % (text, item[5], item[6], item[7], item[3], item[9])
        if item[10]:
            text = "%s ![](%s) \n " % (text, item[10])

        descript = item[8]
        if len(descript) > 100:
            descript = descript[1:100]
        text = "%s > %s \n \n" % (text, descript)

        print "[INFO]Generate publish msg for %s | %s | %s | %s " % (item[5], item[6], item[7], item[3])

    return p_title,text

def parse_argu():
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument('--mode', type=str, default="subscribe")
    parser.add_argument('--user', type=str, default="LinGH")
    args = parser.parse_args()
    return args.mode, args.user

def subscribe(uid):
    feed_list = db_util.list_rss(uid)
    for source in feed_list:
        feed(source, uid)
    print "[INFO]Finish to subcribe for user %d." % uid

def send_msg(uid, send_url):
    items = db_util.list_subcribe(uid)

    if len(items) <= 0:
        return code.finish

    p_title, text = generate_msg(uid, items)

    md = {
        "title": p_title,
        "text": text
    }

    try:
        textmod = json.dumps({"markdown": md, "msgtype": "markdown"})
	print textmod
        resp = HttpUtil.p_json(send_url, textmod, header)
        if int(json.loads(resp)['errcode']) == 0:
            print "[RESULT]%s" % resp
            db_util.update_status(items)
        else:
            db_util.update_retry_times(items)
            print "[ERROR]Publish news failed, Cause by : %s" % json.loads(resp)['errmsg']
        time.sleep(2)
    except Exception as e:
        print e

    return code.success

def publish(uid, send_url):
    start = (int(time.time()))
    while True:
        time_out =  int(time.time()) - start
        flag = send_msg(uid, send_url)
        if time_out > 60 or flag == code.failure:
            print "[ERROR]Failed to publish msg. Cause by time out is %d and flag is %d" % (time_out, flag)
            break
        elif flag == code.finish:
            print "[INFO]Finish to publish msg!"
            break


if __name__ == "__main__":
    mod, name = parse_argu()
    print "[INFO]Start to %s for user %s ......" % (mod, name)
    uid, send_url = g_uid(name)
    if mode.subscribe == mod:
        subscribe(uid)
    elif mode.publish == mod:
        publish(uid, send_url)


