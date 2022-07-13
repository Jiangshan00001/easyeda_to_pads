# coding:utf-8

__author__ = "songjiangshan"
__copyright__ = "Copyright (C) 2021 songjiangshan \n All Rights Reserved."
__license__ = ""
__version__ = "1.0"

import sys
import time
import codecs

import requests  # 导入requests包
import json
from pads_ascii import PadsAscii
from easyeda import EasyEda
from szlc_read import get_comp_uuid_list, get_one_decl
from easy_to_pads import easy_to_pads
import datetime
from line_profiler import LineProfiler


def lc_get_comp_decl(comp_uuid):
    url = 'https://lceda.cn/api/components?version=6.4.20.2&docType=2&uid=0819f05c4eef4c71ace90d822a990e87&type=3'
    url2 = 'https://lceda.cn/api/components/' + comp_uuid + '?version=6.4.20.2&uuid=' + comp_uuid + '&datastrid='
    strhtml = requests.get(url2)  # Get方式获取网页数据
    comp_list_ret = json.loads(strhtml.text)
    packageDetail = comp_list_ret['result']['packageDetail']
    return packageDetail, comp_list_ret['result']['dataStr']['head']


def lc_search(user_id, keyword):
    """

    :param user_id:
    :param keyword:
    :return:
    """
    url = 'https://lceda.cn/api/components/search'
    param = {'type': 3, 'doctype[]': 2, 'uid': user_id, 'returnListStyle': 'classifyarr', 'wd': keyword,
             'version': '6.4.20.2'}
    ret = requests.post(url, param)
    ret_j = json.loads(ret.text)
    if ret_j['success'] is not True:
        print('some error:', ret_j['message'])
        return None, None
    pkt_uuid = ret_j['result']['lists']['lcsc'][0]['uuid']
    pkt_title = ret_j['result']['lists']['lcsc'][0]['title']
    return pkt_uuid, pkt_title


def etopads(ddetail_json: dict, partdetail_json: dict, a: PadsAscii):
    """

    :param ddetail_json:
    :param a:
    :return:
    """

    easy = EasyEda()
    t1 = time.time()
    packageDetail = ddetail_json
    easy.parse_decl_json(packageDetail)
    easy.org_to_zero()
    easy.y_mirror()
    easy.hole_to_pad()
    easy.pin_renumber()
    easy.pin_resort()
    t2 = time.time()

    package_decl_name = easy.pDetail['decl_name']
    if partdetail_json is not None:
        part_name = partdetail_json['c_para']['name']
        part_time = partdetail_json.get('utime')
        if (part_time == '') or (part_time is None):
            part_time = time.time()
    else:
        part_time = 0
        part_name = None
    part_time = int(part_time)
    a = easy_to_pads(easy, part_name, part_time, a)

    t3 = time.time()
    return a, [t2 - t1, t3 - t2]


def save_to_file(stri, file_name):
    f = open(file_name, 'w+')
    f.write(json.dumps(stri, indent=4))
    f.close()


def pull_one_comp():
    a = PadsAscii()

    user_id = '0819f05c4eef4c71ace90d822a990e87'
    keywords = ['SMA-TH_SMA-KWE903', 'ANT-SMD_KH-IPEX-K501-29', 'MICRO-SIM-SMD_SIM-002-A6',
                'LCC-LGA-58_L17.7-W15.8-P1.1-TL-BC260Y-CN']  # , ]#, , 'SOT-23-3_L2.9-W1.3-P1.90-LS2.4-BR']
    for kw in keywords:
        puuid, ptitle = lc_search(user_id, kw)
        # puuid = '5ec5c544aad7443f95c394098550fb07'
        ddetail, partdetail = lc_get_comp_decl(puuid)
        a = etopads(ddetail, partdetail, a)

    f = open('out.d', 'w+')
    a.set_format('pcb_decals')
    f.write(a.dump())
    f.close()

    f = open('out.p', 'w+')
    a.set_format('part_types')
    f.write(a.dump())
    f.close()


from szlc_read import get_decl_list


def szlc_to_pads_decl_list(decl_title_list):
    """
    通过封装名称的列表，导出封装
    :param title_list:
    :return:
    """

    a = PadsAscii()

    cnt = 0
    decl_list = get_decl_list(decl_title_list)

    for i in decl_list:
        t1 = time.time()
        t2 = time.time()
        a, time_list = etopads(i[3], None, a)
        print('\r', cnt, end='')

        cnt += 1

    f = open('out.d', 'w+')
    a.set_format('pcb_decals')
    f.write(a.dump())
    f.close()

    f = open('out.p', 'w+')
    a.set_format('part_types')
    f.write(a.dump())
    f.close()


def szlc_to_pads_2k():
    """
    函数主要时间在通过uuid查询decl_json_data. 需要创建索引来加快速度
    :return:
    """
    a = PadsAscii()

    cnt = 0
    comp_list = get_comp_uuid_list()

    t_read = 0
    t_easy = 0
    t_pads = 0
    for i in comp_list:
        t1 = time.time()
        decl_data = get_one_decl(i[2])
        t2 = time.time()
        a, time_list = etopads(decl_data[1], i[3]['head'], a)
        t_read += t2 - t1
        t_easy += time_list[0]
        t_pads += time_list[1]
        print('\r', cnt, t_read, t_easy, t_pads, end='')
        if cnt % 2000 == 0:
            print('\r', t2 - t1, time_list, cnt, len(comp_list), end='')
            if cnt > 0:
                break
        cnt += 1

    f = open('out.d', 'w+')
    a.set_format('pcb_decals')
    f.write(a.dump())
    f.close()

    f = open('out.p', 'w+')
    a.set_format('part_types')
    f.write(a.dump())
    f.close()


from szlc_read import get_comp_tags

def comp_save_by_tags():
    # 按照分类导出各类数据到指定文件
    # 7637 里面的某个值，有问题
    comp_list = get_comp_tags()
    tag_list=list(set([ i[4] for i in comp_list]))
    tag_list.sort()
    print(tag_list)


    #tag_list = tag_list[0:10]
    #tag_list = tag_list[10:20]
    #tag_list = tag_list[20:30]
    #tag_list = tag_list[30:50]
    #tag_list = tag_list[50:70]
    #tag_list = tag_list[70:90]
    #tag_list = tag_list[90:110]
    #tag_list = tag_list[110:150]
    #tag_list = tag_list[150:200]
    #tag_list = tag_list[200:300]
    tag_list = tag_list[300:]

    tags_pads = {}
    cnt = 0
    for i in comp_list:
        curr_tag = i[4]
        comp_uuid = i[1]
        decl_uuid = i[2]
        sch = i[3]
        if curr_tag not in tag_list:
            continue


        print('\r', i[0], end='')
        if curr_tag not in tags_pads:
            tags_pads[curr_tag] = PadsAscii()
        decl_data = get_one_decl(decl_uuid)
        tags_pads[curr_tag], time_list = etopads(decl_data[1], sch['head'], tags_pads[curr_tag])
        cnt += 1


    print('to pads ready.')
    cnt = 0
    for tag_title in tags_pads:
        tag_title_file_name = tag_title.encode('gbk', 'ignore').decode('gbk', 'ignore').replace('[', '').replace(']', '').replace('"', '').replace('/', '_').replace(
            ' ', '_').replace(',', '_').replace('\\uff0c', '_').replace('\\uff08', '').replace('\\uff09', '').replace('\\u4f5c', '').replace('\\u5e9f', '')
        f = open('./lc_pads/'+tag_title_file_name + '.d', 'wb+')
        tags_pads[tag_title].set_format('pcb_decals')
        f.write(tags_pads[tag_title].dump().encode('gbk', 'ignore'))
        f.close()

        f = open('./lc_pads/'+tag_title_file_name + '.p', 'wb+')
        tags_pads[tag_title].set_format('part_types')
        f.write(tags_pads[tag_title].dump().encode('gbk', 'ignore'))
        f.close()
        print('\r', cnt, end='')
        cnt += 1


if __name__ == '__main__':

    # szlc_to_pads_decl_list(['SMA-SMD_BWSMA-KE-P001', 'IND-SMD_L3.6-W2.9', 'SOT-363_L2.0-W1.3-P0.65-LS2.1-TL', 'SOT-23-3_L2.9-W1.3-P1.90-LS2.4-BR'])
    szlc_to_pads_decl_list(['CAP-SMD_L7.3-W4.3-R-RD'])
    sys.exit(0)

    comp_save_by_tags()
    sys.exit(0)

    lp = LineProfiler()

    lp_wrapper = lp(comp_save_by_tags)
    lp_wrapper()
    lp.print_stats()

    sys.exit(0)

    lp = LineProfiler()
    lp.add_function(get_comp_uuid_list)  # add additional function to profile
    lp.add_function(get_one_decl)
    lp_wrapper = lp(szlc_to_pads_2k)
    lp_wrapper()
    lp.print_stats()

