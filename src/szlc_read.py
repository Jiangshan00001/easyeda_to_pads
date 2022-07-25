# coding:utf-8
# 从服务器 读取各个元件的封装

__author__ = "songjiangshan"
__copyright__ = "Copyright (C) 2021 songjiangshan \n All Rights Reserved."
__license__ = ""
__version__ = "1.0"

import requests
import json
import sqlite3
import datetime
from szlc_read_list import get_comp_index
import sys
import time
import json
import zlib
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def lc_pull_comp_decl(comp_uuid):
    url2 = 'https://lceda.cn/api/components/' + str(comp_uuid) + '?version=6.4.20.2&uuid=' + str(
        comp_uuid) + '&datastrid='
    t1 = time.time()
    strhtml = requests.get(url2, verify=False)  # Get方式获取网页数据
    t2 = time.time()
    try:
        comp_list_ret = json.loads(strhtml.text)
    except Exception as e:
        print(e)
        print(strhtml.text)
        print(comp_uuid)
        sys.exit(0)
    t3 = time.time()
    # print((t3-t2)/(t3-t1),end=' ')
    return comp_list_ret, [t3 - t2, t2 - t1]
    # packageDetail = comp_list_ret['result']['packageDetail']
    # return packageDetail, comp_list_ret['result']['dataStr']['head']


def create_comp_db(file_name, create_comp=1, create_decl=1):
    conn = sqlite3.connect(file_name)
    c = conn.cursor()
    if create_comp:
        c.execute("""
        create table if not exists comp_list(
        id int primary key not null,
        uuid varchar(50),
        is_smt int,    
        decl_uuid varchar (50),
        sch blob,
        tags text,
        title text,
        updateTime varchar(50)
        );
        """)
        conn.commit()

    if create_decl:
        c.execute("""
        create table if not exists decl_list(
        id INTEGER  primary key AUTOINCREMENT,
        uuid varchar(50),
        title varchar(50),
        json_data blob
        );
        """)
        conn.commit()

    conn.close()


def exe_sql(file_name, sql, is_fetch=1, tmp_cursor=None):
    if tmp_cursor is None:
        conn = sqlite3.connect(file_name)
        c = conn.cursor()
    else:
        c = tmp_cursor

    c.execute(sql)
    rows = None
    if is_fetch:
        rows = c.fetchall()
    if tmp_cursor is None:
        conn.commit()
        conn.close()

    return rows


def exe_sql2(file_name, sql, sql_param, is_fetch=1, tmp_cursor=None):
    if tmp_cursor is None:
        conn = sqlite3.connect(file_name)
        c = conn.cursor()
    else:
        c = tmp_cursor
    c.execute(sql, sql_param)
    rows = None
    if is_fetch:
        rows = c.fetchall()

    if tmp_cursor is None:
        conn.commit()
        conn.close()

    return rows


def get_start_id(file_name):
    rows = exe_sql(file_name, "select max(id) from comp_list")
    start_id = rows[0][0]
    if start_id is None:
        return 0
    return start_id


def is_comp_has(file_name, uuid):
    rows = exe_sql(file_name, "select id, uuid from comp_list where uuid='" + str(uuid) + "'")
    if len(rows) > 0:
        return True, rows[0]
    return False, 0


def is_decl_has(file_name, uuid, tmp_cursor=None):
    rows = exe_sql(file_name, "select id, uuid from decl_list where uuid='" + uuid + "'", 1, tmp_cursor)
    if len(rows) > 0:
        return True, rows[0]
    return False, 0


def save_comp(file_name, id, uuid, is_smt, decl_uuid, sch_text, tags, title, updateTime, gzip_comp=0, cursor=None,
              is_update=0):
    if (type(sch_text) == type({})) and ('colors' in sch_text):
        del sch_text['colors']

    if type(sch_text) == type({}):
        sch_text = json.dumps(sch_text).replace('\'', '_')

    if is_update:
        sql_str = 'update  comp_list set uuid=?,is_smt=?, decl_uuid=?, sch=?, tags=?, title=?, updateTime=?  where id=?;'
    else:
        sql_str = 'insert into comp_list(id, uuid,is_smt, decl_uuid, sch, tags, title, updateTime ) values(?,?,?,?,?,?,?,?);'

    if is_smt is None:
        is_smt = 0
    elif is_smt == True:
        is_smt = 1
    else:
        is_smt = 0
    if is_update:
        values = [uuid, is_smt, decl_uuid, sqlite3.Binary(zlib.compress(sch_text.encode('utf-8'))), str(tags),
                  title,
                  updateTime, id]
    else:
        if gzip_comp:
            values = [id, uuid, is_smt, decl_uuid, sqlite3.Binary(zlib.compress(sch_text.encode('utf-8'))), str(tags),
                      title,
                      updateTime]
        else:
            values = [id, uuid, is_smt, decl_uuid, sch_text, str(tags), title,
                      updateTime]
    try:
        exe_sql2(file_name, sql_str, values, 0, cursor)
        print('.', end="")
    except Exception as e:
        print(e)
        print('gzip_comp:', gzip_comp)
        print('save comp error.', id, uuid)
        print('sql_str:', sql_str)
        sys.exit(0)


def save_decl(file_name, title, uuid, pkt, tmp_cursor=None):
    # uuid = pkt['uuid']
    has, rows = is_decl_has(file_name, uuid, tmp_cursor)
    if has:
        print('S', end="")
        return

    pkt_str = json.dumps(pkt)

    sql_str = 'insert into decl_list(uuid, title,  json_data) values(?,?, ?);'
    values = [uuid, title, sqlite3.Binary(zlib.compress(pkt_str.encode('utf-8')))]
    try:
        exe_sql2(file_name, sql_str, values, 0, tmp_cursor)
        print('*', end="")
    except Exception as e:
        print(e)
        print('save decl error.', id, uuid)
        print('sql_str:', sql_str)
        sys.exit(0)


def get_comp_tags(file_name_comp_gz='comp_20210612_gz.db'):
    """

    :param file_name_comp_gz:
    :return:[[id, uuid, decl_uuid, sch, tags] ]
    """
    comp_list = exe_sql(file_name_comp_gz, 'select id, uuid, decl_uuid, sch, tags from comp_list;', 1)
    for i in range(len(comp_list)):
        comp_list[i] = list(comp_list[i])
        aa = zlib.decompress(comp_list[i][3]).decode('utf-8')
        try:
            comp_list[i][3] = json.loads(aa)
        except Exception as e:
            print(e)
            print(aa)
            print('comp_id, comp_uuid', comp_list[i][0], comp_list[i][1])
            return comp_list

    return comp_list

def get_comp_uuid_list(file_name_comp_gz='comp_20210612_gz.db'):
    """
    获取文件中的comp uuid list
    :param file_name_comp_gz:
    :return:
    """
    comp_list = exe_sql(file_name_comp_gz, 'select id, uuid, decl_uuid, sch from comp_list;', 1)
    for i in range(len(comp_list)):
        comp_list[i] = list(comp_list[i])
        aa = zlib.decompress(comp_list[i][3]).decode('utf-8')
        try:
            comp_list[i][3] = json.loads(aa)
        except Exception as e:
            print(e)
            print(aa)
            print('comp_id, comp_uuid', comp_list[i][0], comp_list[i][1])
            return comp_list

    return comp_list

def get_decl_list(decl_title_list,file_name_decl_gz='decl_20210612_gz.db'):
    """

    :param decl_title_list:
    :param file_name_decl_gz:
    :return: [[id, uuid, title, json_data], ...   ]
    """
    list_str=[ '"'+i+'"' for i in decl_title_list]
    list_str='('+', '.join(list_str)+')'
    dlist = exe_sql(file_name_decl_gz, 'select id, uuid, title, json_data from decl_list where title in '+list_str,1)
    for i in range(len(dlist)):
        dlist[i]=list(dlist[i])
        dlist[i][3] = json.loads(zlib.decompress(dlist[i][3]).decode('utf-8'))
        dlist[i][3]['uuid'] = str(dlist[i][1])

    return dlist


def get_decl_uuid_list(file_name_decl_gz='decl_20210612_gz.db'):
    """
    获取文件中的comp uuid list
    :param file_name_comp_gz:
    :return:
    """
    return exe_sql(file_name_decl_gz, 'select id, uuid, from decl_list;', 1)


def get_one_comp(id, file_name_comp_gz='comp_20210612_gz.db'):
    return exe_sql(file_name_comp_gz,
                   'select id, uuid,is_smt, decl_uuid, sch, tags, title, updateTime from comp_list where id=' + str(id),
                   1)


def get_one_decl(uuid, file_name_decl_gz='decl_20210612_gz.db'):
    """

    :param uuid:
    :param file_name_decl_gz:
    :return:[0][uuid, json_data]
    """
    try:
        decl_one = exe_sql(file_name_decl_gz, 'select uuid, json_data from decl_list where uuid="' + str(uuid) + "\"",
                           1)
    except Exception as e:
        print(e)
        print('ERROR:get_one_decl. uuid=', uuid)
        sys.exit(0)
    if len(decl_one) == 0:
        print('ERROR:get_one_decl. uuid=', uuid)
        sys.exit(0)
    decl_one[0] = list(decl_one[0])
    decl_one[0][1] = json.loads(zlib.decompress(decl_one[0][1]).decode('utf-8'))
    decl_one[0][1]['uuid'] = str(decl_one[0][0])
    return decl_one[0]


def pull_and_save(comp_id, comp_uuid, file_name_comp_gz='comp_20210612_gz.db', file_name_decl_gz='decl_20210612_gz.db'):
    #update a comp
    data, time2 = lc_pull_comp_decl(comp_uuid)

    save_comp(file_name_comp_gz, comp_id, comp_uuid, data['result'].get('SMT'),
              data['result']['packageDetail']['uuid'],
              data['result']['dataStr'],
              data['result']['tags'],
              data['result']['title'],
              data['result']['updateTime'], 1, None, 1)

    save_decl(file_name_decl_gz, data['result']['packageDetail']['title'], data['result']['packageDetail']['uuid'],
              data['result']['packageDetail'])


def read_comp_decl_all():
    # 29134的封装未保存。因为提示W错误
    # 65406 未读取，因为uuid错误。改为和65405的uuid一样继续运行
    # id=1048 - uuid=11ebff3ba98c439790bae4f3913c7950 comp. 字符串里包含‘ ，导致错误。重新获取？

    file_name_comp_gz = 'comp_20210612_gz.db'
    file_name_decl_gz = 'decl_20210612_gz.db'

    # file_name = 'comp_20210612.db'
    uuid_list = get_comp_index()
    print(len(uuid_list))

    create_comp_db(file_name_comp_gz, 1, 0)
    create_comp_db(file_name_decl_gz, 0, 1)

    start_id = get_start_id(file_name_comp_gz)
    print('start_id', start_id)
    time_pull = 0
    time_save = 0
    time_req_json = [0, 0]
    for i in uuid_list:
        id = i[0]
        uuid = i[1]
        if id <= start_id:
            continue
        if id % 50 == 0:
            print('\r', id, round(time_pull, 4), round(time_save, 4), round(time_req_json[0], 4),
                  round(time_req_json[1], 4), end='')
            time_pull = 0
            time_save = 0
            time_req_json = [0, 0]

        has, rows = is_comp_has(file_name_comp_gz, uuid)
        if has:
            print('comp already has. curr id-uuid', id, uuid)
            print('new id-uuid', rows)
            continue
        t1 = time.time()
        data, time2 = lc_pull_comp_decl(i[1])
        t2 = time.time()
        save_comp(file_name_comp_gz, id, uuid, data['result'].get('SMT'),
                  data['result']['packageDetail']['uuid'],
                  data['result']['dataStr'],
                  data['result']['tags'],
                  data['result']['title'],
                  data['result']['updateTime'], 1)

        save_decl(file_name_decl_gz, data['result']['packageDetail']['title'], data['result']['packageDetail']['uuid'],
                  data['result']['packageDetail'])
        t3 = time.time()
        time_pull = time_pull + round(t2 - t1, 4)
        time_save = time_save + round(t3 - t2, 4)
        time_req_json = [time_req_json[0] + time2[0], time_req_json[1] + time2[1]]


def add_decl_title():
    # 读出数据
    # title为空的，解码，添加title
    file_name_decl_gz = 'decl_20210612_gz.db'

    decl_all = exe_sql(file_name_decl_gz, 'select id, title, json_data from decl_list;', 1)
    for i in decl_all:
        if (i[1] is None) or (len(i[1]) == 0):
            # just
            decl_json = json.loads(zlib.decompress(i[2]).decode('utf-8'))
            # print(decl_json['title'])
            decl_json['title'] = decl_json['title'].replace('"', '_')
            # print(decl_json['title'])
            print('\r', i[0], end='')
            exe_sql2(file_name_decl_gz, 'update decl_list set title=? where id=?', [decl_json['title'], i[0]], 0)


if __name__ == "__main__":
    file_name_comp_gz = 'comp_20210612_gz.db'
    file_name_decl_gz = 'decl_20210612_gz.db'
    #pull_and_save(6010,'2f87c3643dd94904b2a746820665e9ef',file_name_comp_gz, file_name_decl_gz)
    pull_and_save(29134, 'd87903658b8443e28d43f13b4c033ed1', file_name_comp_gz, file_name_decl_gz)
    sys.exit(0)
    for i in range(100):
        try:
            read_comp_decl_all()
        except Exception as e:
            print(e)
