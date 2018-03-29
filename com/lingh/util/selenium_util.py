#!/usr/bin/python
# -*- coding:utf-8 -*-

from selenium.webdriver import Chrome
from selenium.webdriver.support.wait import WebDriverWait


def g_img_url(pageURL):
    driver = Chrome('D:\\work\\makedown\\blog\\publish_news\\chromedriver.exe') # 调用浏览器
    driver.get(pageURL)
    try:
        WebDriverWait(driver, 5).until(lambda x: x.find_element_by_tag_name('main') or x.find_element_by_tag_name("section") or x.find_element_by_tag_name("table") or x.find_element_by_tag_name("article"))
    except Exception as e:
        pass

    p_element = None
    img = None

    try:
        if not p_element:
            p_element =driver.find_element_by_tag_name("figure")
    except Exception as e:
        pass

    try:
        if not p_element:
            p_element =driver.find_element_by_class_name("xd-b-left")
    except Exception as e:
        pass

    try:
        if not p_element:
            p_element =driver.find_element_by_tag_name("article")
    except Exception as e:
        pass

    try:
        p_element = driver.find_element_by_tag_name("main") # 找到相应的标签。
    except Exception as e:
        pass

    try:
        if not p_element:
            p_element = driver.find_element_by_tag_name("section")
    except Exception as e:
        pass

    try:
        if not p_element:
            p_element = driver.find_element_by_tag_name("table")
    except Exception as e:
        pass

    try:
        img = p_element.find_element_by_tag_name("img")
    except Exception as e:
        pass

    if img:
        return img.get_attribute('src')# 打印出属性为『src』的内容
    else:
        return None