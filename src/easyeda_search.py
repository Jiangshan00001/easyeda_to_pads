import os.path

import requests
import json

def read_cfg():
    f = open('cfg.json', 'r')
    cfg = f.read()
    f.close()
    cfg = json.loads(cfg)
    return cfg

def write_cfg(dat):
    f = open('cfg.json', 'w')
    f.write(json.dumps(dat))
    f.close()

def sort_comp(ls, decal_name):

    # 按照 ls[0]['title'] ls[0]['owner']['username']=='lcsc'
    #按照是否lcsc的封装进行排序
    ls_lcsc=[]
    ls_other = []
    for i in ls:
        if i['owner']['username'].upper()=='LCSC':
            ls_lcsc.append(i)
        else:
            ls_other.append(i)

    ls_match = []
    ls_not_match=[]
    # 按照是否完全一致进行排序
    for i in ls_lcsc:
        if i['title'].upper()==decal_name.upper():
            ls_match.append(i)
    for i in ls_other:
        if i['title'].upper() == decal_name.upper():
            ls_match.append(i)

    if len(ls_match)>0:
        return ls_match

    # 没有完全一致的，找内部包含的
    for i in ls_lcsc:
        if decal_name.upper() in i['title'].upper() :
            ls_match.append(i)
    for i in ls_other:
        if decal_name.upper() in i['title'].upper():
            ls_match.append(i)

    if len(ls_match) > 0:
        return ls_match

    # 没有包含的，则直接按照默认排序

    ls_lcsc.extend(ls_other)
    return ls_lcsc


def szlc_read_comp_search(wd,uid, type=3,doctype=2, returnListStyle='classifyarr',
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

    ls = sort_comp(ls, wd)
    return ls

def lc_get_comp_decl(comp_uuid,version):
    url2 = 'https://lceda.cn/api/components/' + comp_uuid + '?version='+version+ '&uuid=' + comp_uuid + '&datastrid='
    strhtml = requests.get(url2)  # Get方式获取网页数据
    comp_list_ret = json.loads(strhtml.text)
    #comp_body = comp_list_ret['result']
    return comp_list_ret

def get_decal_data(decal_name):
    try:
        curr_dir = os.path.dirname(__file__)
        curr_dir = os.path.join(curr_dir, 'tmp/')
        if not os.path.exists(curr_dir):
            os.mkdir(curr_dir)

        file_name = os.path.join(curr_dir, decal_name+'.tmp')
        if os.path.exists(file_name ):
            f=open(file_name,'r')
            stri=f.read()
            f.close()
            return stri


        cfg = read_cfg()
        uid = cfg['uid']
        version = cfg['version']
        ls = szlc_read_comp_search(decal_name, uid,version=version)
        comp_uuid = ls[0]['uuid']
        comp = lc_get_comp_decl(comp_uuid, version)

        f = open(file_name,'w')
        f.write(json.dumps(comp,indent=4))
        f.close()

        return comp
    except Exception as e:
        return None