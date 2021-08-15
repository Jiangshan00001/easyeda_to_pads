# coding:utf-8
# 读取元件列表


__author__ = "songjiangshan"
__copyright__ = "Copyright (C) 2021 songjiangshan \n All Rights Reserved."
__license__ = ""
__version__ = "1.0"

import requests
import json
import sqlite3
import datetime
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



def szlc_read(page=1, uid='0819f05c4eef4c71ace90d822a990e87'):
    """
    获取指定页数的元件列表
    搜索引擎=立创EDA 类型=符号 库别=立创商城

    :return:
    """
    url='https://lceda.cn/api/components?version=6.4.20.2&docType=2&uid='+uid+'&page='+str(page)+'&type=3'
    ret = requests.get(url, verify=False)
    ret_j = json.loads(ret.text)
    if ret_j['success'] is not True:
        print('return error.', ret.text)
        return

    return ret_j['result']['lists']



    #类型=封装。库别=系统库
    #https://lceda.cn/api/components?version=6.4.20.2&docType=4&uid=4251c6ae97414f38bb1d929da02c4173&type=3
    #类型=封装 库别=立创商城
    #https://lceda.cn/api/components?version=6.4.20.2&docType=4&uid=0819f05c4eef4c71ace90d822a990e87&type=3

    #类型=符号 库别=系统库
    #https://lceda.cn/api/components?version=6.4.20.2&docType=2&uid=4251c6ae97414f38bb1d929da02c4173&type=3

    # 搜索引擎=立创EDA 类型=符号 库别=立创商城
    #https://lceda.cn/api/components?version=6.4.20.2&docType=2&uid=0819f05c4eef4c71ace90d822a990e87&type=3

    # 搜索引擎=立创EDA 类型=符号 库别=嘉立创贴片
    #https://lceda.cn/api/components?version=6.4.20.2&docType=2&uid=0819f05c4eef4c71ace90d822a990e87&type=3&SMT=true

    # 搜索引擎=立创EDA 类型=符号 库别=立创商城 第二页
    #https://lceda.cn/api/components?docType=2&uid=0819f05c4eef4c71ace90d822a990e87&type=3&page=2&version=6.4.20.2

    pass

def get_total_page(uid='0819f05c4eef4c71ace90d822a990e87'):
    """
    获取总共的页数
    :param uid:
    :return:
    """

    url='https://lceda.cn/api/components?version=6.4.20.2&docType=2&uid='+uid+'&type=3'
    ret = requests.get(url, verify=False)
    ret_j = json.loads(ret.text)
    if ret_j['success'] is not True:
        print('return error.', ret.text)
        return 0
    return ret_j['result']['totalPage']


def create_db(page_cnt,file_name='szlc_20210611.db'):
    """
    创建数据库
    :param page_cnt:
    :param file_name:
    :return:
    """

    conn = sqlite3.connect(file_name)
    c=conn.cursor()
    #c.execute('    drop table if exists page_index;')
    c.execute("""
    create table if not exists page_index(
    id int primary key not null,
    is_read int,
    start_time text, 
    end_time text,
    cnt int
    );
    """)
    conn.commit()
    c.execute("""
    create table if not exists comp_list(
    id INTEGER  primary key AUTOINCREMENT,
    uuid int,
    name text, 
    package_name text,
    desc text
    );
    """)
    conn.commit()

    rows = c.execute("select id from page_index")
    rows = rows.fetchall()
    if len(rows)==0:
        #page_cnt=1062#
        print('page_cnt:' , page_cnt)
        for i in range(1, page_cnt+1):
            c.execute(" INSERT INTO page_index (id) VALUES ('"+str(i)+"' );  ")
        conn.commit()


    conn.close()

def page_list_save(page_list, file_name='szlc_20210611.db'):
    """
    保存元件列表
    :param page_list:
    :param file_name:
    :return:
    """
    conn = sqlite3.connect(file_name)
    c=conn.cursor()
    for i in page_list:
        comp_uuid = str(i['uuid'])
        comp_name = i['dataStr']['head']['c_para']['name']
        comp_package = i['dataStr']['head']['c_para']['package']
        comp_desc=i['description']
        c.execute("insert into comp_list(uuid, name, package_name, desc) values('"+comp_uuid+"', '"+ comp_name+"', '"+comp_package +"', '"+comp_desc+"'"+");")

    conn.commit()

    conn.close()

def pull_comp_index(file_name='szlc_20210611.db'):
    """
    获取所有的元件，保存到文件中
    :param file_name:
    :return:
    """
    total_page = get_total_page()
    print('total_page:', total_page)
    #total_page = 1062
    create_db(total_page, file_name)

    conn = sqlite3.connect(file_name)
    c = conn.cursor()
    rows = c.execute('select id, is_read from page_index')
    rows = rows.fetchall()
    conn.close()
    for row in rows:
        print('page. isread:', row[0], row[1])
        if row[1] is None:
            # 未读，需要读出
            dt1 = datetime.datetime.now()

            page_list = szlc_read(page=row[0])
            page_list_save(page_list, file_name)

            conn = sqlite3.connect(file_name)
            c = conn.cursor()
            c.execute(
                'UPDATE page_index set is_read = 1, start_time="' + dt1.isoformat() + '"' + ',end_time="' + datetime.datetime.now().isoformat() + '", cnt='+ str(len(page_list)) +' where id=' + str(
                    row[0]))
            print('page finish:', row[0], len(page_list))
            conn.commit()
            conn.close()


def get_comp_index(file_name='szlc_20210611.db'):
    """
    获取文件中的元件列表

    :param file_name:
    :return:[[id, uuid] [id, uuid]]
    """
    conn = sqlite3.connect(file_name)
    c=conn.cursor()
    c.execute("select id, uuid from comp_list")
    uuid_list = c.fetchall()
    conn.close()
    return uuid_list
if __name__=="__main__":

    #读取元件列表并保存到sqlite文件中
    pull_comp_index('szlc_20210611.db')
    get_comp_index()
