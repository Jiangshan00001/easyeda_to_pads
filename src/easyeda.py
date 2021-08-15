# coding:utf-8

__author__ = "songjiangshan"
__copyright__ = "Copyright (C) 2021 songjiangshan \n All Rights Reserved."
__license__ = ""
__version__ = "1.0"

import copy
import datetime

# https://docs.easyeda.com/en/DocumentFormat/3-EasyEDA-PCB-File-Format/index.html#CIRCLE
import sys

"""
#VIA~4000.1016~2998.4616~1.1812~~0.3937~gge200~0
command: VIA
center x: 432
center y: 215
diameter: 3.2
net : ‘’
hole radius: 0.8 (8 mil)
id: gge5
locked:null
"""

s_cmd_list = {
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
    'SOLIDREGION': {'key_list': ['type', 'layer_id', 'net', 'points', 'sub_type', 'id', 'locked'],
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
        'key_list': ['type', 'stroke_width', 'layer_id', 'net', 'c', 'helper_dots', 'id'],
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

}


def shift_val(obj, key, shift_v):
    obj[key] = round(obj[key] + shift_v, 5)
    return obj


def mirror_val(obj, key, is_mirror):
    if is_mirror:
        obj[key] = -obj[key]
    return obj


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


def decode_layer(stri):
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


def point_unit_convert(pts_str):
    """
    1 1 2 2 3 4
    3个点

    M 100 100 L 300 100 L 200 300 z
    The M indicates a moveto, the Ls indicate linetos, and the z indicates a closepath
    :param pts_str:
    :return:
    """
    pts = pts_str.split(' ')
    pts2 = []
    for i in pts:
        if is_number(i):
            pts2.append(value_to_mil(i))
        elif (i.strip() == 'z') or (i.strip() == 'Z'):
            pts2.append(pts2[0])
            pts2.append(pts2[1])

    pts3 = []
    pts3_i = []
    for i in pts2:
        pts3_i.append(i)
        if len(pts3_i) == 2:
            pts3.append(pts3_i)
            pts3_i = []

    return pts3


def shift_points(points, sx, sy):
    pts = []
    for i in points:
        pts.append([round(i[0] + sx, 5), round(i[1] + sy, 5)])
    return pts


def mirror_points(points, mx, my):
    pts = []
    for i in points:
        pts.append([-i[0] if mx else i[0], -i[1] if my else i[1]])
    return pts


def package_shape_str_decode2(stri):
    if len(stri) == 0:
        return {}
    stri = stri.strip()
    for i in s_cmd_list:
        if len(stri) < len(i):
            continue
        if i != stri[0:len(i)]:
            continue

        # matched
        pkt = stri.split('~')
        keys = s_cmd_list[i]['key_list']
        decoded = dict(zip(keys, pkt))
        for j in range(len(decoded)):
            ikey = s_cmd_list[i]['key_list'][j]
            if s_cmd_list[i]['is_point_list'][j]:
                decoded[ikey] = point_unit_convert(decoded[ikey])
            elif s_cmd_list[i]['key_to_mil'][j]:
                decoded[ikey] = value_to_mil(decoded[ikey])

        return decoded

    print('unknown command:package_shape_str_decode2. ', stri)
    return {}


def package_shape_shift2(tp, sx, sy):
    for i in s_cmd_list:
        if i == tp['type']:
            keys = s_cmd_list[i]['key_list']

            for j in range(len(tp)):
                ikey = s_cmd_list[i]['key_list'][j]
                if s_cmd_list[i]['is_point_list'][j]:
                    tp[ikey] = shift_points(tp[ikey], sx, sy)
                elif s_cmd_list[i]['key_is_x'][j]:
                    tp = shift_val(tp, ikey, sx)
                elif s_cmd_list[i]['key_is_y'][j]:
                    tp = shift_val(tp, ikey, sy)

            return tp

    print('package_shape_shift2:unknown command:', tp)
    return tp


def package_shape_mirror2(tp, x_mirror, y_mirror):
    for i in s_cmd_list:
        if i == tp['type']:
            keys = s_cmd_list[i]['key_list']

            for j in range(len(tp)):
                ikey = s_cmd_list[i]['key_list'][j]
                if s_cmd_list[i]['is_point_list'][j]:
                    tp[ikey] = mirror_points(tp[ikey], x_mirror, y_mirror)
                elif s_cmd_list[i]['key_is_x'][j]:
                    tp = mirror_val(tp, ikey, x_mirror)
                elif s_cmd_list[i]['key_is_y'][j]:
                    tp = mirror_val(tp, ikey, y_mirror)

            return tp

    print('package_shape_mirror2:unknown command:', tp)
    return tp


class EasyEda():
    """
    0: "1~TopLayer~#FF0000~true~true~true~"
    1: "2~BottomLayer~#0000FF~true~false~true~"
    2: "3~TopSilkLayer~#FFCC00~true~false~true~"
    3: "4~BottomSilkLayer~#66CC33~true~false~true~"
    4: "5~TopPasteMaskLayer~#808080~true~false~true~"
    5: "6~BottomPasteMaskLayer~#800000~true~false~true~"
    6: "7~TopSolderMaskLayer~#800080~true~false~true~0.3"
    7: "8~BottomSolderMaskLayer~#AA00FF~true~false~true~0.3"
    8: "9~Ratlines~#6464FF~true~false~true~"
    9: "10~BoardOutLine~#FF00FF~true~false~true~"
    10: "11~Multi-Layer~#FFFFFF~true~false~true~0.5"
    11: "12~Document~#FFFFFF~true~false~true~"
    12: "13~TopAssembly~#33CC99~true~false~true~"
    13: "14~BottomAssembly~#5555FF~true~false~true~"
    14: "15~Mechanical~#F022F0~true~false~true~"
    15: "19~3DModel~#66CCFF~true~false~true~"
    16: "21~Inner1~#800000~false~false~false~~"
    17: "22~Inner2~#008000~false~false~false~~"
    18: "23~Inner3~#00FF00~false~false~false~~"
    19: "24~Inner4~#BC8E00~false~false~false~~"
    20: "25~Inner5~#70DBFA~false~false~false~~"
    21: "26~Inner6~#00CC66~false~false~false~~"
    22: "27~Inner7~#9966FF~false~false~false~~"
    23: "28~Inner8~#800080~false~false~false~~"
    24: "29~Inner9~#008080~false~false~false~~"
    25: "30~Inner10~#15935F~false~false~false~~"
    26: "31~Inner11~#000080~false~false~false~~"
    27: "32~Inner12~#00B400~false~false~false~~"
    28: "33~Inner13~#2E4756~false~false~false~~"
    29: "34~Inner14~#99842F~false~false~false~~"
    30: "35~Inner15~#FFFFAA~false~false~false~~"
    31: "36~Inner16~#99842F~false~false~false~~"
    32: "37~Inner17~#2E4756~false~false~false~~"
    33: "38~Inner18~#3535FF~false~false~false~~"
    34: "39~Inner19~#8000BC~false~false~false~~"
    35: "40~Inner20~#43AE5F~false~false~false~~"
    36: "41~Inner21~#C3ECCE~false~false~false~~"
    37: "42~Inner22~#728978~false~false~false~~"
    38: "43~Inner23~#39503F~false~false~false~~"
    39: "44~Inner24~#0C715D~false~false~false~~"
    40: "45~Inner25~#5A8A80~false~false~false~~"
    41: "46~Inner26~#2B937E~false~false~false~~"
    42: "47~Inner27~#23999D~false~false~false~~"
    43: "48~Inner28~#45B4E3~false~false~false~~"
    44: "49~Inner29~#215DA1~false~false~false~~"
    45: "50~Inner30~#4564D7~false~false~false~~"
    46: "51~Inner31~#6969E9~false~false~false~~"
    47: "52~Inner32~#9069E9~false~false~false~~"
    48: "99~ComponentShapeLayer~#00CCCC~true~false~true~0.4"
    49: "100~LeadShapeLayer~#CC9999~true~false~true~"
    50: "101~ComponentPolarityLayer~#66FFCC~true~false~true~"
    51: "Hole~Hole~#222222~false~false~true~"
    52: "DRCError~DRCError~#FAD609~false~false~true~"
    """

    def __init__(self):
        self.pDetail = {}
        self.packageDetailRaw = None
        self.hole_to_pad_index = 0
        self.TOP_LAYER = '1'
        self.BOTTOM_LAYER = '2'
        self.TOP_SILK_LAYER = '3'
        self.BOTTOM_SILK_LAYER = '4'

        self.TOP_PASTEM_LAYER = '5'
        self.BOTTOM_PASTEM_LAYER = '6'

        self.TOP_SOLDERM_LAYER = '7'
        self.BOTTOM_SOLDERM_LAYER = '8'

        self.BOARDOUTLINE_LAYER = '10'
        self.MULTI_LAYER = '11'
        self.DOCUMENT_LAYER = '12'
        self.LEAD_SHAPE_LAYER = '100'
        self.COMP_SHAPE_LAYER = '101'

    def parse_decl_json(self, packageDetail):
        self.packageDetailRaw = copy.deepcopy(packageDetail)
        self.pDetail['decl_name'] = self.packageDetailRaw['dataStr']['head']['c_para']['package']
        self.pDetail['orgx'] = value_to_mil(self.packageDetailRaw['dataStr']['head']['x'])
        self.pDetail['orgy'] = value_to_mil(self.packageDetailRaw['dataStr']['head']['y'])
        self.pDetail['updateTime'] = datetime.datetime.fromtimestamp(self.packageDetailRaw['updateTime'])
        layers = self.packageDetailRaw['dataStr']['layers']
        # 解码layer定义
        self.pDetail['layers'] = {decode_layer(i)['id']: decode_layer(i) for i in layers}
        shape = packageDetail['dataStr']['shape']
        # 解码数据
        self.pDetail['shape'] = [package_shape_str_decode2(i) for i in shape]

    def is_top_layer(self, shape):
        if shape.get('layer_id'):
            if shape.get('layer_id') == '1':
                return True
        return False

    def hole_to_pad(self):
        for i in range(len(self.pDetail['shape'])):
            if self.pDetail['shape'][i]['type'] == 'HOLE':
                # hole->pad
                self.pDetail['shape'][i]['type'] = 'PAD'
                self.pDetail['shape'][i]['shape'] = 'ELLIPSE'
                self.pDetail['shape'][i]['width'] = self.pDetail['shape'][i]['radius'] * 2
                self.pDetail['shape'][i]['height'] = self.pDetail['shape'][i]['radius'] * 2
                self.pDetail['shape'][i]['hole_radius'] = self.pDetail['shape'][i]['radius']
                self.pDetail['shape'][i]['plated'] = 'N'
                self.pDetail['shape'][i]['number'] = 'HOLEN' + str(self.hole_to_pad_index)
                self.hole_to_pad_index += 1

    def shift_xy(self, shape_index, sx, sy):
        p = self.pDetail['shape'][shape_index]
        self.pDetail['shape'][shape_index] = \
            package_shape_shift2(p, -self.pDetail['orgx'], -self.pDetail['orgy'])

    def org_to_zero(self):
        for i in range(len(self.pDetail['shape'])):
            self.shift_xy(i, -self.pDetail['orgx'], -self.pDetail['orgy'])

        self.pDetail['orgx'] = 0.0
        self.pDetail['orgy'] = 0.0

    def y_mirror(self):
        for i in range(len(self.pDetail['shape'])):
            self.pDetail['shape'][i] = package_shape_mirror2(self.pDetail['shape'][i], 0, 1)

    def pin_renumber(self):

        # 找到所有引脚号
        pnum = []
        for i in range(len(self.pDetail['shape'])):
            if self.pDetail['shape'][i]['type'] == 'PAD':
                pnum.append(self.pDetail['shape'][i]['number'])

        # 统一编号为1-N
        pnum_cnt = len(pnum)
        pnum_pads = [str(i) for i in range(1, pnum_cnt + 1)]

        for i in range(len(self.pDetail['shape'])):
            if self.pDetail['shape'][i]['type'] == 'PAD':
                if self.pDetail['shape'][i]['number'] in pnum_pads:
                    pnum_pads.remove(self.pDetail['shape'][i]['number'])
                    pnum_pads.append(self.pDetail['shape'][i]['number'])
                    continue

        for i in range(len(self.pDetail['shape'])):
            if self.pDetail['shape'][i]['type'] == 'PAD':
                if self.pDetail['shape'][i]['number'] in pnum_pads:
                    pnum_pads.remove(self.pDetail['shape'][i]['number'])
                    continue
                else:
                    # print(self.pDetail['decl_name'], 'decl has pin number not supported by pads')
                    # print('renumber:', self.pDetail['shape'][i]['number'], 'to:', pnum_pads[0])
                    self.pDetail['shape'][i]['number'] = pnum_pads[0]
                    pnum_pads.pop(0)
                    continue

    def pin_resort(self):
        self.pDetail['shape'].sort(key=shape_cmp)


def shape_cmp(one_shape):
    ret = one_shape['type']
    if ret == 'PAD':
        ret += one_shape['number'].zfill(5)

    return ret

######################
# dep 下面是废弃的函数
#
# def package_shape_str_decode(stri):
#     if len(stri)==0:
#         return {}
#     cmd_list={'CIRCLE':decode_circle,
#               'PAD':decode_pad,
#               'TRACK':decode_track,
#               'SOLIDREGION':decode_solidregion,
#               'SVGNODE':decode_svnnode,
#               'HOLE':decode_hole,
#               }
#     for i in cmd_list:
#         if len(stri)<len(i):
#             continue
#         if i==stri[0:len(i)]:
#             return cmd_list[i](stri)
#
#     print('unknown command:', stri)
#     return ''
#
#
# def package_shape_shift(tp, sx, sy):
#     cmd_list = {'CIRCLE': shift_circle,
#                 'PAD': shift_pad,
#                 'TRACK': shift_track,
#                 'SOLIDREGION': shift_solidregion,
#                 'SVGNODE': shift_svnnode,
#                 'HOLE': shift_hole,
#                 }
#     for i in cmd_list:
#         if i == tp['type']:
#             return cmd_list[i](tp, sx, sy)
#
#     print('unknown command:', tp)
#     return tp
#
# def package_shape_mirror(tp, x_mirror, y_mirror):
#     cmd_list = {'CIRCLE': mirror_circle,
#                 'PAD': mirror_pad,
#                 'TRACK': mirror_track,
#                 'SOLIDREGION': mirror_solidregion,
#                 'SVGNODE': mirror_svnnode,
#                 'HOLE':mirror_hole,
#                 }
#     for i in cmd_list:
#         if i == tp['type']:
#             return cmd_list[i](tp, x_mirror, y_mirror)
#
#     print('unknown command:', tp)
#     return tp
#
# def decode_circle(stri):
#     """
#     "CIRCLE~363~273~42~1~3~gge33"
#     'CIRCLE~4000~3000~0.984~1.9685~100~gge100~0~~'
#     :param stri:
#     :return:
#     """
#     pkt = stri.split('~')
#     return {
#         'type':pkt[0],
#         'cx':value_to_mil(pkt[1]),
#         'cy': value_to_mil(pkt[2]),
#         'r': value_to_mil(pkt[3]),
#         'stroke_width': value_to_mil(pkt[4]),
#         'layer_id': pkt[5],
#         'id': pkt[6]
#     }
#
# def shift_circle(circle, sx, sy):
#     shift_val(circle, 'cx', sx)
#     shift_val(circle, 'cy', sy)
#     return circle
#
# def mirror_circle(circle, mx, my):
#     mirror_val(circle, 'cx', mx)
#     mirror_val(circle, 'cy', my)
#
#     return circle
#
#
# def shift_points(points, sx, sy):
#     pts=[]
#     for i in points:
#         pts.append([round(i[0]+sx,5 ), round(i[1]+sy, 5)])
#
#     return pts
#
# def mirror_points(points, mx, my):
#     pts = []
#     for i in points:
#         pts.append([-i[0] if mx else i[0], -i[1] if my else i[1]])
#
#     return pts
#
#
# def decode_track(stri):
#     """
#     "TRACK~1~1~S$8~311 175 351 175 352 174~gge18"
#     'TRACK~1~3~~4098.4254 2997.9213 4098.4254 3047.6378~gge260~0'
#     :param stri:
#     :return:
#     """
#
#     pkt = stri.split('~')
#     return {
#         'type': pkt[0],
#         'stroke_width': value_to_mil(pkt[1]),
#         'layer_id': pkt[2],
#         'net': pkt[3],
#         'points': point_unit_convert(pkt[4]),
#         'id': pkt[5],
#         'locked': pkt[6],
#     }
# def shift_track(track, sx, sy):
#     track['points']=shift_points(track['points'], sx, sy)
#     return track
#
# def mirror_track(track, mx, my):
#     track['points'] = mirror_points(track['points'], mx, my)
#     return track
#
#
# def decode_pad(stri):
#     """
#     "PAD~OVAL~814~371~6~16~11~~1~1.8~814 366 814 376~0~gge5~11~814 374.7 814 367.3~N"
#     'PAD~RECT~4000~3000~7.874~7.874~11~~1~2.3622~3996.063 2996.063 4003.937 2996.063 4003.937 3003.937 3996.063 3003.937~0~gge8~0~~Y~0~~0.1969~4000,3000'
#
#     command: PAD
#     shape: ELLIPSE/RECT/OVAL/POLYGON-圆形，矩形，长圆形，多边形
#     center x: 814
#     center y: 371
#     width: 6 (60 mil)
#     height: 16 (160 mil)
#     layer id: 11 (All)
#     net: ‘’
#     number: 1
#     hole radius: 1.8 (18 mil)
#     points: ‘’ (ELLIPSE = ‘’, RECT = outline points)
#     rotation: 0 [0 - 360]
#     id: gge19
#     Hole(Length): 11 (110mil)
#     Hole Points: 814 374.7 814 367.3 // slot hole from to point
#     Plated:Y/N
#     locked:null
#     :param stri:
#     :return:
#     """
#     pkt = stri.split('~')
#     return {
#         'type': pkt[0],
#         'shape': pkt[1],
#         'cx': value_to_mil(pkt[2]),
#         'cy': value_to_mil(pkt[3]),
#         'width': value_to_mil(pkt[4]),
#         'height': value_to_mil(pkt[5]),
#         'layer_id': pkt[6],
#         'net': pkt[7],
#         'number': pkt[8],
#         'hole_radius': value_to_mil(pkt[9]),
#         'points': point_unit_convert(pkt[10]),
#         'rotation': pkt[11],
#         'id': pkt[12],
#         'hole_length': value_to_mil(pkt[13]),
#         'hole_points': pkt[14],
#         'plated': pkt[15],
#         'locked': pkt[16],
#     }
#
# def shift_pad(pad_json, sx, sy):
#     pad_json['cx']=round(pad_json['cx']+sx, 5)
#     pad_json['cy'] = round(pad_json['cy'] + sy, 5)
#     #TODO: points shift
#     pad_json['points'] = shift_points(pad_json['points'], sx, sy)
#     return pad_json
#
# def mirror_pad(pad_json, mx, my):
#     if mx:
#         pad_json['cx'] = -pad_json['cx']
#     if my:
#         pad_json['cy'] = -pad_json['cy']
#     # TODO: points mirror
#     pad_json['points'] = mirror_points(pad_json['points'], mx, my)
#     return pad_json
#
#
# def decode_solidregion(stri):
#     #"SOLIDREGION~1~GND~322 256 376 317 447 250 353 231~solid~gge34"
#     #SOLIDREGION~99~~M 3997.4409 3005.7087 L 3997.4409 2994.2913 L 4002.5591 2994.2913 L 4002.5591 3005.7087 Z ~solid~gge999~~~~0
#     pkt = stri.split('~')
#     return {
#         'type': pkt[0],
#         'layer_id': pkt[1],
#         'net': pkt[2],
#         'points':point_unit_convert(pkt[3]),
#         'sub_type': pkt[4],# solid/cutout/npth
#         'id': pkt[5],
#         'locked': pkt[6],
#     }
#
# def shift_solidregion(solid, sx, sy):
#     solid['points'] = shift_points(solid['points'], sx, sy)
#     return solid
# def mirror_solidregion(solid, mx, my):
#     solid['points'] = mirror_points(solid['points'], mx, my)
#     return solid
#
#
# def decode_svnnode(stri):
#     pkt = stri.split('~')
#     return {
#         'type': pkt[0],
#         'payload': pkt[1],
#     }
#
# def shift_svnnode(svnn, sx, sy):
#     return svnn
# def mirror_svnnode(svnn, mx, my):
#     return svnn
#
# def decode_hole(stri):
#     """
#     HOLE~4001.878~2986.374~1.1811~gge107~0
#     "HOLE~284~255~4~gge5"
#         command: HOLE
#         center x: 284
#         center y: 255
#         diameter: 4
#         id: gge5
#         locked:null
#     :param stri:
#     :return:
#     """
#     pkt = stri.split('~')
#     return {
#         'type': pkt[0],
#         'cx': value_to_mil(pkt[1]),
#         'cy': value_to_mil(pkt[2]),
#         'diameter': value_to_mil(pkt[3]),
#         'id': pkt[4],
#     }
#
#
#
# def shift_hole(obj, sx, sy):
#     shift_val(obj, 'cx', sx)
#     shift_val(obj, 'cy', sy)
#     return obj
# def mirror_hole(obj, mx, my):
#     mirror_val(obj, 'cx', mx)
#     mirror_val(obj, 'cy', my)
#     return obj
#
