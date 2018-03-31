#!/usr/bin/python
# -*- coding:utf-8 -*-
import urllib
import urllib2

def g_html(url, header=None):
    req = urllib2.Request(url=url, headers=header)
    resp = urllib2.urlopen(req)
    return resp.read()

def p_json(url, data, header = {}):
    header["Content-Type"] = "application/json"
    req = urllib2.Request(url, data, header)
    res = urllib2.urlopen(req)
    return res.read()

def g_host(url):
    proto, rest = urllib.splittype(url)
    res, rest = urllib.splithost(rest)
    return res