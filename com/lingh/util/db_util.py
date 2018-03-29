#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.lingh.model.db_model import subscribe_url
import MySQLdb

conn = MySQLdb.connect("localhost","root","admin","publish_news", charset='utf8')

def check(conn):
    try:
        conn.ping()
    except Exception as e:  # 实际对应的  MySQLdb.OperationalError 这个异常
        conn = MySQLdb.connect("localhost","root","admin","publish_news", charset='utf-8')

sql_c_publish_news = """CREATE DATABASE IF NOT EXISTS `publish_news`;"""

sql_subscribe_url = """CREATE TABLE IF NOT EXISTS `subscribe_url` (
	`id` BIGINT(20) NOT NULL AUTO_INCREMENT,
	`gmt_create` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`gmt_modified` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	`url` VARCHAR(128) NOT NULL DEFAULT '""',
	`uid` BIGINT(20) NOT NULL,
	`p_title` VARCHAR(256) NULL DEFAULT NULL,
	`title` VARCHAR(256) NULL DEFAULT NULL,
	`pub_date` VARCHAR(50) NULL DEFAULT NULL,
	`img` VARCHAR(128) NULL DEFAULT NULL,
	PRIMARY KEY (`id`),
	UNIQUE INDEX `uk_uid_url` (`uid`, `url`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
;"""

sql_rss = """CREATE TABLE IF NOT EXISTS `rss` (
	`id` BIGINT(20) NOT NULL AUTO_INCREMENT,
	`gmt_create` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`gmt_modified` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
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
	`id` BIGINT(20) NOT NULL AUTO_INCREMENT,
	`gmt_create` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`gmt_modified` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	`name` VARCHAR(50) NOT NULL,
	`notify_url` VARCHAR(128) NOT NULL,
	`status` TINYINT(4) NOT NULL DEFAULT '1',
	PRIMARY KEY (`id`),
	UNIQUE INDEX `name` (`name`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
;"""

def c_database():
    check(conn)
    cursor = conn.cursor()
    cursor.execute(sql_c_publish_news)
    print "create database publish_news success."

def c_subscribe():
    check(conn)
    cursor = conn.cursor()
    cursor.execute(sql_subscribe_url)
    print "create table subscribe_url success."

def c_rss():
    check(conn)
    cursor = conn.cursor()
    cursor.execute(sql_rss)
    print "create table rss success."

def c_account():
    check(conn)
    cursor = conn.cursor()
    cursor.execute(sql_account)
    print "create table account success."

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
    insert("""INSERT INTO subscribe_url VALUES (NULL , NOW(), NOW(), '%s', '%s', '%s', '%s', '%s', '%s')""" % (subscribe.url, subscribe.uid, subscribe.p_title, subscribe.title, subscribe.pub_date, subscribe.img))

def insert_rss(rss):
    # SQL 插入语句
    insert("""INSERT INTO rss VALUES (NULL , NOW(), NOW(), '%s', '%s', '%s', '%s')""" % (rss.rss_url,rss.uid, rss.description, rss.status))

def insert_account(account):
    # SQL 插入语句
    insert("""INSERT INTO account VALUES (NULL , NOW(), NOW(), '%s', '%s', '%s')""" % (account.name, account.notify_url, account.status))

def select_one(sql):
    check(conn)
    cursor = conn.cursor()
    res = None
    try:
        # SQL 查询语句
        cursor.execute(sql)
        res = cursor.fetchone()
    except:
       print "Error: unable to fecth data"
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
    res = None
    try:
        # SQL 查询语句
        cursor.execute(sql)
        res = cursor.fetchall()
    except:
        print "Error: unable to fecth data"
    return res

def list_rss(uid):
    return [ x[0] for x in select_all("""select rss_url from rss WHERE status = 1 and uid = '%s'""" % uid)]

    # subscribe = subscribe_url('http://www.zreading.cn/archives/6321.html', '应对未来的最佳策略，是承认自己无知', '左岸读书', 'Tue, 27 Mar 2018 22:47:58 +0000', 'http://zreading-img.qiniudn.com/20180328-1.jpg')
    # insert(subscribe)
    # print select_one('http://www.zreading.cn/archives/6321.html')

# print select_account_by_name('LinGH')
