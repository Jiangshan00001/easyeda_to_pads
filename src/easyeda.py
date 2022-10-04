# coding:utf-8

# 将easyeda的字符串数字，转为dict数值，方便理解。
# 将单位从默认的10mil改为1mil
# 添加偏移，转符号等功能
#

# easyeda format parse

__author__ = "songjiangshan"
__copyright__ = "Copyright (C) 2021 songjiangshan \n All Rights Reserved."
__license__ = ""
__version__ = "1.0"

import copy
import datetime

# https://docs.easyeda.com/en/DocumentFormat/3-EasyEDA-PCB-File-Format/index.html#CIRCLE
import sys

"""
	SCH:'1',
	SCHLIB:'2',
	PCB:'3',
	PCBLIB:'4',
	PRJ:'5',
	SUBPART:'6',
	SPICESYMBOL:'7',
	SUBCKT:'8',
	WAVEFORM:'10'
"""


#之前的points都是svg代码。之前只转为了点list，现在改为svg的dict
s_pcb_cmd_list = {
    'CIRCLE': {'key_list': ['type', 'cx', 'cy', 'r', 'stroke_width', 'layer_id', 'id'],
               'key_to_mil': [0, 1, 1, 1, 1, 0, 0],
               'key_is_x': [0, 1, 0, 0, 0, 0, 0],
               'key_is_y': [0, 0, 1, 0, 0, 0, 0],
               'is_point_list': [0, 0, 0, 0, 0, 0, 0],
               },
    'TRACK': {'key_list': ['type', 'stroke_width', 'layer_id', 'net', 'points', 'id', 'locked'],
              'key_to_mil': [0, 1, 0, 0, 1, 0, 0],
              'key_is_x': [0, 0, 0, 0, 0, 0, 0],
              'key_is_y': [0, 0, 0, 0, 0, 0, 0],
              'is_point_list': [0, 0, 0, 0, 1, 0, 0]
              },
    'PAD': {'key_list': ['type', 'shape', 'cx', 'cy', 'width', 'height', 'layer_id', 'net', 'number', 'hole_radius',
                         'points', 'rotation', 'id', 'hole_length', 'hole_points', 'plated', 'locked'],
            'key_to_mil': [0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0],
            'key_is_x': [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'key_is_y': [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'is_point_list': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0],
            },
    'SOLIDREGION': {'key_list': ['type', 'layer_id', 'net', 'svg', 'sub_type', 'id', 'locked'],
                    'key_to_mil': [0, 0, 0, 0, 0, 0, 0],
                    'key_is_x': [0, 0, 0, 0, 0, 0, 0],
                    'key_is_y': [0, 0, 0, 0, 0, 0, 0],
                    'is_point_list': [0, 0, 0, 1, 0, 0, 0]
                    },
    'SVGNODE': {'key_list': ['type', 'payload'],
                'key_to_mil': [0, 0],
                'key_is_x': [0, 0],
                'key_is_y': [0, 0],
                'is_point_list': [0, 0]
                },
    'HOLE': {'key_list': ['type', 'cx', 'cy', 'radius', 'id'],  # 'diameter'
             'key_to_mil': [0, 1, 1, 1, 0],
             'key_is_x': [0, 1, 0, 0, 0],
             'key_is_y': [0, 0, 1, 0, 0],
             'is_point_list': [0, 0, 0, 0, 0],
             },
    'ARC': {
        'key_list': ['type', 'stroke_width', 'layer_id', 'net', 'svg', 'helper_dots', 'id'],
        'key_to_mil': [0, 1, 0, 0, 0, 0, 0],
        'key_is_x': [0, 0, 0, 0, 0, 0, 0],
        'key_is_y': [0, 0, 0, 0, 0, 0, 0],
        'is_point_list': [0, 0, 0, 0, 1, 0, 0, 0],
    },
    'COPPERAREA': {
        'key_list': ['type'],
        'key_to_mil': [0],
        'key_is_x': [0],
        'key_is_y': [0],
        'is_point_list': [0],
    },
    'RECT': {
        'key_list': ['type', 'x', 'y', 'width', 'height', 'layer_id', 'id', 'is_fill', 'stroke_width'],
        'key_to_mil': [0, 1, 1, 1, 1, 0, 0, 0, 1],
        'key_is_x': [0, 1, 0, 0, 0, 0, 0, 0, 0],
        'key_is_y': [0, 0, 1, 0, 0, 0, 0, 0, 0],
        'is_point_list': [0, 0, 0, 0, 0, 0, 0, 0, 0],
    },
    'TEXT': {
        'key_list': ['type', 'sub_type', 'x', 'y', 'stroke_width', 'rotation', 'mirror', 'layer_id', 'net', 'font_size',
                     'text', 'text_path', 'display', 'id'],
        'key_to_mil': [0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        'key_is_x': [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'key_is_y': [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'is_point_list': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    },
    'DIMENSION': {
        'key_list': ['type'],
        'key_to_mil': [0],
        'key_is_x': [0],
        'key_is_y': [0],
        'is_point_list': [0],
    },

    'VIA': {

        'key_list': ['type', 'cx', 'cy', 'diameter', 'net', 'hole_radius', 'id'],
        'key_to_mil': [0, 1, 1, 1, 0, 1, 0],
        'key_is_x': [0, 1, 0, 0, 0, 0, 0],
        'key_is_y': [0, 0, 1, 0, 0, 0, 0],
        'is_point_list': [0, 0, 0, 0, 0, 0, 0],
    },
    'LIB': {
        'key_list': ['type', 'cx', 'cy', 'custom', 'rotation', 'import_flag', 'id', 'locked'],
        'key_to_mil': [0, 1, 1, 0, 0, 0, 0, 0],
        'key_is_x': [0, 1, 0, 0, 0, 0, 0, 0],
        'key_is_y': [0, 0, 1, 0, 0, 0, 0, 0],
        'is_point_list': [0, 0, 0, 0, 0, 0, 0, 0],
    }

}

s_sch_cmd_list={
    'R': {'key_list': ['type', 'x', 'y', 'rx','ry','width','height' 'stroke_color','stroke_width','stroke_style','fill_color','id','locked'],
               'key_to_mil': [0, 1, 1, 1, 1, 1, 1,0,0,0,0,0,0],
               'key_is_x': [0, 1, 0, 0, 0, 0, 0],
               'key_is_y': [0, 0, 1, 0, 0, 0, 0],
               'is_point_list': [0, 0, 0, 0, 0, 0, 0],
            'name':'RECT',
               },
    'PL': {'key_list': ['type', 'points', 'stroke_color', 'stroke_width',  'stroke_style',
                       'fill_color', 'id', 'locked'],
          'key_to_mil': [0, 0, 0, 1, 0, 0, 0],
          'key_is_x': [0, 0, 0, 0, 0, 0, 0],
          'key_is_y': [0, 0, 0, 0, 0, 0, 0],
          'is_point_list': [0, 1, 0, 0, 0, 0, 0],
          'name': 'POLYLINE',
          },
    'PT': {'key_list': ['type', 'path_string', 'stroke_color', 'stroke_width', 'stroke_style',
                        'fill_color', 'id', 'locked'],
           'key_to_mil': [0, 0, 0, 1, 0, 0, 0],
           'key_is_x': [0, 0, 0, 0, 0, 0, 0],
           'key_is_y': [0, 0, 0, 0, 0, 0, 0],
           'is_point_list': [0, 1, 0, 0, 0, 0, 0],
           'name': 'PATH',
           },
    'A': {'key_list': ['type', 'path_string', 'help_dots','stroke_color', 'stroke_width', 'stroke_style',
                        'fill_color', 'id', 'locked'],
           'key_to_mil': [0, 0, 0, 0, 1, 0, 0],
           'key_is_x': [0, 0, 0, 0, 0, 0, 0],
           'key_is_y': [0, 0, 0, 0, 0, 0, 0],
           'is_point_list': [0, 1, 1, 0, 0, 0, 0],
           'name': 'ARC',
           },
    'PI': {'key_list': ['type', 'path_string', 'help_dots', 'stroke_color', 'stroke_width', 'stroke_style',
                       'fill_color', 'id', 'locked'],
          'key_to_mil': [0, 0, 0, 0, 1, 0, 0],
          'key_is_x': [0, 0, 0, 0, 0, 0, 0],
          'key_is_y': [0, 0, 0, 0, 0, 0, 0],
          'is_point_list': [0, 1, 1, 0, 0, 0, 0],
          'name': 'Pie',
          },
    'BE': {'key_list': ['type', 'rotation', 'x', 'y', 'x2', 'y2',
                         'id', 'locked'],
           'key_to_mil': [0, 0, 1, 1, 1, 1, 0],
           'key_is_x': [0, 0, 1, 0, 1, 0, 0],
           'key_is_y': [0, 0, 0, 1, 0, 1, 0],
           'is_point_list': [0, 0, 0, 0, 0, 0, 0],
           'name': 'BusEntry',
           },

    'I': {'key_list': ['type', 'x', 'y', 'width', 'height', 'rotation',
                       'href',
                        'id', 'locked'],
           'key_to_mil': [0, 1, 1, 1, 1, 0, 0],
           'key_is_x': [0, 1, 0, 0, 0, 0, 0],
           'key_is_y': [0, 0, 1, 0, 0, 0, 0],
           'is_point_list': [0, 0, 0, 0, 0, 0, 0],
           'name': 'Image',
           },
    'PG': {'key_list': ['type', 'points','stroke_color', 'stroke_width', 'stroke_style',
                       'fill_color', 'id', 'locked'],
          'key_to_mil': [0, 0,0, 1, ],
          'key_is_x': [0, 0, 0, 0],
          'key_is_y': [0, 0, 0, 0],
          'is_point_list': [0, 1, 0, 0],
          'name': 'Polygon',
          },
    'L': {'key_list': ['type', 'x','y','x2','y2', 'stroke_color', 'stroke_width', 'stroke_style',
                        'fill_color', 'id', 'locked'],
           'key_to_mil': [0, 1, 1, 1,1,0,1 ],
           'key_is_x': [0, 1, 0, 1,0],
           'key_is_y': [0, 0, 1, 0,1],
           'is_point_list': [0, 0, 0, 0],
           'name': 'Line',
           },
    'C': {'key_list': ['type', 'x', 'y', 'r',  'stroke_color', 'stroke_width', 'stroke_style',
                       'fill_color', 'id', 'locked'],
          'key_to_mil': [0, 1, 1, 1, 0, 1],
          'key_is_x': [0, 1, 0, 0, 0],
          'key_is_y': [0, 0, 1, 0, 0],
          'is_point_list': [0, 0, 0, 0],
          'name': 'Circle',
          },
    'P':{'key_list': ['type', 'display', 'electric', 'pin_number',  'x', 'y', 'rotation',
                        'id', 'locked'],
          'key_to_mil': [0, 0, 0, 0, 1, 1],
          'key_is_x':   [0, 0, 0, 0, 1,0],
          'key_is_y':   [0, 0, 0, 0, 0,1],
          'is_point_list': [0, 0, 0, 0,0,0],
          'name': 'Pin',
          },



}

def shift_val(obj, key, shift_v):
    obj[key] = round(obj[key] + shift_v, 5)
    return obj


def mirror_val(obj, key, is_mirror):
    if is_mirror:
        obj[key] = -obj[key]
    return obj


def mirror_points(points, mx, my):
    """
    svg points mirror
    """
    pts = copy.deepcopy(points)
    for index, i in enumerate(pts) :
        if 'x' in i['param']:
            i['param']['x'] = -i['param']['x'] if mx else i['param']['x']
        if 'y' in i['param']:
            i['param']['y'] = -i['param']['y'] if my else i['param']['y']

        # rx ry 只能是正的，代表长度，无需反转??
        # if 'rx' in i['param']:
        #     pass
        #     #i['param']['rx'] = -i['param']['rx'] if mx else i['param']['rx']
        # if 'ry' in i['param']:
        #     i['param']['ry'] = -i['param']['ry'] if my else i['param']['ry']
        #
        # if 'rx2' in i['param']:
        #     i['param']['rx'] = -i['param']['rx2'] if mx else i['param']['rx2']
        # if 'ry2' in i['param']:
        #     i['param']['ry2'] = -i['param']['ry2'] if my else i['param']['ry2']



        #pts.append([-i[0] if mx else i[0], -i[1] if my else i[1]])
    return pts


def is_number(val):
    try:
        a = float(val)
    except Exception as e:
        return False
    return True


def value_to_mil(val):
    # 默认单位都是10mil.转为mil
    try:
        if val == '':
            return 0.0
        ff = round(float(val) * 10.0, 5)
    except Exception as e:
        print('value_to_mil')
        print(e)
        print(val)
        sys.exit(0)
    return ff

def parse_svg_cmds(pts_str:str):
    """
    M 100 100 L 300 100 L 200 300 z
    The M indicates a moveto, the Ls indicate linetos, and the z indicates a closepath

    'M4383.6127 3101.618A9.8427 9.8427 0 0 0 4373.77 3111.4607'
    [{'cmd':'M', param:[4383.6127 3101.618]}, {'cmd':'A' 'param':[9.8427 9.8427 0 0 0 4373.77 3111.4607]}]
    """
    s_svg_cmd={
        'M':['x','y'], #Moveto
        'm': ['rx', 'ry'],
        'L':['x','y'], #LineTo
        'l': ['rx', 'ry'],
        'z':[], #close
        'Z': [],
        'A':['rx','ry','x_rotation','large_arc_flag','sweep_flag','x','y'], #Arc
        'a': ['rx', 'ry', 'x_rotation', 'large_arc_flag', 'sweep_flag', 'rx2', 'ry2']
    }

    def to_cmd(cmd, param):
        return {'cmd': cmd, 'param': dict(zip(s_svg_cmd[cmd], param))}


    cmds = []

    pts_str = pts_str.strip()
    cmd = None
    param = []
    curr_num = ''
    for i in pts_str:
        if (i in s_svg_cmd):
            # new cmd
            if cmd is not None:
                if len(curr_num) > 0:
                    param.append(curr_num)
                    curr_num = ''
                cmds.append(to_cmd(cmd, param))
                cmd = None
                param = []
            cmd = i
        elif i in '0123456789.':
            curr_num += i
        elif i in ' ,':
            if len(curr_num)>0:#FIXME:20220920  M 4115.08 3230.21 -> param:[0,4115.08]
                param.append(curr_num)
            curr_num = ''
        else:
            print('unknown svg cmd: i=', i, pts_str)


    if cmd is not None:
        if len(curr_num) > 0:
            param.append(curr_num)
            curr_num = ''
        cmds.append(to_cmd(cmd, param))
        cmd = None
        param = []

    return cmds


def point_unit_convert(pts_str):
    """
    1 1 2 2 3 4
    3个点

    M 100 100 L 300 100 L 200 300 z
    The M indicates a moveto, the Ls indicate linetos, and the z indicates a closepath
    :param pts_str:
    :return:
    """
    pts_str=pts_str.strip()
    cmds=[]
    if len(pts_str)>0 and pts_str[0] in '0123456789.':
        #just points list
        pts_list = pts_str.split(' ')
        for i in range(len(pts_list)//2):
            cmds.append({'cmd':'M', 'param':{'x':pts_list[i*2],'y':pts_list[i*2+1]}})
    else:
        cmds = parse_svg_cmds(pts_str)

    for i in cmds:
        for j in i['param']:
            if j=='x' or j=='y' or j=='rx' or j=='ry' or j=='rx2' or j=='ry2':
                i['param'][j] = value_to_mil(i['param'][j])

    return cmds


import json


class EasyEdaWrite:
    pass


class EasyEdaRead:
    def __init__(self):
        self.easy_data=None
        self.doc_type='unknown' #'SCHLIB', 'PCB' 'PCBLIB' 'SCH'
        self.package_detail=None

    def _package_shape_mirror2(self, shape, x_mirror, y_mirror):
        for tp in shape:
            if len(tp) == 0:
                break
            if 'type' not in tp:
                print('unknown type:', tp)

            if tp['type'] not in s_pcb_cmd_list:
                continue

            i = tp['type']
            keys = s_pcb_cmd_list[i]['key_list']
            for j in range(len(tp)):
                if j >= len(s_pcb_cmd_list[i]['key_list']):
                    continue
                ikey = s_pcb_cmd_list[i]['key_list'][j]
                if s_pcb_cmd_list[i]['is_point_list'][j]:
                    tp[ikey] = mirror_points(tp[ikey], x_mirror, y_mirror)
                elif s_pcb_cmd_list[i]['key_is_x'][j]:
                    tp = mirror_val(tp, ikey, x_mirror)
                elif s_pcb_cmd_list[i]['key_is_y'][j]:
                    tp = mirror_val(tp, ikey, y_mirror)

            if i == 'LIB':
                # 对于lib，镜像需要处理？？？
                tp['shape'] = self._package_shape_mirror2(tp['shape'], x_mirror, y_mirror)
                #for ishape in range(len(tp['shape'])):
                #    tp['shape'][ishape] = self._package_shape_mirror2(tp['shape'][ishape], x_mirror, y_mirror)


        return shape

    def y_mirror(self):
        if 'dataStr' not in self.easy_data:
            print('file format not known')
            return None
        self.easy_data['dataStr']['shape'] = self._package_shape_mirror2(self.easy_data['dataStr']['shape'],0, 1)
        #for i in range(len(self.easy_data['dataStr']['shape'])):
        #    self.easy_data['dataStr']['shape'][i] = self._package_shape_mirror2(self.easy_data['dataStr']['shape'][i],
        #                                                                        0, 1)

    def pin_renumber_all(self):
        for i in self.easy_data['dataStr']['shape']:
            if len(i) == 0:
                continue
            if i['type'] != 'LIB':
                continue
            i['shape'] = self.pin_renumber(i['shape'])

    def pin_renumber(self, shape):
        shape = copy.deepcopy(shape)

        # 规则：
        # 如果有3个管脚，则编号应该为1，2，3
        # 如果某个管脚已经有2，则保留
        # 每个管脚都有唯一的编号。如果2个管脚编号一样，则更换

        # 找到所有引脚号
        pnum = []
        for i in range(len(shape)):
            if shape[i]['type'] == 'PAD':
                pnum.append(shape[i]['number'])

        # 统一编号为1-N
        pnum_cnt = len(pnum)
        pnum_pads = [str(i) for i in range(1, pnum_cnt + 1)]

        for index, i in enumerate(pnum):
            if i in pnum_pads:
                if i != pnum_pads[index]:
                    # 编号正常的，保留原来编号
                    tmp = pnum_pads[index]

                    index2 = pnum_pads.index(i)
                    pnum_pads[index] = i
                    pnum_pads[index2] = tmp

        index = 0
        for i in range(len(shape)):
            if shape[i]['type'] == 'PAD':
                shape[i]['number'] = pnum_pads[index]
                index += 1
                continue

        return shape

    def _shift_shape_xy(self, shape, x, y):
        for ishape in shape:

            if 'svg' in ishape:
                for i in ishape['svg']:
                    if 'x' in i['param']:
                        i['param']['x'] -= x
                    if 'y' in i['param']:
                        i['param']['y'] -= y

            if 'points' in ishape:
                for i in ishape['points']:
                    if 'x' in i['param']:
                        i['param']['x']-=x
                    if 'y' in i['param']:
                        i['param']['y'] -= y


            # change format arc
            # if 'c' in ishape:
            #     for i in ishape['c']:
            #         i[0]-=x
            #         i[1]-=y

            if 'x' in ishape:
                ishape['x'] -= x

            if 'y' in ishape:
                ishape['y'] -= y
            if 'cx' in ishape:
                ishape['cx'] -= x

            if 'cy' in ishape:
                ishape['cy'] -= y

            if 'type' in ishape and ishape['type'] == 'LIB':
                self._shift_shape_xy(ishape['shape'], x, y)

    def _shift_xy(self, dataStr, x, y):
        if 'BBox' in dataStr:
            dataStr["BBox"]['x'] -= x
            dataStr["BBox"]['y'] -= y

        if 'shape' in dataStr:
            self._shift_shape_xy(dataStr['shape'], x, y)

        pass

    def org_to_zero(self):
        if self.doc_type =='unknown':
            return
        if 'BBox' in self.easy_data['dataStr']:
            x = self.easy_data['dataStr']['BBox']['x'] + self.easy_data['dataStr']['BBox']['width']/2
            y = self.easy_data['dataStr']['BBox']['y'] + self.easy_data['dataStr']['BBox']['height']/2
        else:
            x = 0
            y = 0

        self._shift_xy(self.easy_data['dataStr'], x, y)

        if self.package_detail is not None:
            self.package_detail.org_to_zero()


    def parse_json(self, json_data):


        if type(json_data) == type(''):
            json_data = json.loads(json_data)

        if 'result' in json_data:
            json_data = json_data['result']

        """
        	SCH:'1',
        	SCHLIB:'2',
        	PCB:'3',
        	PCBLIB:'4',
        	PRJ:'5',
        	SUBPART:'6',
        	SPICESYMBOL:'7',
        	SUBCKT:'8',
        	WAVEFORM:'10'
        """

        self.easy_data = copy.deepcopy(json_data)

        if 'docType' not in json_data:
            return None

        if json_data['docType']==2:
            #decl??
            self.doc_type='SCHLIB'
            for i in self.easy_data:
                self.easy_data[i] = self._parse_kv(i, self.easy_data[i])

            if 'packageDetail' in self.easy_data:
                self.package_detail =EasyEdaRead()
                self.package_detail.parse_json(self.easy_data['packageDetail'])


        elif json_data['docType']==3:
            #pcb
            self.doc_type='PCB'
            for i in self.easy_data:
                self.easy_data[i] = self._parse_kv(i, self.easy_data[i])

        elif json_data['docType']==4:
            #pcb
            self.doc_type='PCBLIB'
            for i in self.easy_data:
                self.easy_data[i] = self._parse_kv(i, self.easy_data[i])

        else:
            print('ERROR: unknown doc type ')


    def _parse_kv(self, key, val):
        # 此处只处理：dataStr->shape dataStr->canvas dataStr->layers dataStr->objects
        if key == 'dataStr':
            if 'shape' in val:
                val['shape'] = self._parse_shape_list(val['shape'])
            if 'canvas' in val:
                val['canvas'] = self._parse_canvas(val['canvas'])
            if 'layers' in val:
                val['layers'] = self._parse_layers_list(val['layers'])
            if 'objects' in val:
                val['objects'] = self._parse_objects_list(val['objects'])
            if 'BBox' in val:
                val['BBox'] = {'x': value_to_mil(val['BBox']['x']),
                               'y': value_to_mil(val['BBox']['y']),
                               'width': value_to_mil(val['BBox']['width']),
                               'height': value_to_mil(val['BBox']['height']),
                               }

        return val

    def _parse_shape_list(self, shape_list):
        nlist = []
        for i in shape_list:
            one = self._package_shape_str_decode(i)
            nlist.append(one)

        return nlist

    def _parse_canvas(self, canvas_str):
        pkt = canvas_str.split('~')

        if len(pkt) < 20:
            # schematic: not pcb
            return {
                'identity': pkt[0],
                'viewWidth': pkt[1],
                'viewHeight': pkt[2],
                'backGround': pkt[3],
                'gridVisible': pkt[4],
                'gridColor': pkt[5],
                'gridSize': pkt[6],
                'canvasWidth': pkt[7],
                'canvasHeight': pkt[8],
                'gridStyle': pkt[9],

                'snapSize': pkt[10],
                'unit': pkt[11],
                'altSnapSize': pkt[12],
                'originX': pkt[13],
                'originY': pkt[14],
            }
        else:
            return {
                'identity': pkt[0],
                'viewWidth': pkt[1],
                'viewHeight': pkt[2],
                'backGround': pkt[3],
                'gridVisible': pkt[4],
                'gridColor': pkt[5],
                'gridSize': pkt[6],
                'canvasWidth': pkt[7],
                'canvasHeight': pkt[8],
                'gridStyle': pkt[9],

                'snapSize': pkt[10],
                'unit': pkt[11],
                'routingWidth': pkt[12],
                'routingAngle': pkt[13],
                'copperAreaDisplay': pkt[14],
                'altSnapSize': pkt[15],
                'originX': pkt[16],
                'originY': pkt[17],
                'routeConflict': pkt[18],
                'removeLoop': pkt[19],

            }

    def _parse_layers_list(self, layers_list):
        nlist = []
        for i in layers_list:
            nlist.append(self._decode_layer(i))
        return nlist

    def _parse_objects_list(self, objects_list):
        return objects_list

    def _decode_layer(self, stri):
        """
        '1~TopLayer~#FF0000~true~false~true~'
        1.[layerid]：层的id标识
        2.[name]：层名称
        3.[color]：层颜色
        4.[visible]：层是否可见
        5.[active]：是否为当前激活层
        6.[config]：是否配置当前层
        7.[transparency]：层透明度
        8.[type]：层类型（内电层 | 信号层），内层专有配置
        :param stri:
        :return:
        """
        pkt = stri.split('~')
        return {
            'id': pkt[0],
            'name': pkt[1],
            'color': pkt[2],
            'visible': pkt[3],
            'active': pkt[4],
            'config': pkt[5],
            'type': pkt[6] if len(pkt) > 6 else 'null',
        }

    def _decode_lib_custom_str(self, stri):
        """
        'package`XH2.54-2P`BOM_Manufacturer``BOM_Manufacturer Part`2P`BOM_Supplier Part``BOM_Supplier``link``Contributor`Guest`'

        """
        ret = {}
        sp1 = stri.split("``")
        kvs = []
        for index, i in enumerate(sp1):
            if index % 2 == 0:
                kvs = i.split("`")
            else:
                kvs.append(i)
            while len(kvs) >= 2:
                ret[kvs[0]] = kvs[1]
                del kvs[1]
                del kvs[0]

        return ret

    def _package_shape_str_decode(self, stri):
        ret = {}
        if len(stri) == 0:
            return {}
        stri = stri.strip()
        pkt = stri.split('~')
        if len(pkt)==0:
            print('error. _package_shape_str_decode: no shape to decode:', stri)
            return None

        cmd_list = None
        if self.doc_type=='SCHLIB':
            if pkt[0] not in s_sch_cmd_list:
                print('_package_shape_str_decode schlib:unknown cmd:', stri)
                return {}
            cmd_list = s_sch_cmd_list
        elif self.doc_type=='PCB':
            if pkt[0] not in s_pcb_cmd_list:
                print('_package_shape_str_decode:unknown cmd:', stri)
                return {}
            cmd_list = s_pcb_cmd_list
        elif self.doc_type=='PCBLIB':
            if pkt[0] not in s_pcb_cmd_list:
                print('_package_shape_str_decode:unknown cmd:', stri)
                return {}
            cmd_list = s_pcb_cmd_list


        i = pkt[0]
        # matched
        keys = cmd_list[i]['key_list']
        decoded = dict(zip(keys, pkt))
        for j in range(len(decoded)):
            ikey = cmd_list[i]['key_list'][j]
            if len(cmd_list[i]['is_point_list'])>j and cmd_list[i]['is_point_list'][j]:
                decoded[ikey] = point_unit_convert(decoded[ikey])
            elif len(cmd_list[i]['key_to_mil'])>j and cmd_list[i]['key_to_mil'][j]:
                decoded[ikey] = value_to_mil(decoded[ikey])

        if ('type' in decoded) and decoded['type'] == 'LIB':

            # 如果是LIB，则需要添加此补充解析
            # 1-添加shape
            shape_str_list = stri.split('#@$')
            shape_str_list = shape_str_list[1:]  # 去掉第0个LIB开头的字段
            shape_list = []
            for shapei in shape_str_list:
                shape_list.append(self._package_shape_str_decode(shapei))

            decoded['shape'] = shape_list
            # 2-custom进行解析
            if 'custom' in decoded:
                decoded['custom'] = self._decode_lib_custom_str(decoded['custom'])

        return decoded
