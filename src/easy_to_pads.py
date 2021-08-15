# coding:utf-8

__author__ = "songjiangshan"
__copyright__ = "Copyright (C) 2021 songjiangshan \n All Rights Reserved."
__license__ = ""
__version__ = "1.0"

import datetime
from pads_ascii import PadsAscii


def decl_add_shape_text(dshape, easy, pads: PadsAscii):
    """

    :param dshape:
    :param easy:
    :param pads:
    :return:
    """
    package_decl_name = easy.pDetail['decl_name']
    if dshape['layer_id'] == easy.TOP_SILK_LAYER:  # 顶层丝印层
        pads.add_txt(package_decl_name, text=dshape['text'], x=dshape['x'], y=dshape['y'], rotation=dshape['rotation'],
                     layer=pads.TOP_SILK_LAYER, height=dshape['font_size'],
                     width=50 if dshape['font_size']>50 else dshape['font_size'], mirror=dshape['mirror'],
                     fontinfo="\"Regular 宋体\"")



def decl_add_shape_rect(dshape, easy, pads):
    package_decl_name = easy.pDetail['decl_name']
    if dshape['layer_id'] == easy.TOP_SILK_LAYER:  # 顶层丝印层
        pads.add_pieces(package_decl_name, type='CLOSED', numcoord=5,
                        width=dshape['stroke_width'],
                        layer=pads.TOP_SILK_LAYER, linestyle=-1, coord_list=[[dshape['x'], dshape['y']],
                                                                             [dshape['x'],
                                                                              round(dshape['y'] - dshape['height'], 5)],
                                                                             [round(dshape['x'] + dshape['width'], 5),
                                                                              round(dshape['y'] - dshape['height'], 5)],
                                                                             [round(dshape['x'] + dshape['width'], 5),
                                                                              round(dshape['y'], 5)],
                                                                             [dshape['x'], dshape['y']],
                                                                             ])


def decl_add_shape_circle(dshape, easy, pads):
    package_decl_name = easy.pDetail['decl_name']
    if dshape['layer_id'] == easy.TOP_SILK_LAYER:  # 顶层丝印层
        pads.add_pieces(package_decl_name, type='CIRCLE', numcoord=2,
                        width=dshape['stroke_width'],
                        layer=pads.TOP_SILK_LAYER, linestyle=-1,
                        coord_list=[[round(dshape['cx'] + dshape['r'], 5), dshape['cy']],
                                    [round(dshape['cx'] - dshape['r'], 5), dshape['cy']]])


def decl_add_shape_arc(dshape, easy, pads):
    package_decl_name = easy.pDetail['decl_name']
    if dshape['layer_id'] == easy.TOP_SILK_LAYER:  # 顶层丝印层
        pass
        # easy:
        # path_string --M329,274 A26.95,26.95 0 0 1 370,309
        # arc	(rx ry x-axis-rotation large-arc-flag sweep-flag x y)+
        # Draws an elliptical arc from the current point to (x, y).
        # The size and orientation of the ellipse are defined by two radii (rx, ry)
        # and an x-axis-rotation, which indicates how the ellipse as a whole is
        # rotated relative to the current coordinate system.
        # The center (cx, cy) of the ellipse is calculated automatically
        # to satisfy the constraints imposed by the other parameters.
        # large-arc-flag and sweep-flag contribute to the automatic
        # calculations and help determine how the arc is drawn.

        # pads format:
        # Start_point start_angle*10 delta_angle*10 circle_xy1, circle_xy2
        # End_point
        # OPEN   2 10 26 -1
        # -488.19 889.76 1669 -2438 -496.47 499.59 139.63 1135.69
        # -106.3 507.87
        #
        #

        # pads.add_pieces(package_decl_name, type='OPEN', numcoord=2,
        #                width=dshape['stroke_width'],
        #                layer=26, linestyle=-1, coord_list=[[round(dshape['cx'] + dshape['r'], 5), dshape['cy']],
        #                                                    [round(dshape['cx'] - dshape['r'], 5), dshape['cy']]])


def decl_add_shape_track(dshape, easy, pads):
    package_decl_name = easy.pDetail['decl_name']

    if dshape['layer_id'] == easy.TOP_SILK_LAYER:  # 顶层丝印层
        pads.add_pieces(package_decl_name, type='OPEN', numcoord=len(dshape['points']),
                        width=dshape['stroke_width'],
                        layer=26, linestyle=-1, coord_list=dshape['points'])


def decl_add_shape_pad(dshape, easy, pads):
    package_decl_name = easy.pDetail['decl_name']
    a = pads

    a.add_terminal(package_decl_name, dshape['number'], dshape['cx'], dshape['cy'], dshape['cx'], dshape['cy'])

    numberlayers = 3
    layer_list = None
    if dshape['shape'] == 'RECT':
        # rectangular finger pad
        rotation = float(dshape['rotation'])
        layer_shape = 'RF'
        wh_swap = 0
        ww = dshape['width']
        hh = dshape['height']
        if ww < hh:
            ww, hh = hh, ww
            wh_swap = 1
            rotation = rotation + 89.998
        if rotation > 180.0:
            rotation -= 180.0
        if rotation == 180.0:
            rotation = 179.998
        # layer width shape corner ori length offset
        layer_one = [-2, hh,
                     layer_shape, 0, round(rotation, 3),
                     ww, 0]
    elif dshape['shape'] == 'ELLIPSE':
        # round pad
        layer_shape = 'R'
        # layer width shape
        layer_one = [-2, dshape['height'], layer_shape]
    elif dshape['shape'] == 'OVAL':
        layer_shape = 'OF'
        rotation = float(dshape['rotation'])

        ww = dshape['width']
        hh = dshape['height']
        wh_swap = 0
        if ww < hh:
            wh_swap = 1
            ww, hh = hh, ww
            rotation = rotation + 89.998

        if rotation > 180.0:
            rotation -= 180.0
        if rotation == 180.0:
            rotation = 179.998
        # layer width shape ori length offset
        layer_one = [-2, hh, layer_shape,
                     round(rotation, 3), ww, 0]
    elif dshape['shape'] == 'POLYGON':
        # TODO: 对异形焊盘的支持??? DFN-5_L3.0-W3.0-P0.65-BL-MDV1595SU
        # print('decl_add_shape_pad:polygon not supported:', dshape['shape'])
        layer_shape = 'R'
        hh = dshape['height']
        ww = dshape['width']

        # layer width shape
        layer_one = [-2, round((ww + hh) / 20, 5), layer_shape]
        # layer width shape corner ori length offset
        # layer_one = [-2, hh, layer_shape, 0, rotation, ww, 0]
        pads.add_pieces(package_decl_name, 'COPCLS', len(dshape['points']), '10', 1, int(dshape['number']) - 1,
                        dshape['points'])
    else:
        print('decl_add_shape_pad:unknown shape', dshape['shape'])
        layer_shape = 'R'
        layer_one = [-2, dshape['height'], layer_shape, 0, 0, dshape['width'], 0]

    if easy.is_top_layer(dshape):
        # 顶层，只有一层有焊盘
        # -2 is the top layer
        # -1 is all inner layers
        # -0 is the bottom layer
        layer_list = [layer_one,
                      [-1, 0, 'R'],
                      [0, 0, 'R']]
    else:
        # 多层，多层都一样的焊盘
        layer_list = [layer_one,
                      [-1] + layer_one[1:],
                      [0] + layer_one[1:]]

    if None in layer_list:
        print('layer_list', layer_list)

    a.add_pad_stack(package_decl_name, pin_number=dshape['number'], numberlayers=numberlayers,
                    layer_list=layer_list, plated=('P' if dshape['plated'] == 'Y' else 'N'),
                    drill=2 * dshape['hole_radius'], drlori='', drllen='', drloff='')


def decl_add_shape_solidregion(dshape, easy, pads):
    package_decl_name = easy.pDetail['decl_name']

    if dshape['layer_id'] == easy.DOCUMENT_LAYER:  # 12-document 99-componentshapelayer.shape layer 100-leadshapelayer
        pads.add_pieces(package_decl_name, type='OPEN', numcoord=len(dshape['points']),
                        width=5,
                        layer=26, linestyle=-1, coord_list=dshape['points'])


def easy_to_pads(easy, part_name, part_time, pads:PadsAscii):
    package_decl_name = easy.pDetail['decl_name']
    packageDetail = easy.packageDetailRaw


    if part_name is not None:
        if not pads.has_part(part_name):
            pads.add_pcb_part(name=part_name, decl_name=package_decl_name, unit='I',
                              dt=datetime.datetime.fromtimestamp(part_time))
        else:
            print('part exist, skip', part_name)

    if pads.has_decl(package_decl_name):
        # print('decl exist. skip', package_decl_name)
        return pads

    pads.add_pcb_decal(name=easy.pDetail['decl_name'], unit='I',
                       originx=easy.pDetail['orgx'], originy=easy.pDetail['orgy'],
                       dt=easy.pDetail['updateTime'])

    pads.add_pcb_decal_attrib_label(decal_name=easy.pDetail['decl_name'], attr_name='', rel_x = 0, rel_y = 0,
                                    rotation=0, mirror=0, height=50, width=5,layer=26,
                                    just=0, flags=33, fontinfo='Regular <Romansim Stroke Font>',
                                    textstring='Comment')
    pads.add_pcb_decal_attrib_label(decal_name=easy.pDetail['decl_name'], attr_name='', rel_x = 0, rel_y = 0,
                                    rotation=0, mirror=0, height=50, width=5,layer=26,
                                    just=0, flags=34, fontinfo='Regular <Romansim Stroke Font>',
                                    textstring='REF-DES')

    for i in easy.pDetail['shape']:
        dshape = i
        if dshape['type'] == 'CIRCLE':
            decl_add_shape_circle(dshape, easy, pads)
        elif dshape['type'] == 'TRACK':
            decl_add_shape_track(dshape, easy, pads)
        elif dshape['type'] == 'PAD':
            decl_add_shape_pad(dshape, easy, pads)
        elif dshape['type'] == 'SOLIDREGION':
            decl_add_shape_solidregion(dshape, easy, pads)
        elif dshape['type'] == 'ARC':
            # TODO: ARC功能未实现
            decl_add_shape_arc(dshape, easy, pads)
        elif dshape['type'] == 'RECT':
            decl_add_shape_rect(dshape, easy, pads)
        elif dshape['type'] == 'TEXT':
            decl_add_shape_text(dshape, easy, pads)

        else:
            pass
            # print('unknown shape to pads', i)

    return pads
