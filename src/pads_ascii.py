# coding:utf-8

__author__ = "songjiangshan"
__copyright__ = "Copyright (C) 2021 songjiangshan \n All Rights Reserved."
__license__ = ""
__version__ = "1.0"


class PadsAscii:
    """
    pads ascii format io
    """
    def __init__(self):
        self.m_format = 'pcb_decals'
        self.m_pcb_decals = {} # pcb封装
        self.m_pad_parts = {}  # pcb parts
        self.TOP_LAYER = '1'
        self.BOTTOM_LAYER = '2'
        self.TOP_SILK_LAYER = '26'
        self.BOTTOM_SILK_LAYER = '29'

        self.TOP_PASTEM_LAYER = '23'
        self.BOTTOM_PASTEM_LAYER = '22'

        self.TOP_SOLDERM_LAYER = '21'
        self.BOTTOM_SOLDERM_LAYER = '28'

        # self.BOARDOUTLINE_LAYER=10
        # self.MULTI_LAYER=11
        # self.DOCUMENT_LAYER = 12
        # self.LEAD_SHAPE_LAYER = 100
        # self.COMP_SHAPE_LAYER = 101
        self.MOUNT_LAYER = '-2'
        self.INNER_LAYER = '-1'
        self.OPPOSITE_LAYER = '0'

    def set_format(self, format):
        """

        :param format: line_items, sch_decals, pcb_decals, part_types
        :return:
        """
        self.m_format = format

    def limit_decl_name(self, name):
        """
        decl_name max 40 char
        :param name:
        :return:
        """

        if len(name) > 40:
            name = name[0:39]
            name = name + '_'
        return name

    def limit_part_name(self, name: str):
        # *?:@,
        name = name.replace(',', '_').replace('@', '_').replace(':', '_').replace('?', '_').replace('*', '_').replace(' ', '_').replace('Ω±', '_').replace('%', '_')
        name=name.replace('±','_').replace('(','_').replace(')','_').replace('Ω', '_').replace('±', '_')
        return name

    def get_start_of_file(self):
        if self.m_format == 'line_items':
            return '*PADS-LIBRARY-LINE-ITEMS-V9*'
        elif self.m_format == 'sch_decals':
            return '*PADS-LIBRARY-SCH-DECALS-V9*'
        elif self.m_format == 'pcb_decals':
            return '*PADS-LIBRARY-PCB-DECALS-V9*'
        elif self.m_format == 'part_types':
            return '*PADS-LIBRARY-PART-TYPES-V9*'
        else:
            return 'unknown format'

    def get_eof(self):
        return '*END*'

    def add_pcb_part(self, name, decl_name, unit, dt, logfam='UND', attrs=0, gates=0, sigpins=0, pinmap=0, flag=0):
        """

        :param name:Part type name. Values can be up to 40 alphanumeric characters.
        :param decl_name:List of alternate PCB decal names, separated by colons name:name:…
                    A PCB decal name can be up to 40 alphanumeric characters. The list
                    may have a maximum of 16 alternates.
        :param unit:Coordinate units type
                    Can be either Imperial (mils) or Metric (mm), expressed as a single
                    letter: I or M
        :param logfam:Logic Family type
                        Values can be any three alphanumeric characters.
        :param attrs:Number of part attributes defined
        :param gates:Number of gates in the part
                        Values range from 0 to 702
        :param sigpins:Number of standard signals predefined in the part, which is typically,
                        but not exclusively, power and ground.
                        Values range from 0 to 1024.
        :param pinmap:Number of alphanumeric pins defined in the part pin mapping.
                        Values range from 0 to 32767.
        :param flag:Decimal value of an eight-bit binary bit string:
                        Bits 0–1 taken as a two-bit number define the type of part:
                        0 = normal part
                        1 = connector
                        2 = off-page reference.
                        Bit 2 is a flag that is set for a non-ECO registered part type.
                        Bit 5 is a flag that is set for a flip chip part ( used in advanced packaging
                        toolkit)
                        Bit 6 is a flag that is set for a die part ( used in advanced packaging
                        toolkit)
                        Bit 7 is a flag that is set to indicate an incomplete or inconsistent part
                        type.
        :return:
        """
        # name pcbdecals u logfam attrs gates sigpins pinmap flag
        # TIMESTAMP year.month.day.hour.minute.second
        if self.has_part(name):
            print('错误:part type已经存在.', name, self.m_pad_parts)
            return
        self.m_pad_parts[name] = {'name': name, 'decl_name': decl_name, 'unit': unit,
                                  'logfam': logfam, 'attrs': attrs, 'gates': gates, 'sigpins': sigpins,
                                  'pinmap': pinmap, 'flag': flag, 'dt': dt}

    def has_decl(self, decl_name):
        return decl_name in self.m_pcb_decals

    def has_part(self, part_name):
        return part_name in self.m_pad_parts

    def add_pcb_decal(self, name, unit, originx, originy, dt):
        """
        添加一个封装
        :param name:User-defined decal name. Values can be up to 40 alphanumeric characters.
        :param unit: Can be either Imperial (mils) or Metric (mm), expressed as a single letter: I or M.
        :param originx: Coordinates of the symbol origin. Expressed in mils.
        :param originy:Coordinates of the symbol origin. Expressed in mils.
        :return:
        """

        if name in self.m_pcb_decals:
            print('错误:封装已经存在.', name, self.m_pcb_decals)
            return False
        self.m_pcb_decals[name] = {'name': name, 'unit': unit,
                                   'x': originx, 'y': originy, 'attrs': {}, 'labels': [], 'terminals': {}, 'stacks': [],
                                   'pieces': [],
                                   'txt': [], 'dt': dt}
        return True

    def add_txt(self, decl_name, text, x, y, rotation, layer, height, width, mirror, fontinfo, just=0, drwnum=0,
                field=0):
        """
        向指定的封装添加文本
        :param decl_name:
        :param text:Text string
                        Up to 255 characters, spaces allowed.
        :param x: Coordinates of the text string location relative to the origin of the schematic
        :param y:
        :param rotation:Orientation of the text in degrees
        :param layer:Numeric layer number for use in PADS Layout.
                    Values range from 0 to 250. A layer value of zero means all layers. The layer
            number is ignored in PADS Logic.
        :param height:Height of text
        Values range from 0.01 to 1.0 inches, expressed in the selected units type.
        :param width:Width of text in mils. Values range from 0.001 to 0.050 inches, expressed in the selected units type.
        :param mirror:Flag indicating text mirroring in PADS Layout. 0 = not mirrored, 1 = mirrored about the y-axis when viewed with zero
        :param just:Text string justification
                Value is the decimal equivalent of a bit string as follows:
                Bits 0 to 3 encode a four-bit value for horizontal justification with the following
                values:
                0 = Left justified
                1 = Center justified
                2 = Right justified
                Bits 4 to 7 encode a four-bit value for vertical justification with the following
                values:
                0 = Bottom justified
                1 = Middle justified
                2 = Top justified.
                Allowed values for justification are as follows:
                Bottom left = 0
                Bottom center = 1
                Bottom right = 2
                Middle left = 16
                Middle center= 17
                Middle right = 18
                Top left = 32
                Top center = 33
                Top right = 34
        :param drwnum:For auto-dimensioning text, this is the PCB drawing number. For other text, the
                        value is zero.
        :param field: A flag to indicate that the text item is a PADS Logic field label.
        :param fontinfo:Font information string, as described in the Font Information Definition section.
        :return:
        """
        txt_elem = {
            'text': text, 'x': x, 'y': y, 'rotation': rotation, 'layer': layer, 'height': height, 'width': width,
            'mirror': mirror,
            'just': just, 'drwnum': drwnum, 'field': field, 'fontinfo': fontinfo

        }
        self.m_pcb_decals[decl_name]['txt'].append(txt_elem)

    def add_pcb_decal_attrib(self, name, attr_name, attr_value):
        """
        "Geometry.Height" 19499961dbunit
        :param name:
        :param attr_name:
        :param attr_value:
        :return:
        """

        if name not in self.m_pcb_decals:
            print('错误:封装不存在.', name, self.m_pcb_decals)
            return
        self.m_pcb_decals[name]['attrs'][attr_name] = attr_value

    def add_pcb_decal_attrib_label(self, decal_name, attr_name, rel_x, rel_y, rotation,
                                   mirror, height, width, layer, just, flags, fontinfo, textstring):
        """
        x y rotation mirror height width layer just flags fontinfo textstring
        :param decal_name:
        :param attr_name:
        :param rel_x:Coordinates of the text string location relative to the origin of the schematic
        :param rel_y:
        :param rotation:Orientation of the text in degrees
        :param mirror:Flag indicating text mirroring in PADS Layout.0 = not mirrored, 1 = mirrored about the y-axis when viewed with zero
orientation.
        :param height:Height of text Values range from 0.01 to 1.0 inches, expressed in the selected units type
        :param width:Width of text in mils Values range from 0.001 to 0.050 inches, expressed in the selected units type
        :param layer: Numeric layer number for use in PADS Layout.Values range from 0 to 250. A layer value of zero means all layers.
        :param just:Justification of the attribute text string
                Value is the decimal equivalent of a bit string as follows:
                Bits 0 to 3 encode a four-bit value for horizontal justification with the following
                values:
                0 = Left justified
                1 = Center justified
                2 = Right justified
                Bits 4 to 7 encode a four-bit value for vertical justification with the following
                values:
                0 = Bottom justified
                1 = Middle justified
                2 = Top justified.
                Allowed values for 0 and 90 degree rotation are as follows:
                Bottom left = 0
                Bottom center = 1
                Bottom right = 2
                Middle left = 16
                Middle center= 17
                Middle right = 18
                Top left = 32
                Top center = 33
                Top right = 34
        :param flags:Type of label, name/value visibility, and right reading status
                Values are the decimal equivalent of an eight-bit binary value with bit fields
                defined as follows:
                Bits 0 to 2 contain a numeric value to define the label type:
                0 = General attribute label
                1 = Reference designator
                2 = Part type
                Bit 3 set indicates the label is right reading and displayed at the nearest 90-degree
                orientation.
                Bit 4 set indicates label is right reading but display is not constrained to a 90-
                degree orientation.
                Bit 5 set indicates that the attribute value is displayed.
                Bit 6 set indicates that the short version of the attribute name is displayed.
                Bit 7 set indicates that the full structured attribute name is displayed.
        :param fontinfo:Font information for the attribute label text
        :param textstring: Name of the attribute whose location is being defined
                        The reserved names “REF-DES” and “PARTTYPE” refer to reference
                        designator and part type labels
                        Up to 255 characters, spaces allowed.
        :return:
        """

        self.m_pcb_decals[decal_name]['labels'].append({'x': rel_x, 'y': rel_y, 'rotation': rotation,
                                                        'mirror': mirror, 'height': height, 'width': width,
                                                        'layer': layer, 'just': just, 'flags': flags,
                                                        'fontinfo': fontinfo,
                                                        'textstring': textstring})

    def add_terminal(self, decl_name, pin_number, rx, ry, label_rx, label_ry):

        term = {'x': rx, 'y': ry, 'lx': label_rx, 'ly': label_ry, 'pin_number': pin_number}
        self.m_pcb_decals[decl_name]['terminals'][pin_number] = term
        return

    def add_pad_stack(self, decl_name, pin_number, numberlayers, layer_list, plated, drill, drlori, drllen, drloff):
        """
        :param decl_name:
        :param pin_number:Pin number to which the pad stack applies
                    If the pin number is zero, then the pad stack applies to all pins that do not have a
                    specific pad stack
        :param numberlayers:Number of pad stack layer lines that follow the header line.
        :param plated:Either the keyword P for plated drill hole or N for nonplated drill hole.
        :param drill:Drill diameter for the pad
                        Value of zero indicates that there is no drill hole
        :param drlori:Orientation of a slotted hole
                        Valid values range from 0 to 179.999 degrees.
        :param drllen:Slotted hole length
        :param drloff: Slot offset
        :param layer_list:
                    Each layer line can have one of the following formats:
                    layer width shape
                    (Round normal pad or round and square anti-pads)
                    layer width shape corner
                    (square normal pads)
                    layer width shape intd
                    (Annular pads)
                    layer width shape ori length offset
                    (Oval pads)
                    layer width shape corner ori length offset
                    (rectangular pads)
                    layer width shape ori intd spkwid numspk
                            layer Layer number
                    Valid values range from 1 to 250.
                    or
                    Layer code of the pin
                    Layer codes are defined as follows:
                    -2 is the top layer
                    -1 is all inner layers
                    -0 is the bottom layer
                    width Width of a finger pad or the external diameter of all other pad shapes

                    shape Shape can be one of the following values:
                    R—round pad
                    S—square pad
                    RA—round anti-pad
                    SA—square anti-pad
                    A—annular pad
                    OF—oval finger pad
                    RF—rectangular finger pad
                    RT—round thermal pad
                    ST—square thermal pad

                    corner This field stores the numerical “corner radius” value and is used to support pads
                    with rounded and chamfered corners. It only exists for square (S) pads and
                    rectangular finger (RF) pad shapes. Zero value is used for 90 degree (nonrounded) pad corners; a positive value is used for pads with rounded corners; a
                    negative value is used for pads with chamfered corners.

                    intd Internal diameter of an annular or thermal pad
                    ori Orientation of a finger pad or the thermal spokes
                    Valid values range from 0 to 179.999 degrees.
                    length Finger pad length
                    offset Finger pad offset
                    spkwid Thermal pad spoke width
                    numspk Number of thermal pad spokes
        :return:
        """
        # PAD pin numlayers plated drill [drlori drllen drloff]

        self.m_pcb_decals[decl_name]['stacks'].append({'pin_number': pin_number, 'numlayers': numberlayers,
                                                       'plated': plated,
                                                       'drill': drill, 'drlori': drlori,
                                                       'drllen': drllen, 'drloff': drloff, 'layer_list': layer_list})

    def add_pieces(self, decl_name, type, numcoord, width, layer, linestyle, coord_list):
        """
        type numcoord width layer linestyle
        x y (format for line segment)
        x y ab aa ax1 ay1 ax2 ay2 (format for arcs)
        :param decl_name:
        :param type:
        :param numcoord:
        :param width:
        :param layer:
        :param linestyle:
                    linestyle System flag for type of line or keepout restrictions
            A value of 1 indicates a solid line; a value of 0 indicates an old Logic
            style dotted line. Negative values indicate line styles introduced in
            PADS 9.4 (for piece types OPEN, CLOSED, CIRCLE only):
            -1 — solid
            -2 — dashed
            -3 — dotted
            -4 — dash dotted
            -5 — dash double-dotted
            Positive values indicate Keepout Restrictions (for piece types
            KPTCLS, KPTCIR only):
            Bit 0: (0x01) Placement
            Bit 1: (0x02) Trace and Copper
            Bit 2: (0x04) Copper Pour and Plane Area
            Bit 3: (0x08) Via and Jumper
            Bit 4: (0x10) Test Point
            Bit 5 : (0x20) Component Drill
            Bit 6: (0x40) Accordion
            Since TAGs have no graphics, the linestyle value for TAGs (typically
            -1) is non-significant.
        :param coord_list:
        :return:
        """

        self.m_pcb_decals[decl_name]['pieces'].append(
            {'type': type, 'numcoord': numcoord, 'width': width, 'layer': layer, 'linestyle': linestyle,
             'coord_list': coord_list})

    def contractS(self, cont_list, sps):
        return sps.join([str(i) for i in cont_list])

    def dump_part_types(self):
        """
        Each part type entry consists of the following parts:
        • Part type header lines
        • Attribute information (optional)
        • Gate information (optional)
        • Signal pin information (optional)
        • Alphanumeric pins (optional)
        :return:
        """
        #    def add_pcb_part(self, name, decl_name, unit, dt, logfam='UND', attrs=0, gates=0, sigpins=0, pinmap=0, flag=0):

        out_str = ''
        for part_name in self.m_pad_parts:
            part = self.m_pad_parts[part_name]
            out_str += self.contractS(
                [self.limit_part_name(part_name), self.limit_decl_name(part['decl_name']), part['unit'], part['logfam'],
                 part['attrs'], part['gates'], part['sigpins'],
                 part['pinmap'], part['flag'], '\n'], ' ')

            out_str += "TIMESTAMP " + self.contractS(
                [part['dt'].year, part['dt'].month, part['dt'].day, part['dt'].hour, part['dt'].minute,
                 part['dt'].second], '.') + '\n'

        return out_str

    def dump_pcb_decal(self):
        """
        A PCB decal consists of the following parts:
        • Header line
        • Decal attributes
        • Attribute label locations
        • Piece definitions
        • Text definitions
        Terminal definitions
        • Pad-stack definitions
        • Maximum layers designation
        :return:
        """
        out_str = ''

        for decl_name in self.m_pcb_decals:
            decl = self.m_pcb_decals[decl_name]
            ##############Header line
            # name u x y attrs labels pieces txt terminals stacks maxlayers
            out_str += self.contractS([self.limit_decl_name(decl['name']), decl['unit'], decl['x'], decl['y'],
                                       len(decl['attrs']), len(decl['labels']), len(decl['pieces']), len(decl['txt']),
                                       len(decl['terminals']), len(decl['stacks']), 0, '\n'], ' ')

            out_str += "TIMESTAMP " + self.contractS(
                [decl['dt'].year, decl['dt'].month, decl['dt'].day, decl['dt'].hour, decl['dt'].minute,
                 decl['dt'].second], '.') + '\n'

            ##############Decal attributes
            for i in decl['attrs']:
                out_str += '"' + i + '" ' + decl['attrs'][i] + '\n'

            ##############Attribute Labels Format
            for i in decl['labels']:
                # 0     0     0     0 1.27  0.127 1 0 34 "Regular <Romansim Stroke Font>"
                # x y rotation mirror height width layer just flags fontinfo textstring
                out_str += self.contractS(
                    [i['x'], i['y'], i['rotation'], i['mirror'], i['height'], i['width'], i['layer'], i['just'],
                     i['flags'], '\"' + i['fontinfo'] + '\"'], ' ')
                out_str += '\n'
                out_str += i['textstring'] + '\n'

            for i in decl['pieces']:
                out_str += self.contractS([i['type'], i['numcoord'], i['width'], i['layer'], i['linestyle']], ' ')
                out_str += '\n'
                for j in i['coord_list']:
                    out_str += self.contractS(j, ' ')
                    out_str += '\n'
            for i in decl['txt']:
                # x y rotation layer height width mirror just drwnum field fontinfo
                out_str += self.contractS(
                    [i['x'], i['y'], i['rotation'], i['layer'], i['height'], i['width'], i['just'],
                     i['drwnum'], i['field'], i['fontinfo']], ' ')
                out_str += '\n'
                out_str += i['text']
                out_str += '\n'

            for i in decl['terminals']:
                # Tx1 y1 x2 y2 pin
                out_str += 'T' + self.contractS(
                    [decl['terminals'][i]['x'], decl['terminals'][i]['y'], decl['terminals'][i]['lx'],
                     decl['terminals'][i]['ly'], decl['terminals'][i]['pin_number']], ' ')
                out_str += '\n'

            for i in decl['stacks']:
                # PAD pin numlayers plated drill [drlori drllen drloff]
                out_str += "PAD " + self.contractS(
                    [i['pin_number'], i['numlayers'], i['plated'], i['drill'], i['drlori'], i['drllen'], i['drloff']],
                    ' ')
                out_str += '\n'
                for j in i['layer_list']:
                    out_str += self.contractS(j, ' ') + '\n'

        return out_str

    def dump(self):
        out_str = ''
        out_str += self.get_start_of_file() + '\n'
        if self.m_format == 'pcb_decals':
            out_str += self.dump_pcb_decal()
        elif self.m_format == 'part_types':
            out_str += self.dump_part_types()

        out_str += self.get_eof() + '\n'
        return out_str

    def dump_pcb_decal_to_png(self):
        pass

