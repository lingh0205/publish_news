#!/usr/bin/python
# -*- coding:utf-8 -*-

class subscribe_url(object):

    def __init__(self, url, uid, title, p_title, pub_date, img):
        self.url = url
        self.uid = uid
        self.title = title
        self.p_title = p_title
        self.pub_date = pub_date
        self.img = img


class rss(object):

    def __init__(self, rss_url, uid, status = 1, description = None):
        self.rss_url = rss_url
        self.uid = uid
        self.status = status
        self.description = description

class account(object):

    def __init__(self, name, notify_url, status = 1):
        self.name = name
        self.notify_url = notify_url
        self.status = status