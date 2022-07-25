# coding:utf-8
# 读取元件列表


__author__ = "songjiangshan"
__copyright__ = "Copyright (C) 2021 songjiangshan \n All Rights Reserved."
__license__ = ""
__version__ = "1.0"

import sys

import requests
import json
import sqlite3
import datetime
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def szlc_product_search(keyword, version='6.5.9'):
    """
    https://lceda.cn/api/eda/product/search
    keyword: C480345
version: 6.5.9

    ret:
    {
    result:{
    productList:[
    {
        image:"image1.jpg<$>image2.jpg"
    }
    ]
    }
    }
    """
    url = 'https://lceda.cn/api/eda/product/search'
    ret = requests.post(url, data={'keyword':keyword,
                                   'version': version}, verify=False)
    ret_j = json.loads(ret.text)
    if ret_j['code']!=200:
        print('szlc_read_tags return error.', ret.text)
        return


    return ret_j['result']['productList']

def szlc_read_comp_search(wd,uid='0819f05c4eef4c71ace90d822a990e87', type=3,doctype=2, returnListStyle='classifyarr',
                          version='6.5.9'):
    """
    input:
    https://lceda.cn/api/components/search
    POST:
    type: 3
    doctype[]: 2
    uid: 0819f05c4eef4c71ace90d822a990e87
    returnListStyle: classifyarr
    wd: SS-12D10
    version: 6.5.9

    ret:
    {
        success:true
        result:{
        lists{
            easyeda:[],
            lcsc:[{title:, uuid:,dataStr{head:{c_para:{package:str}}} }],
            mine:[]
        }
        }
    }
    """
    url = 'https://lceda.cn/api/components/search'
    ret = requests.post(url,data={'wd':wd, 'uid':uid, 'type':type,'returnListStyle':returnListStyle, 'version':version}, verify=False)
    ret_j = json.loads(ret.text)
    if ret_j['success'] is not True:
        print('szlc_read_tags return error.', ret.text)
        return


    ls=[]
    for i in ret_j['result']['lists'].values():
        ls.extend(i)
    print('szlc_read_comp_search', ls)
    return ls

def szlc_read_tags(version='6.5.9', docType=2, uid='0819f05c4eef4c71ace90d822a990e87'):
    """
    获取tags:
    https://lceda.cn/api/components/tags?version=6.5.9&docType=2&uid=0819f05c4eef4c71ace90d822a990e87

    获取某个子类型中的元素
    https://lceda.cn/api/components?version=6.5.9&docType=2&uid=0819f05c4eef4c71ace90d822a990e87&type=3&tag%5B%5D=Darlington+Transistors
    {
    result{
        lists[
        {

        }

        ]
    }
    }
    """
    url = 'https://lceda.cn/api/components/tags?version='+version+'&docType='+str(docType)+'&uid=' + uid
    ret = requests.get(url, verify=False)
    ret_j = json.loads(ret.text)
    if ret_j['success'] is not True:
        print('szlc_read_tags return error.', ret.text)
        return

    return ret_j['result']['lists']



def szlc_read(page=1, uid='0819f05c4eef4c71ace90d822a990e87'):
    """
    获取指定页数的元件列表
    搜索引擎=立创EDA 类型=符号 库别=立创商城

    :return:
    """
    url = 'https://lceda.cn/api/components?version=6.4.20.2&docType=2&uid=' + uid + '&page=' + str(page) + '&type=3'
    ret = requests.get(url, verify=False)
    ret_j = json.loads(ret.text)
    if ret_j['success'] is not True:
        print('return error.', ret.text)
        return

    return ret_j['result']['lists']

    # 类型=封装。库别=系统库
    # https://lceda.cn/api/components?version=6.4.20.2&docType=4&uid=4251c6ae97414f38bb1d929da02c4173&type=3
    # 类型=封装 库别=立创商城
    # https://lceda.cn/api/components?version=6.4.20.2&docType=4&uid=0819f05c4eef4c71ace90d822a990e87&type=3

    # 类型=符号 库别=系统库
    # https://lceda.cn/api/components?version=6.4.20.2&docType=2&uid=4251c6ae97414f38bb1d929da02c4173&type=3

    # 搜索引擎=立创EDA 类型=符号 库别=立创商城
    # https://lceda.cn/api/components?version=6.4.20.2&docType=2&uid=0819f05c4eef4c71ace90d822a990e87&type=3

    # 搜索引擎=立创EDA 类型=符号 库别=嘉立创贴片
    # https://lceda.cn/api/components?version=6.4.20.2&docType=2&uid=0819f05c4eef4c71ace90d822a990e87&type=3&SMT=true

    # 搜索引擎=立创EDA 类型=符号 库别=立创商城 第二页
    # https://lceda.cn/api/components?docType=2&uid=0819f05c4eef4c71ace90d822a990e87&type=3&page=2&version=6.4.20.2

    pass


def get_total_page(uid='0819f05c4eef4c71ace90d822a990e87'):
    """
    获取总共的页数
    :param uid:
    :return:
    """

    url = 'https://lceda.cn/api/components?version=6.4.20.2&docType=2&uid=' + uid + '&type=3'
    ret = requests.get(url, verify=False)
    ret_j = json.loads(ret.text)
    if ret_j['success'] is not True:
        print('return error.', ret.text)
        return 0
    return ret_j['result']['totalPage']


def create_db(page_cnt, file_name='szlc_20210611.db'):
    """
    创建数据库
    :param page_cnt:
    :param file_name:
    :return:
    """

    conn = sqlite3.connect(file_name)
    c = conn.cursor()
    # c.execute('    drop table if exists page_index;')
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
    if len(rows) == 0:
        # page_cnt=1062#
        print('page_cnt:', page_cnt)
        for i in range(1, page_cnt + 1):
            c.execute(" INSERT INTO page_index (id) VALUES ('" + str(i) + "' );  ")
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
    c = conn.cursor()

    for i in page_list:
        comp_uuid = str(i['uuid'])
        comp_name = i['dataStr']['head']['c_para']['name']
        comp_package = i['dataStr']['head']['c_para']['package']
        comp_desc = i['description']
        c.execute(
            "insert into comp_list(uuid, name, package_name, desc) values('" + comp_uuid + "', '" + comp_name + "', '" + comp_package + "', '" + comp_desc + "'" + ");")

    conn.commit()

    conn.close()


from line_profiler import LineProfiler
import atexit

lp = LineProfiler()


@atexit.register
def line_profile_print():
    lp.print_stats()


@lp
def pull_comp_index(file_name='szlc_20210611.db'):
    """
    获取所有的元件，保存到文件中
    :param file_name:
    :return:
    """
    total_page = get_total_page()
    print('total_page:', total_page)
    # total_page = 1062
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
                'UPDATE page_index set is_read = 1, start_time="' + dt1.isoformat() + '"' + ',end_time="' + datetime.datetime.now().isoformat() + '", cnt=' + str(
                    len(page_list)) + ' where id=' + str(
                    row[0]))
            print('page finish:', row[0], len(page_list))
            conn.commit()
            conn.close()

        if row[0]>5:
            sys.exit(0)



def get_comp_index(file_name='szlc_20210611.db'):
    """
    获取文件中的元件列表

    :param file_name:
    :return:[[id, uuid] [id, uuid]]
    """
    conn = sqlite3.connect(file_name)
    c = conn.cursor()
    c.execute("select id, uuid from comp_list")
    uuid_list = c.fetchall()
    conn.close()
    return uuid_list


if __name__ == "__main__":
    # 读取元件列表并保存到sqlite文件中
    pull_comp_index('szlc_20210611.db')
    get_comp_index()
