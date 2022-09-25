s_control_statements = {
    'PCB': {
        'name': "*PCB*",
        'key': {
            'UNITS': {'key': ['cmd', 'value']},
            'USERGRID': {'key': ['cmd', 'value']},
            'MAXIMUMLAYER': {},
            'WORKLEVEL': {},
            'DISPLAYLEVEL': {},
            'LAYERPAIR': {},
            'VIAMODE': {},
            'LINEWIDTH': {},
            'TEXTSIZE': {},
            'JOBTIME': {},
            'DOTGRID': {},
            'SCALE': {},
            'ORIGIN': {},
            'WINDOWCENTER': {},
            'BACKUPTIME': {},
            'REAL WIDTH': {},
            'ALLSIGONOFF': {},
            'REFNAMESIZE': {},
            'HIGHLIGHT': {},
            'JOBNAME': {},
            'CONCOL': {},
            'FBGCOL': {},
            'HATCHGRID': {},
            'TEARDROP': {},
            'THERLINEWID': {},
            'PADFILLWD': {},
            'THERSMDWID': {},
            'MINHATAREA': {},
            'HATCHMODE': {},
            'HATCHDISP': {},
            'MITRETYPE': {},
            'HATCHRAD': {},
            'HATCHANG': {},
            'VIAPSPACING': {},
            'VIAPSHAPE': {},
            'VIAPTOTRACE': {},
            'VIAPFILL': {},
            'VIAPSHSIG': {},
            'VIAPSHVIA': {},
            'VIAPFLAG': {},
            'THERFLAGS': {},
            'DRLOVERSIZE': {},
            'PLANERAD': {},
            'PLANEFLAGS': {},
            'ROUTERFLAGS': {},
            'VERIFYFLAGS': {},
            'FABCHKFLAGS': {},
            'ATMAXSIZE': {},
            'ATMAXANGLE': {},
            'SLMINCOPPER': {},
            'SLMINMASK': {},
            'STMINCLEAR': {},
            'STMINSPOKES': {},
            'TPMINWIDTH': {},
            'TPMINSIZE': {},
            'SSMINGAP': {},
            'SBMINGAP': {},
            'SBLAYER': {},
            'ARPTOM': {},
            'ARPTOMLAYER': {},
            'ARDTOM': {},
            'ARDTOMLAYER': {},
            'ARDTOP': {},
            'ARDTOPLAYER': {},
            'OSNAP': {},
            'ASSOCIATEDNETNETCOUNT': {},
            'ASSOCIATEDNETPLANEPINCOUNT': {},
            'ASSOCIATEDNETPREFIX0': {},
            'ASSOCIATEDNETPREFIX1': {},
            'ASSOCIATEDNETPREFIX2': {},
            'ASSOCIATEDNETPREFIX3': {},
            'ASSOCIATEDNETPREFIX4': {},
            'TEARDROPDATA': {},

        }
    },
    'REUSE': {
        'name': "*REUSE*"
    },
    'TEXT': {
        'name': "*TEXT*"
    },

    'LINES': {
        'name': "*LINES*"
    },
    'CLUSTER': {
        'name': "*CLUSTER*",
    },
    'CONN': {
        'name': "*CONN*",
    },
    'END': {
        'name': "*END*"
    },
    'GET': {
        'name': "*GET*"
    },
    'JUMPER': {
        'name': "*JUMPER*"
    },

    'MISC': {
        'name': "*MISC*"
    },
    'NET': {
        'name': "*NET*"
    },
    'PART': {
        'name': "*PART*"
    },
    'PARTDECAL': {
        'name': "*PARTDECAL*"
    },
    'PARTTYPE': {
        'name': "*PARTTYPE*"
    },

    'GET': {
        'name': "*GET*"
    },
    'POUR': {
        'name': "*POUR*"
    },
    'REMARK': {
        'name': "*REMARK*"
    },

    'ROUTE': {
        'name': "*ROUTE*"
    },
    'SIGNAL': {
        'name': "*SIGNAL*"
    },
    'STANDARD': {
        'name': "*STANDARD*"
    },
    'TESTPOINT': {
        'name': "*TESTPOINT*"
    },
    'VIA': {
        'name': "*VIA*"
    },

}


class PadsPcbAsciiRead:
    UNIT_MILS = 1

    def __init__(self):
        self.pads_data = {}
        # self.pads_data['product']='POWERPCB'
        # self.pads_data['version']='V9.2'
        # self.pads_data['units']=''

    def _parse_general_parameter(self, line):
        pass

    def _parse_header_line(self, line):
        # header line:
        header_list = line.split('!')
        header_val = header_list[1].split('-')
        # zip
        header_key = ['product', 'version', 'units', 'mode', 'encoding']
        ret = {}
        for i in len(header_val):
            if i >= len(header_key):
                break
            ret[header_key[i]] = header_val[i]

        return ret

    def parse(self, stri: str):

        self.status = 'header'

        lines = stri.split('\n')
        if len(lines) == 0:
            return

        self.pads_data['header'] = self._parse_header_line(lines[0])

        for i in lines[1:]:
            if i == '*PCB*':
                self.status = 'PCB'
                continue
            if i == '*REUSE*':
                self.status = 'REUSE'
                continue

            if self.status == 'PCB':
                i = i.replace('\t', ' ')
                gen_param = i.split(' ')
                if gen_param[0] in s_control_statements['PCB']['key']:
                    self.pads_data['PCB'][gen_param[0]] = gen_param
                else:
                    print('ERROR:unknown param:', i)

                continue

            if self.status == 'REUSE':
                print("WARN:skip reuse", i)
                continue


class PadsPcbAsciiWrite:

    def _arc_convert_calc(self,x1,y1, x2,y2, rx, ry, x_rotation, large_arc_flag, sweep_flag):
        #https://www.w3.org/TR/SVG11/paths.html#PathElement
        # https://blog.csdn.net/fuckcdn/article/details/83937140
        # https://github.com/regebro/svg.path/blob/master/src/svg/path/path.py
        # http://svn.apache.org/repos/asf/xmlgraphics/batik/branches/svg11/sources/org/apache/batik/ext/awt/geom/ExtendedGeneralPath.java
        # x1 y1 ab aa ax1 ay1 ax2 ay2

        # x1 y1 Beginning of the arc
        # ab Beginning angle of the arc in tenths of a degree
        # aa Number of degrees in the arc in tenths of a degree
        # ax1, ay1 Lower left point of the rectangle around the circle of the arc
        # ax2, ay2 Upper right point of the rectangle around the circle of the arc
        # ax2 – ax1 = ay2 – ay1 Diameter of the circle of the arc
        # (ax1 + ax2)/2, (ay1 +ay2)/2
        # Coordinates of the center of the arc circle
        import math

        x_rotation = float(x_rotation)
        large_arc_flag = int(large_arc_flag)
        sweep_flag = int(sweep_flag)

        # Compute the half distance between the current and the final point
        cosr=math.cos(math.radians(x_rotation))
        sinr=math.sin(math.radians(x_rotation))
        dx=(x1-x2)/2
        dy=(y1-y2)/2

        # Step 1 : Compute (x1prim, y1prim)
        x1prim = cosr*dx + sinr *dy
        x1prim_sq=x1prim * x1prim
        y1prim = -sinr * dx + cosr * dy
        y1prim_sq = y1prim * y1prim
        rx_sq = rx*rx
        ry_sq = ry*ry

        #check that radii are large enough
        #correct out of range radii
        radius_scale = (x1prim_sq/rx_sq) + y1prim_sq/ry_sq
        if radius_scale>1:
            radius_scale = math.sqrt(radius_scale)
            rx *= radius_scale
            ry *= radius_scale
            rx_sq = rx*rx
            ry_sq = ry*ry
        else:
            #SVG spec only scales UP
            radius_scale = 1

        t1 = rx_sq * y1prim_sq
        t2 = ry_sq * x1prim_sq
        c = math.sqrt(abs((rx_sq * ry_sq - t1 - t2) / (t1 + t2)))

        #FIXME:here
        #sq = (rx_sq*ry_sq - rx_sq*y1prim_sq - ry_sq *x1prim_sq)/(rx_sq*y1prim_sq + ry_sq*x1prim_sq  )
        #sing_fix =
        if large_arc_flag != sweep_flag:
            c = -c
        cxprim = c * rx * y1prim / ry
        cyprim = -c * ry * x1prim / rx

        center_x = (cosr * cxprim - sinr * cyprim) + ((x1 + x2) / 2)
        center_y = (sinr * cxprim + cosr * cyprim) + ((y1 + y2) / 2)


        ux = (x1prim - cxprim) / rx
        uy = (y1prim - cyprim) / ry
        vx = (-x1prim - cxprim) / rx
        vy = (-y1prim - cyprim) / ry
        n = math.sqrt(ux * ux + uy * uy)
        p = ux
        start_angle = math.degrees(math.acos(p / n))
        if uy < 0:
            start_angle = -start_angle
        start_angle = start_angle % 360

        n = math.sqrt((ux * ux + uy * uy) * (vx * vx + vy * vy))
        p = ux * vx + uy * vy
        d = p / n
        # In certain cases the above calculation can through inaccuracies
        # become just slightly out of range, f ex -1.0000000000000002.
        if d > 1.0:
            d = 1.0
        elif d < -1.0:
            d = -1.0
        angle_extent = math.degrees(math.acos(d))

        #if (not sweep_flag ) and (angle_extent>0):
        #    angle_extent -= 360.0
        #elif sweep_flag and (angle_extent<0):
        #    angle_extent += 360.0

        if (ux * vy - uy * vx) < 0:
            angle_extent = -angle_extent
        angle_extent = angle_extent % 360
        if not sweep_flag:
            angle_extent -= 360

        angle_extent=-angle_extent
        #start_angle=-start_angle

        # angle_extent = angle_extent % 360
        # start_angle = start_angle % 360

        return [x1,y1,int(start_angle*10), int(angle_extent*10), center_x-rx, center_y-ry,  center_x+rx,center_y+ry ]


    def _float_format(self, float_val):
        if type(float_val) == type(''):
            float_val = float(float_val)
        return str(round(float_val, 5))


    def _get_piece_definition(self, piece, org):
        """
        {'type': 'TRACK', 'stroke_width': 11.811, 'layer_id': '2', 'net': 'PD1_TXD', 'points': [[2815.0999999999985, 2870.5], [2984.4000000000015, 3039.800000000003], [4259.5999999999985, 3039.800000000003]], 'id': 'gge2302344', 'locked': '0'}
        {'type': 'ARC', 'stroke_width': 11.811, 'layer_id': '3', 'net': '', 'c': [[1412.800000000003, -1865.0999999999985], [-39732.094, 30431.094], [-39738.0, 30427.0], [-39738.0, -10713.699999999997]], 'helper_dots': '', 'id': 'gge2302020'}
        {'type': 'CIRCLE', 'cx': 1681.2799999999988, 'cy': -2054.2700000000004, 'r': 5.0, 'stroke_width': 10.0, 'layer_id': '12', 'id': 'gge2300310'}
        """

        ret = ''

        if piece['type']=='TRACK':
            if org is None:
                org = piece['points'][0]

            piece_type = 'OPEN'
            # TODO: linestyle: 0 solid 1-dashed 2-dotted 3-dash dotted

            # type numcoords widthhght  linestyle level
            ret += piece_type + ' ' + str(len(piece['points'])) + ' ' + self._float_format(piece['stroke_width']) + ' 0 ' + \
                   piece['layer_id'] + '\n'
            #points：
            for j in piece['points']:
                ret += self._float_format(j['param']['x'] - org[0]) + '  ' + self._float_format(
                    j['param']['y'] - org[1]) + '\n'

        elif piece['type']=='CIRCLE':
            # type numcoords widthhght  linestyle level
            ret += self._list_to_str([ 'CIRCLE' ,2, piece['stroke_width'],0,piece['layer_id'] ])  + '\n'
            #points：
            ret += self._list_to_str([piece['cx']-org[0]-piece['r'] ,piece['cy']-org[1]])+ '\n'
            ret += self._list_to_str([piece['cx'] -org[0]+piece['r'], piece['cy'] - org[1]]) + '\n'
        elif piece['type']=='ARC':

            # type numcoords widthhght  linestyle level
            ret += self._list_to_str(['OPEN', 2, piece['stroke_width'],0, piece['layer_id'] ])+'\n'
            x1=piece['svg'][0]['param']['x']
            y1=piece['svg'][0]['param']['y']
            x2=piece['svg'][1]['param']['x']
            y2 = piece['svg'][1]['param']['y']
            rx=piece['svg'][1]['param']['rx']
            ry = piece['svg'][1]['param']['ry']
            x_rotation = piece['svg'][1]['param']['x_rotation']
            large_arc_flag = piece['svg'][1]['param']['large_arc_flag']
            sweep_flag = piece['svg'][1]['param']['sweep_flag']
            # calc arc here
            #x1 y1 ab aa ax1 ay1 ax2 ay2
            #eg: 1.27   1.778  369 1063 -1.30175 -0.508 1.55575 2.3495

            #TODO: arc convert calc
            k=self._arc_convert_calc(x1,y1, x2,y2, rx, ry, x_rotation, large_arc_flag, sweep_flag)
            k=[k[0]-org[0], k[1]-org[1], k[2],k[3],k[4]-org[0],k[5]-org[1],k[6]-org[0],k[7]-org[1]]
            #ret += self._float_format(k[0])+(' '*6) + self._float_format(k[1])+(' ' *6) + self._list_to_str(k[2:])+'\n'
            ret += self._list_to_str(                k) + '\n'
            ret += self._list_to_str([x2-org[0],y2-org[1]])+'\n'
            pass
        return ret

    def _get_text_definition(self, itext, org):
        """
        from:
        {'type': 'TEXT', 'sub_type': 'N', 'x': 43765.26, 'y': 33118.55, 'stroke_width': 6.0, 'rotation': '90', 'mirror': '0', 'layer_id': '3', 'net': '', 'font_size': 45.0, 'text': 'BAT', 'text_path': 'M 4371.9866 3311.8504 L 4376.2766 3311.8504 M 4371.9866 3311.8504 L 4371.9866 3310.0104 L 4372.1866 3309.4004 L 4372.3966 3309.2004 L 4372.8066 3308.9904 L 4373.2166 3308.9904 L 4373.6166 3309.2004 L 4373.8266 3309.4004 L 4374.0266 3310.0104 M 4374.0266 3311.8504 L 4374.0266 3310.0104 L 4374.2366 3309.4004 L 4374.4366 3309.2004 L 4374.8466 3308.9904 L 4375.4666 3308.9904 L 4375.8666 3309.2004 L 4376.0766 3309.4004 L 4376.2766 3310.0104 L 4376.2766 3311.8504 M 4371.9866 3306.0004 L 4376.2766 3307.6404 M 4371.9866 3306.0004 L 4376.2766 3304.3704 M 4374.8466 3307.0304 L 4374.8466 3304.9804 M 4371.9866 3301.5904 L 4376.2766 3301.5904 M 4371.9866 3303.0204 L 4371.9866 3300.1504', 'display': '', 'id': 'gge2302822'}
        to:
            x y ori level height width M hjust vjust
            fontstyle[:fontheight:fontdescent] fontface
            textstring

        """
        #FIXME: 此处文字字体是固定的。 文字大小是根据自己计算出来的
        font_height = itext['font_size']/10
        font_width = font_height* len(itext['text'])
        if    font_width>=50:
            font_width=49

        font_height = self._float_format(font_height)
        font_width = self._float_format(font_width)
        ret = self._float_format(itext['x']-org[0])  + ' ' + self._float_format( itext['y']-org[1]) +' ' + itext['rotation'] +' '+ itext['layer_id'] +' ' + str(font_height) +' ' + str(font_width)   + (' M ' if itext['mirror']=='0' else ' N ') +' LEFT DOWN\n'
        ret += 'Regular <Romansim Stroke Font>\n'
        ret += itext['text']+'\n'


        pass

        return ret

    def _list_to_str(self,ll):
        ret=''
        for i in ll:
            if type(i)==type(''):
                ret+= i+' '
            elif type(i)==type(1.23):
                ret += self._float_format(i)+' '
            else:
                ret += str(i) + ' '

        ret=ret.strip()
        return ret
    def _get_pin_definition(self, pad, org):
        """
        from:
        {'type': 'PAD', 'shape': 'RECT', 'cx': 43903.06, 'cy': 33020.12, 'width': 59.055, 'height': 98.425, 'layer_id': '11', 'net': 'GND', 'number': '1', 'hole_radius': 19.685, 'points': [[43853.843, 33049.647], [43853.843, 32990.592], [43952.268, 32990.592], [43952.268, 33049.647]], 'rotation': '90', 'id': 'gge2302828', 'hole_length': 0.0, 'hole_points': [], 'plated': 'Y', 'locked': '0'}
        to:
        Tx y nmx nmy pinnumber
        """
        ll = [pad['cx']-org[0], pad['cy']-org[1], pad['cx']-org[0], pad['cy']-org[1],  pad['number']]
        ret = '\nT'+self._list_to_str(ll)+'\n'

        return ret

    def _get_pad_stack_definition(self, pad, org):
        """
        from:
        {'type': 'PAD', 'shape': 'RECT', 'cx': 43903.06, 'cy': 33020.12, 'width': 59.055, 'height': 98.425, 'layer_id': '11', 'net': 'GND', 'number': '1', 'hole_radius': 19.685, 'points': [[43853.843, 33049.647], [43853.843, 32990.592], [43952.268, 32990.592], [43952.268, 33049.647]], 'rotation': '90', 'id': 'gge2302828', 'hole_length': 0.0, 'hole_points': [], 'plated': 'Y', 'locked': '0'}
        to:
        PAD pinno stacklines
        level size shape idia finori finlength finoffset [corner] [drill [plated]] [slotori slotlength slotoffset]
        level size shape idia [corner] [drill [plated]]

        """
        ret=''

        layer_list = []
        if pad['shape'] == 'RECT' or pad['shape'] == 'POLYGON':
            # rectangular finger pad
            rotation = float(pad['rotation'])
            layer_shape = 'RF'
            wh_swap = 0
            ww = pad['width']
            hh = pad['height']
            if ww < hh:
                ww, hh = hh, ww
                wh_swap = 1
                rotation = rotation + 89.998
            if rotation > 180.0:
                rotation -= 180.0
            if rotation == 180.0:
                rotation = 179.998
            # layer width shape corner ori length offset
            if 'plated' in pad:
                if pad['plated']=='Y':
                    plated = 'P'
                else:
                    plated='N'
            else:
                plated='N'


            layer_one = [-2, hh,
                         layer_shape, round(rotation, 3),
                         ww, 0,0, pad['hole_radius'], plated,rotation, pad['hole_length'],0 ]

            layer_list.append(layer_one)
            if pad['hole_radius']<0.00001:
                #没有过孔，贴片焊盘
                layer_list.append([-1, 0,
                         layer_shape, 0,
                         0, 0,0])
                layer_list.append([0, 0,
                         layer_shape, 0,
                         0, 0,0])
            else:
                layer_list.append([-1, hh,
                         layer_shape, round(rotation, 3),
                         ww, 0,0])
                layer_list.append([0, hh,
                         layer_shape, round(rotation, 3),
                         ww, 0,0])


        elif pad['shape'] == 'OVAL':
            layer_shape = 'OF'
            rotation = float(pad['rotation'])

            ww = pad['width']
            hh = pad['height']
            wh_swap = 0
            if ww < hh:
                wh_swap = 1
                ww, hh = hh, ww
                rotation = rotation + 89.998

            if rotation > 180.0:
                rotation -= 180.0
            if rotation == 180.0:
                rotation = 179.998
            # layer width shape ori length offset drill [plated]
            layer_one = [-2, hh, layer_shape,
                         round(rotation, 3), ww, 0, pad['hole_radius']*2,]

            layer_list.append(layer_one)
            if pad['hole_radius'] < 0.00001:
                # 没有过孔，贴片焊盘
                layer_list.append([-1, 0,
                                   layer_shape, 0,
                                   0, 0])
                layer_list.append([0, 0,
                                   layer_shape, 0,
                                   0, 0])
            else:
                layer_list.append([-1, hh,
                                   layer_shape, round(rotation, 3),
                                   ww, 0])
                layer_list.append([0, hh,
                                   layer_shape, round(rotation, 3),
                                   ww, 0])
        else:# pad['shape'] == 'ELLIPSE':
            if pad['shape']!='ELLIPSE':
                print('decl_add_shape_pad:unknown shape', pad['shape'])
            # round pad
            layer_shape = 'R'
            # layer width shape drillsize（drill只在mount层）
            layer_one = [-2, pad['height'], layer_shape, pad['hole_radius']*2]

            layer_list.append(layer_one)
            if pad['hole_radius'] < 0.00001:
                # 没有过孔，贴片焊盘
                layer_list.append([-1, 0,
                                   layer_shape])
                layer_list.append([0, 0,
                                   layer_shape])
            else:
                layer_list.append([-1, pad['height'], layer_shape])
                layer_list.append([0, pad['height'], layer_shape])
        #
        # elif pad['shape'] == 'POLYGON':
        #     # TODO: 对异形焊盘的支持??? DFN-5_L3.0-W3.0-P0.65-BL-MDV1595SU
        #     # print('decl_add_shape_pad:polygon not supported:', dshape['shape'])
        #     layer_shape = 'R'
        #     hh = pad['height']
        #     ww = pad['width']
        #
        #     # layer width shape
        #     layer_one = [-2, round((ww + hh) / 20, 5), layer_shape]
        #     # layer width shape corner ori length offset
        #     # layer_one = [-2, hh, layer_shape, 0, rotation, ww, 0]
        #     # pads.add_pieces(package_decl_name, 'COPCLS', len(dshape['points']), '10', 1, int(dshape['number']) - 1,
        #     #                 dshape['points'])
        # else:
        #     print('decl_add_shape_pad:unknown shape', pad['shape'])
        #     layer_shape = 'R'
        #     layer_one = [-2, pad['height'], layer_shape, 0, 0, pad['width'], 0]

        # if pad['layer_id']=='1':
        #     # 顶层，只有一层有焊盘
        #     # -2 is the top layer
        #     # -1 is all inner layers
        #     # -0 is the bottom layer
        #     layer_list = [layer_one,
        #                   [-1, 0, 'R'],
        #                   [0, 0, 'R']]
        # else:
        #     # 多层，多层都一样的焊盘
        #     layer_list = [layer_one,
        #                   [-1] + layer_one[1:],
        #                   [0] + layer_one[1:]]

        if None in layer_list:
            print('layer_list', layer_list)

        plated = ('P' if pad['plated'] == 'Y' else 'N')
        pin_number = pad['number']


        #TODO: 此处焊盘，只有Round 一种形状，应该是根据焊盘实际形状，添加其他形状
        ret='PAD ' + pad['number']+' 3\n'
        #FIXME: 焊盘尺寸形状，此处未实现
        # -2 top -1 inner ; 0--bottom
        #ret += '-2 ' + str(pad['width']) + ' R\n'
        #ret += '-1 ' + str(pad['width']) + ' R\n'
        #ret += '-0 ' + str(pad['width']) + ' R\n'
        for i in layer_list:
            ret += self._list_to_str(i)+'\n'



        return ret


    def to_partdecal(self, dataStr):
        ret = '''
        
*PARTDECAL*  ITEMS

*REMARK* NAME UNITS ORIX ORIY PIECES TERMINALS STACKS TEXT LABELS
*REMARK* PIECETYPE CORNERS WIDTHHGHT LINESTYLE LEVEL [RESTRICTIONS]
*REMARK* PIECETYPE CORNERS WIDTH LINESTYLE LEVEL [PINNUM]
*REMARK* XLOC YLOC BEGINANGLE DELTAANGLE
*REMARK* XLOC YLOC ORI LEVEL HEIGHT WIDTH MIRRORED HJUST VJUST
*REMARK* VISIBLE XLOC YLOC ORI LEVEL HEIGTH WIDTH MIRRORED HJUST VJUST RIGHTREADING
*REMARK* FONTSTYLE FONTFACE
*REMARK* T XLOC YLOC NMXLOC NMYLOC PINNUMBER
*REMARK* PAD PIN STACKLINES
*REMARK* LEVEL SIZE SHAPE IDIA [CORNERRADIUS] [DRILL [PLATED]]
*REMARK* LEVEL SIZE SHAPE FINORI FINLENGTH FINOFFSET [CORNERRADIUS] [DRILL [PLATED]]

'''
        part_decl_name_list={}

        for i in dataStr['shape']:
            if 'type' not in i:
                continue
            if i['type'] != 'LIB':
                continue


            # LIB里面是封装
            ione = i
            name = ione['custom']['package']

            if name not in part_decl_name_list:
                part_decl_name_list[name]={'name':name, 'rotation': (0 if i['rotation']=='' else i['rotation']) }
            else:
                # 如果已经存在，则直接跳过
                continue


            units = ' I '  # I--mils. M --metric/mm

            pieces = []
            terminals = []
            stacks = []
            text = []
            labels = []
            for ipie in i['shape']:
                if ipie['type'] == 'PAD':
                    terminals.append(ipie)
                elif ipie['type'] == 'TEXT':
                    # text中：L(普通) | N(器件名称) | P(器件编号) | PK(彩饰名)
                    if ipie['sub_type']=='P' or ipie['sub_type']=='N':
                        #此信息在part list中处理，此处只保留封装信息，不处理此信息
                        continue
                    text.append(ipie)
                elif (ipie['type'] == 'TRACK'  or ipie['type']=='CIRCLE' or ipie['type'] == 'ARC'  ) and\
                        (('net' not in ipie) or (ipie['net']=='')) and (int(ipie['layer_id'])<30) :
                    #TODO 封装内部添加其他类型的曲线
                    #or ipie['type'] == 'ARC' or ipie['type']=='SVGNODE' or ipie['type']=='SOLIDREGION'
                    pieces.append(ipie)
                else:
                    print('LIB:unknow shape??',ipie)

            #FIXME: 此处label是固定的2个
            #NAME UNITS ORIX ORIY PIECES TERMINALS STACKS TEXT LABELS
            head_line = '\n'+name + ' ' + units + ' 0 0 ' + str(len(pieces)) + ' ' + str(len(terminals)) + ' ' + str(
                len(terminals)) + \
                        ' ' + str(len(text)) + ' 2'+'\n'

            ret += head_line

            for ipie in pieces:
                ret += self._get_piece_definition(ipie, [i['cx'], i['cy']])

            for itext in text:
                ret +='\n'+ self._get_text_definition(itext,[i['cx'], i['cy']])


            ret +="""
VALUE           0           0   0.000  1        1.27       0.127 N   LEFT   DOWN
Regular <Romansim Stroke Font>
Ref.Des.
VALUE           0           0   0.000  1        1.27       0.127 N   LEFT     UP
Regular <Romansim Stroke Font>
Part Type
            """


            for iterminals in terminals:
                ret += self._get_pin_definition(iterminals,[i['cx'], i['cy']])

            for iterminals in terminals:
                ret += self._get_pad_stack_definition(iterminals,[i['cx'], i['cy']])

        return ret,part_decl_name_list

    def to_layer_data(self, easy):
        """
        板层定义：
        TODO: 需要添加颜色定义，否则不显示(无颜色)
        """
        if 'dataStr' not in easy.easy_data:
            return ''
        if 'layers' not in easy.easy_data['dataStr']:
            return ''

        colors_list = [
            """
COLORS :
{
ROUTE 3
VIA 1
PAD 20
COPPER 23
2DLINE 5
TEXT 5
ERROR 18
TOPCOMPONENT 18
BOTTOMCOMPONENT 6
REFDES 1
PARTTYPE 0
ATTRIBUTE 18
KEEPOUT 27
PINNUMBER 1
NETNAME 18
TOPPLACEMENT 8
BOTTOMPLACEMENT 0
}
            """,
            """
COLORS :
{
ROUTE 11
VIA 1
PAD 25
COPPER 28
2DLINE 4
TEXT 4
ERROR 18
TOPCOMPONENT 19
BOTTOMCOMPONENT 19
REFDES 27
PARTTYPE 0
ATTRIBUTE 25
KEEPOUT 27
PINNUMBER 14
NETNAME 11
TOPPLACEMENT 0
BOTTOMPLACEMENT 16
}
            """,
            """
COLORS :
{
ROUTE 0
VIA 0
PAD 0
COPPER 0
2DLINE 0
TEXT 0
ERROR 0
TOPCOMPONENT 0
BOTTOMCOMPONENT 0
REFDES 0
PARTTYPE 0
ATTRIBUTE 0
KEEPOUT 0
PINNUMBER 0
NETNAME 0
TOPPLACEMENT 0
BOTTOMPLACEMENT 0
}
            """

        ]

        ret = ''
        ret += 'LAYER DATA\n{\n'

        # LAYER 0 代表所有层-- songjiangshan
        ret += """
        LAYER 0
        {
        LAYER_THICKNESS 0
        DIELECTRIC 3.300000
        }
        """
        layer_index = 0
        for i in easy.easy_data['dataStr']['layers']:
            clayer = i
            try:
                lid = int(clayer['id'])
            except:
                # FIXME:针对层： {'id': 'Hole', 'name': 'Hole', 'color': '#222222', 'visible': 'false', 'active': 'false', 'config': 'true', 'type': ''}
                # 此层的id不是数字，忽略此层
                continue
            ret += ' LAYER ' + str(clayer['id']) + '\n{\n'
            ret += 'LAYER_NAME ' + clayer['name'] + '\n'

            # FIXME: easyeda内部没有pads此参数，此处根据名称判断添加参数
            # UNASSIGNED ROUTING ASSEMBLY SOLDER_MASK PASTE_MASK SILK_SCREEN
            if clayer['name'] in ['TopLayer', 'BottomLayer']:
                ret += 'LAYER_TYPE ROUTING\n'
                ret += 'COMPONENT Y\nROUTABLE Y\n'
                if clayer['name']=='TopLayer':
                    ret +='ASSOCIATED_SILK_SCREEN TopSilkLayer\n'
                    ret += 'ASSOCIATED_PASTE_MASK TopPasteMaskLayer\n'
                    ret += 'ASSOCIATED_SOLDER_MASK TopSolderMaskLayer\n'
                elif clayer['name']=='BottomLayer':
                    ret +='ASSOCIATED_SILK_SCREEN BottomSilkLayer\n'
                    ret += 'ASSOCIATED_PASTE_MASK BottomPasteMaskLayer\n'
                    ret += 'ASSOCIATED_SOLDER_MASK BottomSolderMaskLayer\n'

            elif clayer['name'] in ['TopSilkLayer', 'BottomSilkLayer']:
                ret += 'LAYER_TYPE SILK_SCREEN\n'
            elif clayer['name'] in ['TopPasteMaskLayer', 'BottomPasteMaskLayer']:
                ret += 'LAYER_TYPE PASTE_MASK\n'
            elif clayer['name'] in ['TopSolderMaskLayer', 'BottomSolderMaskLayer']:
                ret += 'LAYER_TYPE SOLDER_MASK\n'
            else:
                ret += 'LAYER_TYPE UNASSIGNED\n'

            ret += 'PLANE NONE\n'
            ret += 'ROUTING_DIRECTION NO_PREFERENCE\n'
            ret += 'VISIBILE Y\n'
            ret += 'ENABLED Y\n'
            ret += 'SELECTABLE Y\n'

            if layer_index < len(colors_list):
                ret += colors_list[layer_index]

            ret += '\n}\n'  # end of LAYER

        ret += '}\n'  # end of layer data

        return ret



    def _to_lines_data(self, easy):
        """
        header line
        piece entry definition
        coordinates
        optional text information
        """
        ret = """
*LINES*      LINES ITEMS

*REMARK* NAME TYPE XLOC YLOC PIECES TEXT SIGSTR
*REMARK* .REUSE. INSTANCE RSIGNAL
*REMARK* PIECETYPE CORNERS WIDTHHGHT LINESTYLE LEVEL [RESTRICTIONS]
*REMARK* XLOC YLOC BEGINANGLE DELTAANGLE
*REMARK* XLOC YLOC ORI LEVEL HEIGHT WIDTH MIRRORED HJUST VJUST

"""
        if 'dataStr' not in easy.easy_data:
            return ret
        if 'shape' not in easy.easy_data['dataStr']:
            return ret

        line_index = 0
        for i in easy.easy_data['dataStr']['shape']:
            line_index += 1
            if ('type' in i) and  (i['type'] == 'TRACK') and (len(i['net'])==0):
                # 此处只记录没有net属性的line，有net属性的，需要在route中记录
                name = 'LLLL' + str(line_index)
                linetype = 'LINES'

                firstxy=[i['points'][0]['param']['x'],i['points'][0]['param']['y']]
                ret += name + ' ' + linetype + ' ' + self._float_format(firstxy[0]) + ' ' + self._float_format(
                    firstxy[1]) + ' 1 0\n'

                ret += self._get_piece_definition(i, firstxy)


                ret += '\n'

            elif ('type' in i) and  (i['type'] == 'ARC') and (len(i['net'])==0):
                # 此处只记录没有net属性的line，有net属性的，需要在route中记录
                name = 'ARCARC' + str(line_index)
                linetype = 'LINES'

                firstxy=[i['svg'][0]['param']['x'],i['svg'][0]['param']['y']]
                ret += name + ' ' + linetype + ' ' + self._float_format(firstxy[0]) + ' ' + self._float_format(
                    firstxy[1]) + ' 1 0\n'

                ret += self._get_piece_definition(i, firstxy)


                ret += '\n'



        return ret

    def _to_pads_header(self, dataStr):
        ret = '!PADS-POWERPCB-V9.4-MILS! DESIGN DATABASE ASCII FILE 1.0' + '\n'
        # param
        ret += '*PCB*        GENERAL PARAMETERS OF THE PCB DESIGN' + '\n'
        ret += 'UNITS        0              2=Inches 1=Metric 0=Mils' + '\n'
        ret += 'LAYERPAIR    1      2       Layer pair used to route connection\n'
        return ret

    def _to_pads_reuse(self, dataStr):

        return """
        *REUSE*

        *REMARK* TYPE TYPENAME
        *REMARK* TIMESTAMP SECONDS
        *REMARK* PART NAMING PARTNAMING
        *REMARK* PART NAME
        *REMARK* NET NAMING NETNAMING
        *REMARK* NET MERGE NAME
        *REMARK* REUSE INSTANCENM PARTNAMING NETNAMING X Y ORI GLUED


                """

    def _to_pads_text(self, dataStr):
        # text
        ret = '''*TEXT*       FREE TEXT
        *REMARK* XLOC YLOC ORI LEVEL HEIGHT WIDTH MIRRORED HJUST VJUST .REUSE. INSTANCENM
        *REMARK* FONTSTYLE FONTFACE

        '''

        for i in dataStr['shape']:
            if 'type' not in i:
                continue
            if i['type']!='TEXT':
                continue

            i=i
            # 难道
            text_height = i['font_size']/100
            text_width = text_height* len(i['text'])/2
            if text_width>50:
                text_width=50
            ret +=self._list_to_str([i['x'],i['y'], i['rotation'], i['layer_id'], text_height,text_width, 'M' if i['mirror'] else 'N', 'LEFT','DOWN',0])+'\n'
            ret += self._list_to_str(['Regular','<Romansim Stroke Font>'])+'\n'
            ret += i['text']+'\n'



        return ret

    def _to_pads_cluster(self, dataStr):
        return """

        *CLUSTER*  ITEMS

        *REMARK* NAME  XLOC YLOC PARENTID CLUSTERID CHILD_NUM ATTRIBUTE ATT2 BROID

        *VIA*  ITEMS

        *REMARK* NAME  DRILL STACKLINES [DRILL START] [DRILL END]
        *REMARK* LEVEL SIZE SHAPE [INNER DIAMETER] [CORNER RADIUS]

                """

    def to_pads_via_definition(self, dataStr):
        return """

*VIA*  ITEMS

*REMARK* NAME  DRILL STACKLINES [DRILL START] [DRILL END]
*REMARK* LEVEL SIZE SHAPE [INNER DIAMETER] [CORNER RADIUS]

JMPVIA_AAAAA     0.9398 3
-2 1.397 R
-1 1.778 R
0  1.397 R

STANDARDVIA      0.9398 3
-2 1.397 R
-1 1.397 R
0  1.397 R

MICROVIA         0.35 3
-2 0.7 R
-1 0.7 R
0  0.7 R

        """

    def to_pads_jumper_definition(self, dataStr):
        return ''

    def to_pads_parttype_definition(self, dataStr):
        """

        CHOLE CHOLE UND  0   0   0     0 Y

        """


        ret="""

*PARTTYPE*   ITEMS

*REMARK* NAME DECALNM TYPE GATES SIGPINS UNUSEDPINNMS FLAGS ECO
*REMARK* G/S SWAPTYPE PINS
*REMARK* PINNUMBER SWAPTYPE.PINTYPE
*REMARK* SIGPIN PINNUMBER SIGNAME
*REMARK* PINNUMBER

"""
        part_type_name=[]
        for i in dataStr['shape']:
            if 'type' not in i:
                continue
            if i['type']!='LIB':
                continue
            if i['custom']['package'] in part_type_name:
                continue
            part_type_name.append(i['custom']['package'])
            ret +=i['custom']['package'] +' ' + i['custom']['package']  +' UND  0   0   0     0 Y\n'


        return ret

    def to_pads_partlist_definition(self, dataStr, decl_info):
        """

        eg:
            L4              LHOLE 79.64 49.56 180.000 U N 0 -1 0 -1 2
            VALUE        0.34       -0.36 180.000  1        1.27       0.127 N   LEFT   DOWN
            Regular <Romansim Stroke Font>
            Ref.Des.
            VALUE           0           0   0.000  1        1.27       0.127 N   LEFT     UP
            Regular <Romansim Stroke Font>
            Part Type

        """
        ret = """
*PART*       ITEMS

*REMARK* REFNM PTYPENM X Y ORI GLUE MIRROR ALT CLSTID CLSTATTR BROTHERID LABELS
*REMARK* .REUSE. INSTANCE RPART
*REMARK* VISIBLE XLOC YLOC ORI LEVEL HEIGTH WIDTH MIRRORED HJUST VJUST RIGHTREADING
*REMARK* FONTSTYLE FONTFACE
"""
        for i in dataStr['shape']:
            if 'type' not in i:
                continue
            if i['type']!='LIB':
                continue

            decl_name = i['custom']['package']
            #text中：L(普通) | N(器件名称) | P(器件编号) | PK(彩饰名)
            for j in i['shape']:
                if j['type']=='TEXT' and j['sub_type']=='P':
                    rotation = i['rotation']
                    if rotation =='':
                        rotation=0
                    if decl_name in  decl_info:
                        rotation = float(rotation) - float(decl_info[decl_name]['rotation'])
                    # rotation应该是0-360度之间，包括0，不包括360
                    while rotation<0:
                        rotation += 360
                    if rotation>360:
                        print('part rotation error:', rotation)
                        rotation=0

                    ret +='\n'+self._list_to_str( [j['text'], i['custom']['package'], i['cx'] , i['cy'] , rotation ,'U','N' ,'0 -1 0 -1 1'])
                    ret +='\n'
                    ret +="""
VALUE        0.34       -0.36 180.000  1        12.7       1.27 N   LEFT   DOWN
Regular <Romansim Stroke Font>
Ref.Des.

"""
                    tmp="""
VALUE           0           0   0.000  1        12.7       1.27 N   LEFT     UP
Regular <Romansim Stroke Font>
Part Type
"""


        return ret

    def to_pads_connection_definition(self, dataStr):
        """
        netlist format
        use route definition instead
        TODO: 网络名称和元件编号完全一样时，导致网表导入错误？？？
        """

        """
        ERROR: 网络名称和元件编号完全一样时，导致网表导入错误？？？
        混合网络 RIGHT R25 2 LEFT R25 2
R25.2 RIGHT.2
**CONNECTION* ascii 数据格式不正确，网络必须包含一个以上管脚。信号 RIGHT
警告:正在删除信号 RIGHT
**发现输入警告**
        """


        ret ='*NETLIST*\n'

        nets = self._collect_net_names(dataStr)

        for i in nets:
            if len(nets[i]) < 2:
                # 只有1个脚的网络无法做链接，忽略
                continue
            ret += '*SIGNAL* ' + i + '\n'
            ret += self._list_to_str([i['name'] for i in nets[i]])
            ret += '\n'

        return ret

    def _collect_net_names(self, dataStr):
        nets={}
        for i in dataStr['shape']:
            if 'type' not in i:
                continue
            if i['type']!='LIB':
                continue
            for j in i['shape']:
                if j['type']=='TEXT' and j['sub_type']=='P':
                    part_name = j['text']

                if j['type']!='PAD':
                    continue
                if len(j['net'])==0:
                    continue
                if j['net'] not in nets:
                    nets[j['net']]=[]

                net_connected = part_name+'.'+ j['number']
                if net_connected not in nets[j['net']]:
                    nets[j['net']].append({'name':part_name+'.'+ j['number'], "coord":[j['cx'], j['cy']], 'layer_id':j['layer_id']})

        return nets


    def to_pads_route_definition(self, dataStr):
        """


        FIXME: 此处调试不通过，
读取文件 --  C:\tmp\github\easyeda_to_pads\src\test_pads_ascii.asc
JMPVIA_AAAAA - 过孔的钻孔+放大值大于所有焊盘。
STANDARDVIA - 过孔的钻孔+放大值大于所有焊盘。
**ROUTE* ascii 数据行不正确
*SIGNAL* R1_1
连线并未真正与信号树绑定 C1.1 R1.1
C1.1 R1.1
连线项目编号不正确 -1
**发现输入警告**
        eg:
        *SIGNAL* GND 536870912 -2 ;
        """

        return ''

        ret = "*ROUTE*\n"
        ret += '*REMARK* *SIGNAL* SIGNAME SIGFLAG COLOR\n'
        ret += '*REMARK* REFNM.PIN .REUSE. INSTANCE RSIG REFNM.PIN .REUSE. INSTANCE RSIG\n'
        ret += '*REMARK* XLOC YLOC LAYER SEGMENTWIDTH FLAGS [ARCDIR/VIANAME] [TEARDROP [P WID LEN [FLAGS]] [N WID LEN [FLAGS]]] [JMPNM JMPFLAG] REUSE INST RSIG\n'
        ret += '\n'

        nets = self._collect_net_names(dataStr)

        for i in nets:
            if len(nets[i])<2:
                #只有1个脚的网络无法做链接，忽略
                continue
            ret += '*SIGNAL* '+i+'\n'
            for index, j in enumerate(nets[i]):
                if index==0:
                    continue
                ret += self._list_to_str([nets[i][index-1]['name'], nets[i][index]['name']])+'\n'

                ret += self._list_to_str([nets[i][index-1]['coord'][0], nets[i][index-1]['coord'][1], nets[i][index-1]['layer_id'], 4,0x700,'THERMAL'])+'\n'
                ret += self._list_to_str(
                        [nets[i][index]['coord'][0], nets[i][index]['coord'][1], nets[i][index]['layer_id'], 4, 0x700,'THERMAL'])+'\n'

            ret +='\n'

        return ret

    def to_pads_copper_pour_definition(self, dataStr):
        return ''

    def easyeda_to_pads_ascii(self, easy):
        dataStr = easy.easy_data['dataStr']
        ret = ''
        # head
        ret += self._to_pads_header(dataStr)

        ret += self._to_pads_reuse(dataStr)

        ret += self._to_pads_text(dataStr)

        ret += self._to_lines_data(easy)

        ret += self._to_pads_cluster(dataStr)

        reti, part_decl_info = self.to_partdecal(easy.easy_data['dataStr'])
        ret += reti
        
        ret += self.to_pads_via_definition(easy.easy_data['dataStr'])

        ret += self.to_pads_jumper_definition(easy.easy_data['dataStr'])
        ret += self.to_pads_parttype_definition(easy.easy_data['dataStr'])
        ret += self.to_pads_partlist_definition(easy.easy_data['dataStr'],part_decl_info)
        ret += self.to_pads_connection_definition(easy.easy_data['dataStr'])
        ret += self.to_pads_route_definition(easy.easy_data['dataStr'])
        ret += self.to_pads_copper_pour_definition(easy.easy_data['dataStr'])

        # Miscellaneous Section
        ret += """
*MISC*      MISCELLANEOUS PARAMETERS

*REMARK*    PARENT_KEYWORD PARENT_VALUE
*REMARK*  [ { 
*REMARK*       CHILD_KEYWORD CHILD_VALUE
*REMARK*     [ CHILD_KEYWORD CHILD_VALUE
*REMARK*     [ { 
*REMARK*          GRAND_CHILD_KEYWORD GRAND_CHILD_VALUE [...] 
*REMARK*       } ]] 
*REMARK*    } ] 
        """
        ret += self.to_layer_data(easy)

        return ret



class PadsLibAsciiWrite:
    pass
