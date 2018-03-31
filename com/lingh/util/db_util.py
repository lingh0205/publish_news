#!/usr/bin/python
# -*- coding:utf-8 -*-

import sqlite3
import re

conn = sqlite3.connect("publish_news")

def check(conn):
    try:
        conn.ping()
    except Exception as e:  # 实际对应的  MySQLdb.OperationalError 这个异常
        conn = sqlite3.connect("publish_news")

sql_c_publish_news = """CREATE DATABASE IF NOT EXISTS `publish_news`;"""

sql_subscribe_url = """CREATE TABLE `subscribe_url` (
	`id` BIGINT(20) NOT NULL,
	`gmt_create` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`gmt_modified` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`url` VARCHAR(128) NOT NULL DEFAULT '',
	`uid` BIGINT(20) NOT NULL,
	`p_title` VARCHAR(256) NULL DEFAULT NULL,
	`p_description` VARCHAR(256) NULL DEFAULT NULL,
	`title` VARCHAR(256) NULL DEFAULT NULL,
	`description` TEXT NULL,
	`pub_date` VARCHAR(50) NULL DEFAULT NULL,
	`img` VARCHAR(128) NULL DEFAULT NULL,
	`send_status` TINYINT(1) NULL DEFAULT '0',
	`retry_times` TINYINT(1) NULL DEFAULT '0',
	PRIMARY KEY (`id`),
	UNIQUE INDEX `uk_uid_url` (`uid`, `url`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
;
"""

sql_rss = """CREATE TABLE IF NOT EXISTS `rss` (
	`id` BIGINT(20) NOT NULL,
	`gmt_create` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`gmt_modified` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`rss_url` VARCHAR(128) NOT NULL,
	`uid` BIGINT(20) NOT NULL,
	`description` VARCHAR(256) NULL DEFAULT NULL,
	`status` INT(11) NOT NULL DEFAULT '0',
	PRIMARY KEY (`id`),
	UNIQUE INDEX `pk_uid_rss_url` (`uid`, `rss_url`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
;"""

sql_account = """CREATE TABLE IF NOT EXISTS `account` (
	`id` BIGINT(20) NOT NULL,
	`gmt_create` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`gmt_modified` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`name` VARCHAR(50) NOT NULL,
	`notify_url` VARCHAR(128) NOT NULL,
	`status` TINYINT(4) NOT NULL DEFAULT '1',
	PRIMARY KEY (`id`),
	UNIQUE INDEX `name` (`name`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
;"""

sql_key_word = """CREATE TABLE `key_word` (
	`id` BIGINT(20) NOT NULL,
	`gmt_create` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`gmt_modified` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`key` VARCHAR(50) NOT NULL,
	`uid` BIGINT(20) NOT NULL,
	`category` VARCHAR(50) NULL DEFAULT '',
	`status` TINYINT(1) NOT NULL DEFAULT '0',
	PRIMARY KEY (`id`),
	UNIQUE INDEX `uk_key_uid_category` (`key`, `uid`, `category`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
;
"""

def c_database():
    check(conn)
    cursor = conn.cursor()
    cursor.execute(sql_c_publish_news)
    print "create database publish_news success."

def c_subscribe():
    check(conn)
    cursor = conn.cursor()
    cursor.execute(sql_subscribe_url)
    conn.commit()
    print "create table subscribe_url success."

def c_rss():
    check(conn)
    cursor = conn.cursor()
    cursor.execute(sql_rss)
    conn.commit()
    print "create table rss success."

def c_account():
    check(conn)
    cursor = conn.cursor()
    cursor.execute(sql_account)
    conn.commit()
    print "create table account success."

def c_key():
    check(conn)
    cursor = conn.cursor()
    cursor.execute(sql_key_word)
    conn.commit()
    print "create table key_word success."

def insert(sql):
    check(conn)
    cursor = conn.cursor()
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        conn.commit()
    except Exception as  e:
        # Rollback in case there is any error
        print e
        conn.rollback()

def insert_subscribe(subscribe):
    # SQL 插入语句
    insert("""INSERT INTO subscribe_url VALUES (NULL , date('now'), date('now'), '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', 0, 0)""" % (subscribe.url, subscribe.uid, subscribe.p_title, subscribe.p_description, subscribe.title, subscribe.description, subscribe.pub_date, subscribe.img))

def insert_rss(rss):
    # SQL 插入语句
    insert("""INSERT INTO rss VALUES (NULL , date('now'), date('now'), '%s', '%s', '%s', '%s')""" % (rss.rss_url,rss.uid, rss.description, rss.status))

def insert_account(account):
    # SQL 插入语句
    insert("""INSERT INTO account VALUES (NULL , date('now'), date('now'), '%s', '%s', '%s')""" % (account.name, account.notify_url, account.status))

def select_one(sql):
    check(conn)
    cursor = conn.cursor()
    res = None
    try:
        # SQL 查询语句
        cursor.execute(sql)
        res = cursor.fetchone()
    except:
       print "Error: unable to fecth data with sql %s" % sql
    return res

def select_account_by_name(name):
    sql = """SELECT * FROM account WHERE name = '%s'""" % name
    res = select_one(sql)
    return res

def count_subscribe_by_url(url, uid):
    sql = """SELECT COUNT(*) FROM subscribe_url WHERE url = '%s' and uid = '%s'""" % (url, uid)
    res = select_one(sql)
    if res:
        res = res[0]
    return res

def select_all(sql):
    check(conn)
    cursor = conn.cursor()
    res = []
    try:
        # SQL 查询语句
        cursor.execute(sql)
        res = cursor.fetchall()
    except:
        print "Error: unable to fecth data with sql %s" % sql
    return res

def list_rss(uid):
    return [ x[0] for x in select_all("""select rss_url from rss WHERE status = 1 and uid = '%s'""" % uid)]

def list_subcribe(uid):
    return select_all("""select * from subscribe_url where uid='%s' and send_status = 0 and retry_times < 3 limit 5""" % uid)

def update_status(items):
    check(conn)
    cursor = conn.cursor()
    for item in items:
        cursor.execute("update subscribe_url set send_status = 1 and gmt_modified = date('now') where uid = '%s' and url = '%s'" % (item[4], item[3]))
    conn.commit()

def update_retry_times(items):
    check(conn)
    cursor = conn.cursor()
    for item in items:
        cursor.execute("update subscribe_url set retry_times = retry_times + 1 and gmt_modified = date('now') where uid = '%s' and url = '%s'" % (item[4], item[3]))
    conn.commit()

def list_ignore_key(uid, category):
    return [ x[0] for x in select_all("""select `key` from key_word where uid='%s' and `category` = '%s' or `category` = 'all' and `status` = 1""" % (uid, re.sub("'", r"#", category)))]

#c_database()
#c_subscribe()
#c_account()
#c_rss()
#c_key()
# print list_key(1, "生活", 0)

#print list_rss(1)
